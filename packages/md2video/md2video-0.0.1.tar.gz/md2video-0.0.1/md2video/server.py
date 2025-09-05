# A live server that returns rendered reveal.js html

import os, io, sys, json
from http.server import SimpleHTTPRequestHandler, test, ThreadingHTTPServer, HTTPStatus
from .md2slidemd import md_to_slide_md, md_to_ast
from .md2image import md_to_revealjs_html

class SlideMDHandler(SimpleHTTPRequestHandler):
    '''
    returns rendered reveal.js html
    '''
    server_version = "SlideMDHandler/1.0"
    index_pages = ("index.html", "index.htm")
    extensions_map = _encodings_map_default = {
        '.gz': 'application/gzip',
        '.Z': 'application/octet-stream',
        '.bz2': 'application/x-bzip2',
        '.xz': 'application/x-xz',
    }
    show_slide_md=False

    def do_GET(self):
        """Serve a GET request."""
        path = self.translate_path(self.path)
        if path.endswith('.md') and os.path.isfile(path):
            print(f"Generating reveal.js result for {path}")
            with open(path, 'r') as md_file:
                data = md_file.read()
                if self.show_slide_md:
                    slide_md = md_to_slide_md(data)
                    import html
                    slide_md = f'<div style="white-space: pre-wrap;">{html.escape(slide_md)}</div>'
                else:
                    # slide_md = json.dumps(md_to_ast(md_to_slide_md(data)), ensure_ascii=False)
                    slide_md = md_to_revealjs_html(md_to_slide_md(data))
                    # slide_md = md_to_revealjs_html(data)
            enc = sys.getfilesystemencoding()
            encoded = slide_md.encode(enc, 'surrogateescape')
            f = io.BytesIO()
            f.write(encoded)
            f.seek(0)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()
        else:
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', default='127.0.0.1', metavar='ADDRESS',
                        help='bind to this address '
                             '(default: all interfaces)')
    parser.add_argument('-d', '--directory', default=os.getcwd(),
                        help='serve this directory '
                             '(default: current directory)')
    parser.add_argument('-p', '--protocol', metavar='VERSION',
                        default='HTTP/1.0',
                        help='conform to this HTTP version '
                             '(default: %(default)s)')
    parser.add_argument('port', default=8000, type=int, nargs='?',
                        help='bind to this port '
                             '(default: %(default)s)')
    parser.add_argument('--show-slide-md', action='store_true', default=False)

    args = parser.parse_args()
    if args.show_slide_md:
        SlideMDHandler.show_slide_md = True
    HandlerClass = SlideMDHandler
    test(
        HandlerClass=SlideMDHandler,
        ServerClass=ThreadingHTTPServer,
        port=args.port,
        bind=args.bind,
        protocol=args.protocol,
    )
    # ServerClass = ThreadingHTTPServer
    # import socket
    # def _get_best_family(*address):
    #     infos = socket.getaddrinfo(
    #         *address,
    #         type=socket.SOCK_STREAM,
    #         flags=socket.AI_PASSIVE,
    #     )
    #     family, type, proto, canonname, sockaddr = next(iter(infos))
    #     return family, sockaddr
    # ServerClass.address_family, addr = _get_best_family(args.bind, args.port)
    # HandlerClass.protocol_version = args.protocol
    # with ServerClass(addr, HandlerClass) as httpd:
    #     host, port = httpd.socket.getsockname()[:2]
    #     url_host = f'[{host}]' if ':' in host else host
    #     print(
    #         f"Serving HTTP on {host} port {port} "
    #         f"(http://{url_host}:{port}/) ..."
    #     )
    #     try:
    #         httpd.serve_forever()
    #     except KeyboardInterrupt:
    #         print("\nKeyboard interrupt received, exiting.")
    #         sys.exit(0)

