#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import os
import logging
import glob

logging.basicConfig(filename="report_server.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

class Api:
    def __init__(self, filename):
        logging.info("Init api class")
        self.path = "/Users/pastuhox/things/http_file_storage/storage"
        self.filename  = filename
        self.directory = filename[:2]
        logging.info("End init api class")

    def download(self):
        logging.info(f"DOWNLOAD {self.filename} {self.directory}")

    def delete(self):
        try:
            file_path = self._create_file_path()
            os.remove(file_path)
            return f"Deleted {self.filename} from the disk."
        except FileNotFoundError as e:
            logging.error(f"method delete {e}")
            return f"File {self.filename} was not found on the disk."
    
    def upload(self):
        logging.info(f"method upload filename {filename} ")

    def _create_file_path(self):
        return f"{self.path}/{self.directory}/{self.filename}"




class S(BaseHTTPRequestHandler, Api):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._parse_path()
        self._set_response()
        self.wfile.write(f"{self.resp_msg}".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
    
    def _parse_path(self):
        logging.info(f"parsing path {self.path}")
        if self.path.startswith("/api/"):
            logging.info(f"self.path = {self.path}")
            path_lst = self.path.split("/")[2:]
            self._parse_method(path_lst)
            logging.info(path_lst)
    
    def _parse_method(self, data):
        try:
            method, filename = data
            logging.info(f"data = {data}")
            Api.__init__(self, filename)
            if not filename:
                self.send_response(404)
    
            logging.info(f"method = {method}")
            if method == 'download':
                self.download()
            elif method == 'upload':
                self.upload()
            elif method == 'delete':
                self.resp_msg = self.delete()
            else:
                logging.info("No method")
        except ValueError:
            logging.info("ValueError")
            self.send_response(500)
        


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
