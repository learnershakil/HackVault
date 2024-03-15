# NetProbe

NetProbe is a simple port scanning tool designed to check for open ports on one or more target hosts.

## How It Works

### User Input

NetProbe prompts the user to input the target host(s) they want to scan and the port range they want to check for open ports. The user can specify multiple hosts separated by commas and a port range using the format "start_port-end_port".

### Port Scanning Logic

Once the user provides the target host(s) and port range, NetProbe uses Python's socket library to establish connections to each port on the specified host(s). It iterates over each port in the provided range and attempts to connect to it on the target host(s).

### Threaded Execution

To improve efficiency, NetProbe uses multi-threading to scan multiple hosts concurrently. This allows it to scan multiple hosts or ports simultaneously, reducing the overall scanning time.

### Output

As NetProbe scans each port on each host, it prints a message indicating whether the port is open or closed. If a connection is successfully established, it prints "Port [port] on [host] is open". If the connection fails or times out, it silently ignores the error and continues scanning.

### Completion

Once all specified hosts have been scanned for open ports within the given range, NetProbe completes its execution.

## Purpose

Overall, NetProbe provides a simple and efficient way to scan for open ports on one or more target hosts, making it useful for network reconnaissance and security auditing purposes.
