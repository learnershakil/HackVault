import scapy.all as scapy
import threading
import time
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(filename='packet_sniffer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables for packet statistics
packet_count = 0
protocol_counts = {}

def packet_sniffer(packet):
    global packet_count
    global protocol_counts
    
    try:
        if packet.haslayer(scapy.IP):
            ip_src = packet[scapy.IP].src
            ip_dst = packet[scapy.IP].dst
            protocol = packet[scapy.IP].proto
            length = len(packet)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Increment packet count
            packet_count += 1
            
            # Update protocol counts
            if protocol in protocol_counts:
                protocol_counts[protocol] += 1
            else:
                protocol_counts[protocol] = 1
            
            # Log packet information
            logging.info("Timestamp: %s, IP Source: %s, IP Destination: %s, Protocol: %s, Length: %s", timestamp, ip_src, ip_dst, protocol, length)
            
            # Print packet information
            print(f"[{timestamp}] IP Source: {ip_src}, IP Destination: {ip_dst}, Protocol: {protocol}, Length: {length}")
            
            # Add custom packet analysis logic here
            
    except Exception as e:
        logging.error("An error occurred while processing packet: %s", str(e))

def start_sniffing(interface):
    logging.info("Starting packet sniffing on interface: %s", interface)
    scapy.sniff(iface=interface, prn=packet_sniffer, store=False)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Packet Sniffer")
    parser.add_argument("-i", "--interface", metavar="interface", required=True, help="Network interface to sniff packets on")
    return parser.parse_args()

args = parse_arguments()

# Start packet sniffing on a separate thread
sniffing_thread = threading.Thread(target=start_sniffing, args=(args.interface,))
sniffing_thread.start()

try:
    while True:
        time.sleep(1)
        # Print packet statistics every minute
        if datetime.now().second == 0:
            logging.info("Packet Count: %s, Protocol Counts: %s", packet_count, protocol_counts)
            print(f"Packet Count: {packet_count}, Protocol Counts: {protocol_counts}")
except KeyboardInterrupt:
    logging.info("Keyboard interrupt detected. Stopping packet sniffing.")
    print("\n[!] Keyboard interrupt detected. Stopping packet sniffing.")
    sniffing_thread.join()
    print("[+] Packet sniffing stopped.")
