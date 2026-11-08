"""Read-only local preview with the production base path; no hosting credentials."""
import argparse,http.server
from urllib.parse import urlsplit
parser=argparse.ArgumentParser();parser.add_argument('--directory',default='dist');parser.add_argument('--port',type=int,default=8767);args=parser.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=args.directory,**kw)
 def do_GET(self):
  if urlsplit(self.path).path.startswith('/ever-youth/'):
   self.path=self.path[len('/ever-youth'):]
  super().do_GET()
http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
