import pkgutil
import importlib
import mimetypes
import os
import re
import io

from flask import Blueprint, current_app, request, send_file, Response


def is_local():
    server_type = current_app.config.get('SERVER_TYPE', 'central')
    return server_type == 'local'


def is_central():
    return not is_local()


def get_service_for_class(class_name):
    from .core import Service
    import MookAPI.services as s
    class_name = class_name.split('.')[-1]
    for name, service in s.__dict__.iteritems():
        if isinstance(service, Service):
            if service.__model__.__name__ == class_name:
                return service
    return None


def current_local_server():
    from MookAPI.services import local_servers
    try:
        return local_servers.get_current() if is_local() else None
    except:
        return None


def register_blueprints(app, package_name, package_path):
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


def unique(list):
    seen = set()
    seen_add = seen.add
    return [x for x in list if not (x in seen or seen_add(x))]


def send_file_partial(content_file):
    """
        Simple wrapper around send_file which handles HTTP 206 Partial Content
        (byte ranges)
        TODO: handle all send_file args, mirror send_file's error handling
        (if it has any)
    """
    range_header = request.headers.get('Range', None)
    if not range_header: return send_file(io.BytesIO(content_file.read()),
                                          attachment_filename=content_file.filename,
                                          mimetype=content_file.contentType)

    size = content_file.length
    byte1, byte2 = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]: byte1 = int(g[0])
    if g[1]: byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1

    data = content_file.read()

    rv = Response(data,
                  206,
                  mimetype=content_file.contentType,
                  direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))

    return rv
