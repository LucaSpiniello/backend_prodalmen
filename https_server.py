import os
import ssl
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prodalwebV3.settings')

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='server.crt', keyfile='server.key')

from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
server_address = ('0.0.0.0', 8000)

httpd = WSGIServer(server_address, WSGIRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.set_app(application)
print("Starting HTTPS server on port 8000...")
httpd.serve_forever()