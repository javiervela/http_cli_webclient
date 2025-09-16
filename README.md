# A Simple HTTP CLI Web Client.

> Made for CS 513 Computer Networks - Project 2

## Project Description

Simple command-line interface (CLI) application that allows users to send HTTP GET requests to a specified server and retrieve web content. The client connects to the server, sends a request for a specific resource, and optionally saves it to a file.

### Functionality

- Connects to a specified server using its hostname and port number.
- Sends an HTTP GET request for a specified path (resource).
- Receives and displays the server's response.
- Optionally saves the response content to a file.

### Enhancements

- Improved HTTP request formatting with additional headers.
- Response handling with status code and headers display.
- Enhanced request logging.


## Project Structure

```plaintext
http_cli_webclient/
├── README.md               # This file
├── pyproject.toml          # Project configuration file
└── src/webclient/          # Source code
    ├── __init__.py
    └── __main__.py
```

## Getting Started

> This Python project has been created using [`uv`](docs.astral.sh/uv/) for dependency and package management.

### Installation

You have 2 (easy) options to install the project and its dependencies:

- Use `uv` to create a virtual environment and install dependencies:

  ```bash
  uv sync                    # Create the virtual environment and install the package
  source .venv/bin/activate  # Activate the virtual environment
  ```

- Use `pip` to install the package:

  ```bash
  virtualenv -p python .venv # Create a virtual environment
  source .venv/bin/activate  # Activate the virtual environment
  pip install .              # Install the package
  ```

### Usage

You can run the web client using the script defined in `pyproject.toml`. This lets you start the client easily without manually running Python files.

```bash
# Run the web client
webclient -h
```

- `webclient`: Runs the web client.

  ```plaintext
  usage: webclient [-h] [-f FILE] [-nf] [host] [port] [path]
  
  positional arguments:
  host                  Hostname of the server to connect to (default: www.example.com)
  port                  Port number to connect to (default: 80)
  path                  Path to request from the server (default: /)
  
  options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Output file to save the response (default: ./webout)
  -nf, --no-file        Do not save output to a file
  ```

