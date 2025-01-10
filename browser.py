import socket
import ssl

# Class to parse the URL
class URL: 
    def __init__(self, url):            # Constructor for the URL class
        self.scheme, url = url.split("://", 1)  # Split the URL into scheme and the rest
        assert self.scheme in ["http", "https"]  # Assert that the scheme is either HTTP or HTTPS
        self.host, url = url.split("/", 1)      # Split the URL into host and the rest
        self.path = "/" + url                   # The path is the rest of the URL
        if self.scheme == "http":
            self.port = 80                     # Default port for HTTP is 80
        elif self.scheme == "https":
            self.port = 443                    # Default port for HTTPS is 443

        if ":" in self.host:                            # If the host contains a colon, split the host and port
            self.host, port =self.host.split(":", 1)    # Split the host and port
            self.port = int(port)                       # Convert the port to an integer   

    # Function to send a request to the server
    def requests(self): 
        s = socket.socket(
            family=socket.AF_INET,      # AF_INET is the address family for IPv4  
            type=socket.SOCK_STREAM,    # Sockets are used for sending and receiving data
            proto=socket.IPPROTO_TCP,   # IPPROTO_TCP is the protocol for TCP, which is a connection-oriented protocol
        )
        s.connect((self.host, self.port))                       # Connect to the host on the specified port
        if self.scheme == "https":                              # If the scheme is HTTPS, wrap the socket in an SSL context
            ctx = ssl.create_default_context()                  # Create a default SSL context
            s = ctx.wrap_socket(s, server_hostname=self.host)   # Wrap the socket in an SSL context   

        request = "GET {} HTTP/1.0\r\n".format(self.path) # Create the request string
        request += "Host: {}\r\n".format(self.host)       # Add the host to the request
        request += "\r\n"                                 # Add a blank line to the request
        s.send(request.encode("utf8"))                    # Send the request to the server

        response = s.makefile("r", encoding="utf8", newline="\r\n") # Make a file object to read the response
        statusline = response.readline()                            # Read the status line
        version, status, explanation = statusline.split(" ", 2)     # Split the status line into version, status, and explanation
        assert status == "200"                                      # Assert that the status is 200 (connection accepted)

        response_headers = {}                                       # Create a dictionary to store the response headers
        while True:                                                 # Loop until the end of the response
            line = response.readline()                              # Read the next line
            if line == "\r\n": break                                # If the line is a blank line, break the loop
            header, value = line.split(":", 1)                      # Split the line into header and value
            response_headers[header.casefold()] = value.strip()     # Headers are case-insensitive, so they are normalised to lowercase. Whitespace is stripped from the value since it is insiginficant in HTTP header values.

        assert "transfer-encoding" not in response_headers  # Assert that the transfer encoding is not in the response headers
        assert "content-encoding" not in response_headers   # Assert that the content encoding is not in the response headers
        
        content = response.read()   # Read the content of the response
        s.close()                   # Close the socket
        return content              # Return the content

# Function to show the content of the response
def show(body):
    in_tag = False              # Boolean to check if we are in a tag
    for c in body:              # Loop through each character in the body
        if c == "<":            # If the character is a less than sign, we are in a tag
            in_tag = True
        elif c == ">":          # If the character is a greater than sign, we are not in a tag
            in_tag = False
        elif not in_tag:        # If we are not in a tag, print the character
            print(c, end="")

# Function to load the URL
def load(url): 
    body = url.requests() # Get the body of the response
    show(body)            # Show the body
    
# Main function
if __name__ == "__main__": 
    import sys              # Import the sys module
    load(URL(sys.argv[1]))  # Load the URL

