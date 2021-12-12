from http.server import BaseHTTPRequestHandler, HTTPServer
import re

class Window(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Eve Sign in</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Sign in Complete</p>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This window can now be closed.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        auth_code = self.path
        

class Callback_Server():
    def __init__(self, hostName, serverPort):
        self.webServer = HTTPServer((hostName, serverPort), Window)
        print("http://{}:{}".format(hostName, str(serverPort)))
        run = True
        while run:
            self.webServer.handle_request()
            if "/?code=" in auth_code:
                run = False
                self.webServer.server_close()
                self.code = re.findall("(?:=)(.*?)(?:&)", auth_code)[0]

if __name__ == "__main__":
    response = Callback_Server("localhost", 8080)
    print(response.code)
