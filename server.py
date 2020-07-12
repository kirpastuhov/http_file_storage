#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import urllib.parse
import posixpath
import mimetypes
import re
import os
import logging
import glob
import shutil

logging.basicConfig(filename="report_server.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.INFO)



class S(BaseHTTPRequestHandler):

    def do_GET(self):
        f = self._parse_path()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
    
    def _create_file_path(self):
        self.path = "/Users/pastuhox/things/http_file_storage/store"
        self.directory = self.filename[:2]
        return f"{self.path}/{self.directory}/{self.filename}"

    def _parse_path(self):
        logging.info(f"parsing path {self.path}")
        if self.path.startswith("/api/"):
            logging.info(f"self.path = {self.path}")
            path_lst = self.path.split("/")[2:]
            return self._parse_method(path_lst)
    
    def _parse_method(self, data):
        try:
            method, self.filename = data
            logging.info(f"data = {data}")
            self.file_path = self._create_file_path()

            if not self.filename:
                self.send_response(404)
    
            logging.info(f"method = {method}")
            if method == 'download':
                return self._download()
            elif method == 'upload':
                self.upload()
            elif method == 'delete':
                self._delete()
            else:
                logging.info("No method")
        except ValueError:
            logging.info("ValueError")
            self.send_response(500)
    
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)
        
    def _download(self):
        path = self.file_path
        f = None
        ctype = self.guess_type(self.file_path)
        try:
            f = open(self.file_path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            logging.info("404 file not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def _delete(self):
        try:
            file_path = self._create_file_path()
            os.remove(file_path)
            self.send_response(200)
            self.send_header("Content-type", 'text/html')
            self.end_headers()
            self.wfile.write(f"Deleted {self.filename} from the disk.".encode('utf-8'))
        except FileNotFoundError as e:
            self.send_response(404)
            self.send_header("Content-type", 'text/html')
            self.end_headers()
            self.wfile.write(f"File {self.filename} was not found on the disk.".encode('utf-8'))
            logging.error(f"File {self.filename} was not found on the disk.".encode('utf-8'))
            logging.error(f"method delete {e}")

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
