# -*- coding: utf-8 -*-
import os

from http.server import HTTPServer
from server.request_handler import RequestHandler


HOST = 'localhost'
PORT = 8080

if __name__ == '__main__':
    
    server = HTTPServer((HOST, PORT), RequestHandler)

    try:
        print(f'Server started at http://{HOST}:{PORT}'.format(HOST, PORT))
        os.system(f'open http://{HOST}:{PORT}')  # [!!!] maybe only ok for macOS
        server.serve_forever()

    except KeyboardInterrupt:
        print('\nGoodbye')
        server.server_close()
