import re
import time
from socket import socket, AF_INET, SOCK_STREAM, IPPROTO_TCP
import struct


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
        info=False,
        verbose=False,
    ):
        self.host = host
        self.port = port
        self.path = path
        self.output_file = output_file
        self.status_code = None
        self.reason_phrase = None
        self.ping = ping
        self.ip_address = None
        self.rtt_ping = None
        self.packet = packet
        self.packet_sizes = []
        self.packet_times = []
        self.info = info
        self.rtt = None
        self.rttvar = None
        self.verbose = verbose

        if not self.path.startswith("/"):
            self.path = "/" + self.path

        self.base_url = f"http://{self.host}:{self.port}{self.path}"

    def _receive_all(self, sock):
        """Receive all data from the socket until closed and tracks packet sizes and times"""
        response = b""
        buffer_size = 10240  # 10K bytes
        while True:
            chunk = sock.recv(buffer_size)
            read_time = time.time()
            if not chunk:
                break
            response += chunk
            self.packet_sizes.append(len(chunk))
            self.packet_times.append(read_time)

        # Ignore errors in decoding
        return response.decode(errors="ignore")

    def _parse_response(self, response):
        """Parse the HTTP response and return status code and reason phrase"""
        match = HTTP_RESPONSE_PATTERN.match(response)
        if match:
            status_code = int(match.group(1))
            reason_phrase = match.group(2)
            return status_code, reason_phrase
        return None, None

    def _get_tcp_info_rtt(self, sock):
        """Query the Linux kernel for TCP statistics (RTT and RTT variance) using getsockopt(TCP_INFO)"""
        # TCP_INFO
        TCP_INFO = 11

        # Request TCP info struct from the kernel
        info = sock.getsockopt(IPPROTO_TCP, TCP_INFO, 104)

        # Unpack the struct to get RTT and RTT variance
        fmt = "B" * 7 + "I" * 24
        tcp_info = struct.unpack(fmt, info)
        rtt_micros, rttvar_micros = tcp_info[22], tcp_info[23]

        rtt_ms = rtt_micros / 1000.0
        rttvar_ms = rttvar_micros / 1000.0

        return rtt_ms, rttvar_ms

    def _log(self):
        if self.ping:
            print(f"{self.ip_address} RTT {int(self.rtt_ping)} ms")
        if self.packet:
            for p_size, p_time in zip(self.packet_sizes, self.packet_times):
                print(f"{p_size} bytes {int(p_time)} ms")
        if self.info:
            print(
                f"TCP_INFO: RTT {int(self.rtt)} ms\n"
                f"TCP_INFO: RTT_var {int(self.rttvar)} ms"
            )
        if self.verbose:
            print(
                f"[LOG] HTTP GET Request\n"
                f"[LOG]  URL                     : {self.base_url}\n"
                f"[LOG]  IP Address              : {self.ip_address}\n"
                f"[LOG]  Output File             : {self.output_file if self.output_file else 'None'}\n"
                f"[LOG]  Status Code             : {self.status_code}\n"
                f"[LOG]  Reason                  : {self.reason_phrase}\n"
                f"[LOG]  RTT (-ping)             : {self.rtt_ping:.2f} ms\n"
                f"[LOG]  RTT (TCP_INFO)          : {self.rtt:.2f} ms\n"
                f"[LOG]  RTT Variance (TCP_INFO) : {self.rttvar:.2f} ms\n"
                f"[LOG]  Response Size           : {sum(self.packet_sizes)} bytes\n"
                f"[LOG]  Response Time           : {self.rtt_ping + sum(self.packet_times):.2f} ms\n"
                f"[LOG]  Number of Packets       : {len(self.packet_sizes)}\n"
                f"[LOG]  Packet Sizes (bytes)    : {' '.join(f'{size:8}' for size in self.packet_sizes)}\n"
                f"[LOG]  Packet Times (ms)       : {' '.join(f'{t:8.2f}' for t in self.packet_times)}"
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
            self.rtt_ping = (end_time - start_time) * 1000

            # Get IP address
            self.ip_address = sock.getpeername()[0]

            self.packet_sizes.append(0)
            self.packet_times.append(start_time)

            # Send the HTTP GET request
            sock.sendall(request_message.encode())

            # Receive the response
            response = self._receive_all(sock)

            self.rtt, self.rttvar = self._get_tcp_info_rtt(sock)
            self.packet_times = [
                (t - self.packet_times[0]) * 1000 for t in self.packet_times[0:]
            ]

        # Parse the response status
        self.status_code, self.reason_phrase = self._parse_response(response)

        if self.output_file:
            # Log the status code and reason phrase
            with open(self.output_file, "w") as f:
                f.write(response)

        self._log()
