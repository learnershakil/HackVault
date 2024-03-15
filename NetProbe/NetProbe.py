import socket
import threading

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Port {port} on {host} is open")
        sock.close()
    except socket.error:
        pass

def scan_host(host, ports):
    print(f"Scanning ports for {host}...")
    for port in ports:
        scan_port(host, port)

def main():
    target_hosts = input("Enter the target host(s) to scan (separated by commas): ").split(',')
    port_range = input("Enter the port range to scan (e.g., 1-100 or a single port): ")

    if '-' in port_range:
        start_port, end_port = map(int, port_range.split('-'))
        ports = range(start_port, end_port + 1)
    else:
        ports = [int(port_range)]

    threads = []
    for host in target_hosts:
        thread = threading.Thread(target=scan_host, args=(host.strip(), ports))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
