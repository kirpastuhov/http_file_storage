#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import urllib.parse
import posixpath
import mimetypes
import re
import sys
import os
import logging
import glob
import shutil
import hashlib
import daemon


logging.basicConfig(filename="/Users/pastuhox/things/http_file_storage/report_server.log",
        format='%(asctime)s %(message)s',
        filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.INFO)


class S(BaseHTTPRequestHandler):

    def do_GET(self):
        f = self._parse_path()
        if f:
            self._copyfile(f, self.wfile)
            f.close()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.info(f"file = {post_data.decode('utf-8')}")
        hash_object = hashlib.sha512(post_data)
        hex_dig = hash_object.hexdigest()
        logging.info(hex_dig)
        try:
            self._save_file(hex_dig, post_data)
            self._set_response(200, f"Saved to the disk {hex_dig}", 'text/plain')
        except Exception as e:
            logging.error(e)
            self._set_response(404, "File not found", "text/plain")

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
                self._set_response(404, "404 Error", "text/plain")

            logging.info(f"method = {method}")
            if method == 'download':
                return self._download()
            elif method == 'delete':
                self._delete()
            else:
                logging.info("No method")
        except ValueError:
            logging.info("ValueError")
            self._set_response(500, "500 Error", "text/plain")

    def _create_file_path(self):
        self.path = "/Users/pastuhox/things/http_file_storage/store"
        self.directory = self.filename[:2]
        return f"{self.path}/{self.directory}/{self.filename}"

    def _download(self):
        path = self.file_path
        f = None
        ctype = self._guess_type(self.file_path)
        try:
            f = open(self.file_path, 'rb')
        except IOError:
            self._set_response(404, "File not found", "text/plain")
            logging.info("404 file not found")
            return None
        self._set_response(200, "Downloaded file", ctype)
        return f

    def _delete(self):
        try:
            file_path = self._create_file_path()
            os.remove(file_path)
            self._set_response(200, f"Deleted {self.filename} from the disk.", "text/plain")
        except FileNotFoundError as e:
            self._set_response(404, f"File {self.filename} was not found on the disk.", "text/plain")

    def _set_response(self, code, message, content_type):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def _save_file(self, hex_dig, post_data):
        directory = f"store/{hex_dig[:2]}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f"{directory}/{hex_dig}", "w") as f:
            f.write(post_data.decode('utf-8'))

    def _guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    def _copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    if not mimetypes.inited:
        mimetypes.init()
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


def run(server_class=HTTPServer, handler_class=S, port=8080):
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
    with daemon.DaemonContext(
        chroot_directory=None,
        working_directory='/Users/pastuhox/things/http_file_storage'):
        logging.info(os.getcwd())
        run()


