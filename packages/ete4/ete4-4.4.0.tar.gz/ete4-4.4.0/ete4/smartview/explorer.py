#!/usr/bin/env python3

"""
Web server to explore trees interactively.

The main endpoints are for the static files to serve the frontend
(that uses javascript), and for exposing an api to manipulate the
trees in the backend.
"""

import sys
import os
import re
import json
import gzip, bz2, zipfile, tarfile
import socket
import webbrowser
from threading import Thread
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter as fmt

import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

from cheroot.wsgi import Server  # our multithreaded wsgi server

import brotli

from bottle import (
    get, post, put, delete, redirect, static_file,
    request, response, error, abort, HTTPError, default_app)

DIR_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(DIR_BIN))  # so we can import ete w/o install

from ete4 import Tree, newick, nexus, operations as ops, treematcher as tm
from ete4.core.eval import eval_on_node
from ete4.smartview import draw
from ete4.smartview.layout import Layout, BASIC_LAYOUT, update_style

DIR_LIB = os.path.dirname(os.path.abspath(draw.__file__))


# Make sure we send the errors as json too.
@error(400)
@error(404)
def json_error(error):
    response.content_type = 'application/json'
    return json.dumps({'message': error.body})


def req_json():
    """Return what request.json would return, but gracefully aborting."""
    try:
        return json.loads(request.body.read())
    except json.JSONDecodeError as e:
        abort(400, f'bad json content: {e}')


def nice_html(content, title='Tree Explorer'):
    """Return the content as part of a nice-looking html page."""
    return f"""
<!DOCTYPE html>
<html><head><title>{title}</title>
<link rel="icon" type="image/png" href="/static/images/icon.png">
<link rel="stylesheet" href="/static/upload.css"></head>
<body><div class="centered">{content}</div></body></html>"""


# Routes.

@get('/')
def callback():
    if g_trees:
        if len(g_trees) == 1:
            name = list(g_trees.keys())[0]
            redirect(f'/static/gui.html?tree={name}')
        else:
            trees = '\n'.join('<li><a href="/static/gui.html?tree='
                              f'{name}">{name}</li>' for name in g_trees)
            return nice_html(f'<h1>Loaded Trees</h1><ul>\n{trees}\n</ul>')
    else:
        return nice_html("""<h1>Tree Explorer</h1>
<p>No trees loaded.</p>
<p>See the <a href="/help">help page</a> for more information.</p>""")

@get('/help')
def callback():
    return nice_html("""<h1>Help</h1>
You can go to the <a href="/static/upload.html">upload page</a>, see
a <a href="/">list of loaded trees</a>, or
<a href="https://etetoolkit.org/">consult the documentation</a>.""")

@get('/static/<path:path>')
def callback(path):
    return static_file(path, f'{DIR_LIB}/static')


@get('/api')
def callback():
    """Get all the available api endpoints and their documentation."""
    exclude = {"/", "/help", "/static/<path:path>"}  # excluded endpoints
    return {r.rule: r.callback.__doc__
            for r in default_app().routes if r.rule not in exclude}


@get('/trees')
def callback():
    """Get information about all the loaded trees."""
    response.content_type = 'application/json'
    return json.dumps([name for name in g_trees])

@get('/trees/<tree_id>/size')
def callback(tree_id):
    """Get tree size as {'width': w, 'height': h}."""
    width, height = load_tree(tree_id).size
    return {'width': width, 'height': height}

@get('/trees/<tree_id>/nodecount')
def callback(tree_id):
    """Get the total number of nodes and leaves of the given tree."""
    t = load_tree(tree_id)
    return {'nnodes': sum(1 for node in t.traverse()),
            'nleaves': sum(1 for node in t.leaves())}

@get('/trees/<tree_id>/properties')
def callback(tree_id):
    """Get a list of the available properties for the tree."""
    t = load_tree(tree_id)
    props = set()
    for node in t.traverse():
        props |= node.props.keys()

    response.content_type = 'application/json'
    return json.dumps(list(props))

@get('/trees/<tree_id>/layouts')
def callback(tree_id):
    """Get the layout names and default options, available for the tree."""
    name, _ = get_tid(tree_id)  # "name" or "tid" is what identifies the tree
    layouts = g_layouts.get(name, [])  # layouts available for the tree
    return {layout.name: {'active': layout.active} for layout in layouts}

@get('/trees/<tree_id>/style')
def callback(tree_id):
    """Get the style of the tree according to all the active layouts."""
    try:
        args = request.query  # shortcut
        assert list(args.keys()) == ['active'], 'missing list of active layouts'

        active = set(json.loads(args['active']))

        t = load_tree(tree_id)

        name, _ = get_tid(tree_id)  # "name" or "tid" is what identifies the tree

        # Get the style of the tree according to all the layouts.
        style = {}
        for layout in g_layouts.get(name, []):
            if layout.name in active:
                for element in layout.draw_tree(t):
                    if type(element) is dict:  # a style element
                        update_style(style, element)
        # Here we care only for the styles. For tree faces see draw.py

        # Susbstitute aliases for their corresponding styles.
        aliasable_keys = {'box', 'dot', 'hz-line', 'vt-line', 'collapsed'}
        for k, v in style.items():
            if type(v) is str and k in aliasable_keys:
                aliases = set(style.get('aliases', {}).keys())
                assert v in aliases, f'unknown style "{v}" among {aliases}'
                style[k] = style['aliases'][v]
        # NOTE: The principal use of "aliases" is for the styles coming out of
        # calling draw_node() in the layouts. This is just an extra.

        # We remove is-leaf-fn because it is a function (thus not serializable).
        style.pop('is-leaf-fn', None)

        # We keep other parts like "aliases" if they are in the style, even if
        # the gui will not do anything with them.

        return style
    except (ValueError, AssertionError) as e:
        abort(400, str(e))

@get('/trees/<tree_id>/draw')
def callback(tree_id):
    """Get all the drawing commands to represent the tree."""
    try:
        kwargs = get_drawing_kwargs(tree_id, request.query)

        graphics = json.dumps(list(draw.draw(**kwargs))).encode('utf8')

        response.content_type = 'application/json'
        if g_config['compress']:
            response.add_header('Content-Encoding', 'br')
            return brotli.compress(graphics)
        else:
            return graphics
    except (AssertionError, SyntaxError) as e:
        abort(400, f'when drawing: {e}')

@get('/trees/<tree_id>/search')
def callback(tree_id):
    """Store a search, saving matching nodes so they can be later drawn."""
    nresults, nparents = store_search(tree_id, request.query)
    return {'message': 'ok', 'nresults': nresults, 'nparents': nparents}

@get('/trees/<tree_id>/newick')
def callback(tree_id):
    """Get the newick string that represents the tree."""
    MAX_MB = 2
    response.content_type = 'application/json'
    return json.dumps(get_newick(tree_id, MAX_MB))

@put('/trees/<tree_id>/clear_searches')
def callback(tree_id):
    """Remove all saved searches."""
    g_searches.clear()
    return {'message': 'ok'}

@put('/trees/<tree_id>/sort')
def callback(tree_id):
    """Sort the nodes in the tree according to the criteria in the request."""
    node_id, key_text, reverse = req_json()
    try:
        sort(tree_id, node_id, key_text, reverse)
        return {'message': 'ok'}
    except Exception as e:
        abort(400, f'evaluating expression: {e}')

@put('/trees/<tree_id>/set_outgroup')
def callback(tree_id):
    """Set the requested node as an outgroup in the tree."""
    tid, subtree = get_tid(tree_id)
    if subtree:
        abort(400, 'operation not allowed with subtree')
    node_id = req_json()
    t = load_tree(tid)
    try:
        ops.set_outgroup(t[node_id])
        ops.update_sizes_all(t)
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot root at {node_id}: {e}')

@put('/trees/<tree_id>/move')
def callback(tree_id):
    """Move the requested node up/down within its siblings."""
    try:
        t = load_tree(tree_id)
        node_id, shift = req_json()
        ops.move(t[node_id], shift)
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot move {node_id}: {e}')

@put('/trees/<tree_id>/remove')
def callback(tree_id):
    """Remove the requested node (including descendants) from the tree."""
    try:
        t = load_tree(tree_id)
        node_id = req_json()
        ops.remove(t[node_id])
        ops.update_sizes_all(t)
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot remove {node_id}: {e}')

@put('/trees/<tree_id>/rename')
def callback(tree_id):
    """Change name of the requested node in the tree."""
    try:
        t = load_tree(tree_id)
        node_id, name = req_json()
        t[node_id].name = name
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot rename {node_id}: {e}')

@put('/trees/<tree_id>/edit')
def callback(tree_id):
    """Edit content (with newick notation) of the requested node in the tree."""
    try:
        t = load_tree(tree_id)
        node_id, content = req_json()
        node = t[node_id]
        node.props = newick.read_props(content+';', pos=0, is_leaf=True,
                                       parser=newick.PARSER_DEFAULT)[0]
        ops.update_sizes_all(t)
        return {'message': 'ok'}
    except (AssertionError, newick.NewickError) as e:
        abort(400, f'cannot edit {node_id}: {e}')

@put('/trees/<tree_id>/to_dendrogram')
def callback(tree_id):
    """Convert tree to dendrogram (remove all branch distances)."""
    node_id = req_json()
    t = load_tree(tree_id)
    ops.to_dendrogram(t[node_id])
    ops.update_sizes_all(t)
    return {'message': 'ok'}

@put('/trees/<tree_id>/to_ultrametric')
def callback(tree_id):
    """Convert tree to ultrametric (all leaves ending at the same distance)."""
    try:
        node_id = req_json()
        t = load_tree(tree_id)
        ops.to_ultrametric(t[node_id])
        ops.update_sizes_all(t)
        return {'message': 'ok'}
    except AssertionError as e:
        abort(400, f'cannot convert to ultrametric {tree_id}: {e}')

@post('/trees')
def callback():
    """Add a new tree."""
    ids = add_trees_from_request()
    response.status = 201
    return {'message': 'ok', 'ids': ids}

@delete('/trees/<tree_id>')
def callback(tree_id):
    """Remove a tree."""
    try:
        remove_tree(tree_id)
        return {'message': 'ok'}
    except KeyError as e:
        abort(404, f'unknown tree {tree_id}')


# Logic.

# Global variables.
g_trees = {}  # 'name' -> Tree
g_config = {'compress': False}  # global configuration
g_layouts = {None: []}  # 'name' -> [available layouts] (None for preloaded)
g_searches = {}  # 'searched_text' -> ({result nodes}, {parent nodes})
g_threads = {}  # {'server': (thread, server)}

def load_tree(tree_id):
    """Add tree to g_trees and initialize it if not there, and return it."""
    try:
        tid, subtree = get_tid(tree_id)
        return g_trees[tid][subtree]
    except (KeyError, IndexError):
        abort(404, f'unknown tree id {tree_id}')


def get_tid(tree_id):
    """Return the tree id and the subtree id, with the appropriate types."""
    # Example: 'my_tree,1,0,1,1' -> ('my_tree', [1, 0, 1, 1])
    try:
        tid, *subtree = tree_id.split(',')
        return tid, [int(n) for n in subtree]
    except ValueError:
        abort(404, f'invalid tree id {tree_id}')


def get_newick(tree_id, max_mb):
    """Return the newick representation of the given tree."""
    t = load_tree(tree_id)

    nw = newick.dumps(t)

    size_mb = len(nw) / 1e6
    if size_mb > max_mb:
        abort(400, 'newick too big (%.3g MB)' % size_mb)

    return nw


def sort(tree_id, node_id, key_text, reverse):
    """Sort the (sub)tree corresponding to tree_id and node_id."""
    t = load_tree(tree_id)

    key = get_eval_search(key_text)

    ops.sort(t[node_id], key, reverse)


# Drawing arguments.

def get_drawing_kwargs(tree_id, args):
    """Return the drawing arguments initialized as specified in the args."""
    valid_keys = ['x', 'y', 'w', 'h', 'zx', 'zy', 'za',
                  'layouts', 'labels', 'collapsed_shape', 'collapsed_ids',
                  'shape', 'node_height_min', 'content_height_min',
                  'rmin', 'amin', 'amax']
    try:
        assert all(k in valid_keys for k in args.keys()), 'invalid keys'

        get = lambda x, default: float(args.get(x, default))  # shortcut

        tree = load_tree(tree_id)

        name, _ = get_tid(tree_id)  # "name" or "tid" is what identifies the tree

        # Active layouts.
        layout_names = json.loads(args.get('layouts', '[]'))  # active layouts
        layouts = [a for a in g_layouts.get(name, []) if a.name in layout_names]

        # Things that can be set in a tree style, and we override from the gui.
        shape = args.get('shape', 'rectangular')

        collapsed_shape = args.get('collapsed_shape', 'skeleton')

        node_height_min = get('node_height_min', 10)
        assert node_height_min > 0, 'node_height_min must be > 0'

        content_height_min = get('content_height_min', 5)
        assert content_height_min > 0, 'content_height_min must be > 0'

        overrides = {  # overrides of the tree style from the gui
            'shape': shape,
            'collapsed-shape': collapsed_shape,
            'node-height-min': node_height_min,
            'content-height-min': content_height_min}

        if shape == 'circular':
            overrides.update({
                'radius': get('rmin', 0),
                'angle-start': get('amin', -180),
                'angle-end': get('amax', 180)})

        # Get the rest: labels, viewport, zoom, collapsed_ids, searches.
        labels = json.loads(args.get('labels', '[]'))

        viewport = ([get(k, 0) for k in ['x', 'y', 'w', 'h']]
            if all(k in args for k in ['x', 'y', 'w', 'h']) else None)
        assert viewport is None or (viewport[2] > 0 and viewport[3] > 0), \
            'invalid viewport'  # width and height must be > 0

        zoom = (get('zx', 1), get('zy', 1), get('za', 1))
        assert all(z > 0 for z in zoom), 'zoom must be > 0'

        collapsed_ids = set(tuple(int(i) for i in node_id.split(',') if i != '')
            for node_id in json.loads(args.get('collapsed_ids', '[]')))

        searches = g_searches.get(tree_id)

        return {'tree': tree,
                'layouts': layouts,
                'overrides': overrides,
                'labels': labels,
                'viewport': viewport,
                'zoom': zoom,
                'collapsed_ids': collapsed_ids,
                'searches': searches}
    except (ValueError, AssertionError) as e:
        abort(400, str(e))


# Search.

def store_search(tree_id, args):
    """Store the results and parents of a search and return their numbers."""
    if 'text' not in args:
        abort(400, 'missing search text')

    text = args.pop('text').strip()
    func = get_search_function(text)

    try:
        tree = load_tree(tree_id)
        results = set(node for node in tree.traverse() if func(node))

        parents = set()  # all ancestors leading to the result nodes
        for node in results:
            current = node.up  # current node that we examine
            while (current is not None and current is not tree and
                   current not in parents):
                parents.add(current)
                current = current.up  # go to its parent

        g_searches.setdefault(tree_id, {})[text] = (results, parents)

        return len(results), len(parents)
    except HTTPError:
        raise
    except Exception as e:
        abort(400, f'evaluating expression: {e}')


def get_search_function(text):
    """Return a function of a node that returns True for the searched nodes."""
    if text.startswith('/'):  # command-based search
        return get_command_search(text)
    elif text == text.lower():  # case-insensitive search
        return lambda node: text in node.props.get('name', '').lower()
    else:  # case-sensitive search
        return lambda node: text in node.props.get('name', '')


def get_command_search(text):
    """Return the appropriate node search function according to the command."""
    parts = text.split(None, 1)
    if parts[0] not in ['/r', '/e', '/t']:
        abort(400, 'invalid command %r' % parts[0])
    if len(parts) != 2:
        abort(400, 'missing argument to command %r' % parts[0])

    command, arg = parts
    if command == '/r':  # regex search
        return lambda node: re.search(arg, node.props.get('name', ''))
    elif command == '/e':  # eval expression
        return get_eval_search(arg)
    elif command == '/t':  # topological search
        return get_topological_search(arg)
    else:
        abort(400, 'invalid command %r' % command)


def get_eval_search(expression):
    """Return a function of a node that evaluates the given expression."""
    try:
        code = compile(expression, '<string>', 'eval')
    except SyntaxError as e:
        abort(400, f'compiling expression: {e}')

    return lambda node: eval_on_node(code, node, safer=True)


def get_topological_search(pattern):
    """Return a function of a node that sees if it matches the given pattern."""
    try:
        tree_pattern = tm.TreePattern(pattern)
    except newick.NewickError as e:
        abort(400, 'invalid pattern %r: %s' % (pattern, e))

    return lambda node: tm.match(tree_pattern, node)


# Add trees.

def add_trees_from_request():
    """Add trees coming from a request to the server and return their names."""
    try:
        if request.content_type.startswith('application/json'):  # a POST
            trees_data = [req_json()]  # we have only one tree
            parser = 'name'
        else:  # the request comes from a form (e.g., from upload.html)
            trees_data = get_trees_from_form()
            parser = request.forms['parser']

        names = []
        for data in trees_data:
            nw = data['newick']
            name = data['name'].replace(',', '_')  # "," is used for subtrees
            names.append(name)
            add_tree(Tree(nw, parser=parser), name)

        return names
    except KeyError as e:
        abort(400, f'missing data in request: {e}')
    except (newick.NewickError, ValueError) as e:
        abort(400, f'malformed tree - {e}')


def get_trees_from_form():
    """Return list of dicts with tree info read from a form in the request."""
    if 'trees' in request.files:
        try:
            fu = request.files['trees']  # bottle FileUpload object
            return get_trees_from_file(fu.filename, fu.file)
        except (gzip.BadGzipFile, UnicodeDecodeError) as e:
            abort(400, f'when reading {fupload.filename}: {e}')
    else:
        return [{'name': request.forms['name'],
                 'newick': request.forms['newick']}]


def get_trees_from_file(filename, fileobject=None):
    """Return list of {'name': ..., 'newick': ...} extracted from file."""
    fileobject = fileobject or open(filename, 'rb')

    trees = []
    def extend(btext, fname):
        name = os.path.splitext(os.path.basename(fname))[0]  # /d/n.e -> n
        trees.extend(get_trees_from_nexus_or_newick(btext, name))

    if filename.endswith('.zip'):
        zf = zipfile.ZipFile(fileobject)
        for fname in zf.namelist():
            extend(zf.read(fname), fname)
    elif filename.endswith('.tar'):
        tf = tarfile.TarFile(fileobj=fileobject)
        for fname in tf.getnames():
            extend(tf.extractfile(fname).read(), fname)
    elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
        tf = tarfile.TarFile(fileobj=gzip.GzipFile(fileobj=fileobject))
        for fname in tf.getnames():
            extend(tf.extractfile(fname).read(), fname)
    elif filename.endswith('.gz'):
        extend(gzip.GzipFile(fileobj=fileobject).read(), filename)
    elif filename.endswith('.bz2'):
        extend(bz2.BZ2File(fileobject).read(), filename)
    else:
        extend(fileobject.read(), filename)

    return trees


def get_trees_from_nexus_or_newick(btext, name_newick):
    """Return list of {'name': ..., 'newick': ...} extracted from btext."""
    text = btext.decode('utf8').strip()

    try:  # we first try to read it as a nexus file
        trees = nexus.get_trees(text)
        return [{'name': name, 'newick': nw} for name, nw in trees.items()]
    except nexus.NexusError:  # if it isn't, we assume the text is a newick
        return [{'name': name_newick, 'newick': text}]  # only one tree!


# Explore.

def explore(tree, name=None, layouts=None,
            host='127.0.0.1', port=None, verbose=False,
            compress=None, keep_server=False, open_browser=True,
            server_args=None, **kwargs):
    """Run the web server, add tree and open a browser to visualize it."""
    add_tree(tree, name, layouts, kwargs)

    # Launch the thread with the http server (if not already running).
    if 'server' not in g_threads:
        print('Creating new server.')
        start_server(host, port, verbose, compress, keep_server, server_args)
    else:
        print('Using existing server.')

    host, port = get_server_address()
    print(f'Explorer available at http://{host}:{port}')

    if open_browser:
        open_browser_window(host, port)


def get_server_address(server=None):
    """Return (host, port) where the server is listening."""
    if server:
        return server.bind_addr  # (host, port)
    elif 'server' in g_threads:
        return g_threads['server'][1].bind_addr  # (host, port)
    else:
        return None, None


def get_layouts(tree_name=None, all_trees=False):
    """Return a list of layouts available for the given tree."""
    if not all_trees:
        return g_layouts.get(tree_name, [])
    else:
        return [x for xs in g_layouts.values() for x in xs]


def add_layouts(layouts, tree_name=None):
    """Add layouts to the given tree (None for generally available ones)."""
    current_layouts = g_layouts.setdefault(tree_name, [])
    for layout in layouts:
        if layout not in current_layouts:
            current_layouts.append(layout)


def add_tree(tree, name=None, layouts=None, extra_style=None):
    """Add tree, layouts, etc to the global variables, and return its name."""
    name = name or make_name()  # in case we didn't receive one

    assert ',' not in name, 'name cannot have ","'  # we use it for subtrees

    ops.update_sizes_all(tree)  # update all internal sizes (ready to draw!)

    g_trees[name] = tree  # add tree to the global dict of trees

    g_layouts[name] = layouts if layouts is not None else [BASIC_LAYOUT]

    if extra_style:
        style = {k.replace('_', '-'): v for k, v in extra_style.items()}
        g_layouts[name].append(Layout(name='extra arguments', draw_tree=style))

    return name


def remove_tree(name):
    """Remove all global references to the tree."""
    g_trees.pop(name)
    g_layouts.pop(name)


def start_server(host='127.0.0.1', port=None, verbose=False, compress=None,
                 keep_server=False, server_args=None, track=True):
    """Create a thread running the web server and return it and the server."""
    port = port or get_next_available_port(host)
    assert port, 'could not find any port available'

    if verbose:
        default_app().install(log_requests)

    if compress is not None:
        g_config['compress'] = compress  # global configuration

    server_args = server_args or {}  # extra server arguments
    server_args.setdefault('numthreads', 100)

    server = Server((host, port), default_app(), **server_args)

    thread = Thread(
        daemon=not keep_server,  # the server persists if it's not a daemon
        target=server.start)

    thread.start()

    if track:  # we normally want to keep track of the server in g_threads
        g_threads['server'] = (thread, server)

    return thread, server


def get_next_available_port(host='127.0.0.1', port_min=5000, port_max=6000):
    """Return the next available port where we can put a server socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for port in range(port_min, port_max):
        try:
            sock.bind((host, port))  # try to bind to the specified port
            sock.close()
            return port
        except socket.error:
            pass


def log_requests(fn):
    """Bottle plugin to log requests and exceptions on responses."""
    # It will wrap the endpoint callbacks if we do app.install(log_requests).
    def wrapper(*args, **kwargs):
        a = request.remote_addr  # shortcut
        info = (('' if a in ['127.0.0.1', 'localhost'] else f'from {a}: ') +
                request.method + ' ' + request.url)

        logging.info(info)  # this is where we log the request

        try:
            return fn(*args, **kwargs)  # the actual processing by bottle
        except Exception as e:  # log the errors
            logging.error('%s -> %d %r' % (info, e.status_code, e.body))
            raise  # and process them normally

    return wrapper


def make_name():
    """Return a unique tree name like 'tree-<number>'."""
    tnames = [name for name in g_trees
              if name.startswith('tree-') and name[len('tree-'):].isdecimal()]
    n = max((int(name[len('tree-'):]) for name in tnames), default=0) + 1
    return f'tree-{n}'


def open_browser_window(host='127.0.0.1', port=5000):
    """Try to open a browser window in a different process."""
    try:
        webbrowser.open(f'http://{host}:{port}')
    except webbrowser.Error:
        pass  # it's ok if we don't succeed


def stop_server(thread_server=None, remove_trees=True):
    """Stop the given server and its thread (from g_threads by default)."""
    thread_server = thread_server or g_threads.pop('server', None)

    if thread_server:
        thread, server = thread_server
        server.stop()
        thread.join()

    if remove_trees:  # with no server, we normally want to forget about trees
        names = list(g_trees.keys())  # copied so g_trees can be modified
        for name in names:
            remove_tree(name)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__, formatter_class=fmt)
    add = parser.add_argument  # shortcut
    add('FILE', help='file with the tree representation')
    add('--parser', choices=['name', 'support', 'indent'], default='support',
        help='tree is newick with name/support in internal nodes, or indented')
    add('--compress', action='store_true', help='send compressed data')
    add('--port', type=int, help='server port number')
    add('-v', '--verbose', action='store_true', help='be verbose')
    args = parser.parse_args()

    try:
        # Read tree(s) and add them to the server.
        for data in get_trees_from_file(args.FILE):
            nw = data['newick']
            name = data['name'].replace(',', '_')  # "," is used for subtrees
            add_tree(Tree(nw, parser=args.parser), name)

        # Launch the http server in a thread and open the browser.
        start_server('127.0.0.1', args.port, args.verbose, args.compress)
        host, port = get_server_address()
        open_browser_window(host, port)

        print(f'Explorer available at http://{host}:{port}')
        print('Press enter to stop the server and finish.')
        input()
    except (FileNotFoundError, newick.NewickError, ValueError) as e:
        sys.exit(f'Error using tree from {args.FILE}: {e}')
    except (OSError, OverflowError) as e:
        sys.exit(f'Error listening at port {port}: {e}')
    except AssertionError as e:
        sys.exit(e)
    except (KeyboardInterrupt, EOFError):
        pass  # bye!
