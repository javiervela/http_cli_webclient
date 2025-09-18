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
        packet=False,
        verbose=False,
    ):
        self.host = host
        self.port = port
        self.path = path
        self.output_file = output_file
        self.ping = ping
        self.packet = packet
        self.packet_sizes = []
        self.packet_times = []
        self.verbose = verbose

        if not self.path.startswith("/"):
            self.path = "/" + self.path

        self.base_url = f"http://{self.host}:{self.port}{self.path}"

    def _receive_all(self, sock):
        """Receive all data from the socket until closed and tracks packet sizes and times"""
        response = b""
        buffer_size = 10240  # 10K bytes
        while True:
            start_read = time.time()
            chunk = sock.recv(buffer_size)
            end_read = time.time()
            if not chunk:
                break
            response += chunk
            self.packet_sizes.append(len(chunk))
            self.packet_times.append((end_read - start_read) * 1000)

        return response.decode()

    def _parse_response(self, response):
        """Parse the HTTP response and return status code and reason phrase"""
        match = HTTP_RESPONSE_PATTERN.match(response)
        if match:
            status_code = int(match.group(1))
            reason_phrase = match.group(2)
            return status_code, reason_phrase
        return None, None

    def _log(self, code, reason, ip_address, rtt):
        print(
            f"[LOG] HTTP GET Request\n"
            f"[LOG]  URL                  : {self.base_url}\n"
            f"[LOG]  IP Address           : {ip_address}\n"
            f"[LOG]  Output File          : {self.output_file if self.output_file else 'None'}\n"
            f"[LOG]  Status Code          : {code}\n"
            f"[LOG]  Reason               : {reason}\n"
            f"[LOG]  RTT                  : {rtt:.2f} ms\n"
            f"[LOG]  Response Size        : {sum(self.packet_sizes)} bytes\n"
            f"[LOG]  Response Time        : {rtt + sum(self.packet_times):.2f} ms\n"
            f"[LOG]  Number of Packets    : {len(self.packet_sizes)}\n"
            f"[LOG]  Packet Sizes (bytes) : {' '.join(f'{size:6}' for size in self.packet_sizes)}\n"
            f"[LOG]  Packet Times (ms)    : {' '.join(f'{t:6.2f}' for t in self.packet_times)}\n"
        )

    def get(self):
        # Construct the HTTP GET request message
        request_message = HTTP_GET_TEMPLATE.format(host=self.host, path=self.path)

        # Create a TCP socket
        with socket(AF_INET, SOCK_STREAM) as sock:
            # Connect to the server, measuring RTT
            start_time = time.time()
            sock.connect((self.host, self.port))
            end_time = time.time()
            rtt = (end_time - start_time) * 1000

            # Get IP address
            ip_address = sock.getpeername()[0]

            # Measure end time and calculate RTT
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
            print(f"{ip_address} RTT {int(rtt)} ms")
        if self.packet:
            for p_size, p_time in zip(self.packet_sizes, self.packet_times):
                print(f"{p_size} bytes {p_time:.2f} ms")
        if self.verbose:
            self._log(
                code=status_code,
                reason=reason_phrase,
                ip_address=ip_address,
                rtt=rtt,
            )
