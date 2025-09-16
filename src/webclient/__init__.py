import re
import time
from socket import socket, AF_INET, SOCK_STREAM


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
    def __init__(
        self,
        host,
        port,
        path,
        output_file=None,
        ping=False,
        verbose=False,
    ):
        self.host = host
        self.port = port
        self.path = path
        self.output_file = output_file
        self.ping = ping
        self.verbose = verbose

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

    def _log(self, code, reason, rtt=None):
        print(
            f"[LOG]  HTTP GET Request\n"
            f"[LOG]    URL         : {self.base_url}\n"
            f"[LOG]    Output File : {self.output_file if self.output_file else 'None'}\n"
            f"[LOG]    Status Code : {code}\n"
            f"[LOG]    Reason      : {reason}\n"
            f"[LOG]    RTT         : {f'{rtt:.2f} ms' if rtt is not None else 'N/A'}\n"
        )

    def get(self):
        # Construct the HTTP GET request message
        request_message = HTTP_GET_TEMPLATE.format(host=self.host, path=self.path)

        # Create a TCP socket
        with socket(AF_INET, SOCK_STREAM) as sock:
            # Measure RTT (even if ping is disabled)
            start_time = time.time()

            # Connect to the server
            sock.connect((self.host, self.port))

            # Measure end time and calculate RTT
            end_time = time.time()
            rtt = (end_time - start_time) * 1000

            # Send the HTTP GET request
            sock.sendall(request_message.encode())

            # Receive the response
            response = self._receive_all(sock)

        # Parse the response status
        status_code, reason_phrase = self._parse_response(response)

        if self.output_file:
            # Log the status code and reason phrase
            with open(self.output_file, "w") as f:
                f.write(response)

        if self.ping:
            print(f"RTT: {rtt:.2f} ms")
        if self.verbose:
            self._log(
                code=status_code, reason=reason_phrase, rtt=(rtt if self.ping else None)
            )
