from http.server import BaseHTTPRequestHandler, HTTPServer
import re

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        auth_code = self.path
        

class Callback_Server():
    def __init__(self, hostName, serverPort):
        self.webServer = HTTPServer((hostName, serverPort), MyServer)
        run = True
        while run:
            self.webServer.handle_request()
            if "/?code=" in auth_code:
                run = False
                self.webServer.server_close()
                self.code = re.sub("\/\?code=", "", auth_code)
                self.code = re.sub("&state=unique-state", "", self.code)
        
        
if __name__ == "__main__":
    res = Callback_Server("localhost", 8080)
    print(res.code)
