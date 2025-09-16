from socket import socket, AF_INET, SOCK_STREAM
import re


# Basic HTTP GET request template
HTTP_GET_TEMPLATE = (
    "GET {path} HTTP/1.0\r\n"
    "Host: {host}\r\n"
    "Accept: */*\r\n"
    "Accept-Language: en-US,en;q=0.9\r\n"
    "User-Agent: SimpleHTTPClient/0.1.0\r\n"
    "Connection: close\r\n"
    "\r\n"
)
# Regex pattern to parse HTTP response status line (e.g., HTTP/1.1 200 OK)
HTTP_RESPONSE_PATTERN = re.compile(r"HTTP/\d\.\d\s+(\d{3})\s+([^\r\n]+)\r\n")


class HTTPWebClient:
    def __init__(self, host, port, path):
        self.host = host
        self.port = port
        self.path = path

        if not self.path.startswith("/"):
            self.path = "/" + self.path

        self.base_url = f"http://{self.host}:{self.port}{self.path}"

    def _receive_all(self, sock):
        """Receive all data from the socket until closed"""
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        return response.decode()

    def _parse_response(self, response):
        """Parse the HTTP response and return status code and reason phrase"""
        match = HTTP_RESPONSE_PATTERN.match(response)
        if match:
            status_code = int(match.group(1))
            reason_phrase = match.group(2)
            return status_code, reason_phrase
        return None, None

    def _log(self, file, code, reason):
        print(
            f"HTTP GET Request\n"
            f"  URL         : {self.base_url}\n"
            f"  Output File : {file if file else 'None'}\n"
            f"  Status Code : {code}\n"
            f"  Reason      : {reason}\n"
        )

    def get(self, output_file):
        # Construct the HTTP GET request message
        request_message = HTTP_GET_TEMPLATE.format(host=self.host, path=self.path)

        # Create a TCP socket
        with socket(AF_INET, SOCK_STREAM) as sock:
            # Connect to the server
            sock.connect((self.host, self.port))
            # Send the HTTP GET request
            sock.sendall(request_message.encode())
            # Receive the response
            response = self._receive_all(sock)

        # Parse the response status
        status_code, reason_phrase = self._parse_response(response)

        if output_file:
            # Log the status code and reason phrase
            with open(output_file, "w") as f:
                f.write(response)

        self._log(output_file, status_code, reason_phrase)
