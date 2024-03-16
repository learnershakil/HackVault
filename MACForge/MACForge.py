import subprocess
import random
import re

def change_mac(interface, new_mac):
    print(f"Changing MAC address of {interface} to {new_mac}")

    # Disable the interface
    subprocess.call(["ifconfig", interface, "down"])

    # Change the MAC address
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])

    # Enable the interface
    subprocess.call(["ifconfig", interface, "up"])

def generate_random_mac():
    # Generate a random MAC address with the locally administered bit set
    return "02:" + ":".join([format(random.randint(0x00, 0xff), '02x') for _ in range(5)])

def restore_original_mac(interface, original_mac):
    print(f"Restoring original MAC address of {interface} to {original_mac}")
    change_mac(interface, original_mac)

def get_current_mac(interface):
    # Extract the current MAC address from the ifconfig output
    ifconfig_result = subprocess.check_output(["ifconfig", interface]).decode("utf-8")
    mac_address_search_result = re.search(r"(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", ifconfig_result)
    if mac_address_search_result:
        return mac_address_search_result.group(0)
    else:
        return None

def validate_mac(mac_address):
    # Validate MAC address format
    return re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", mac_address)

def main():
    interface = input("Enter the name of the interface (e.g., eth0, wlan0): ")
    new_mac = input("Enter the new MAC address (leave blank for random): ")

    # Validate the interface name
    if not interface:
        print("Interface name cannot be empty.")
        return

    # Validate the MAC address format
    if new_mac and not validate_mac(new_mac):
        print("Invalid MAC address format.")
        return

    try:
        # Retrieve the original MAC address
        original_mac = get_current_mac(interface)

        # Generate a random MAC address if not provided by the user
        if not new_mac:
            new_mac = generate_random_mac()

        # Change the MAC address
        change_mac(interface, new_mac)

        # Verify that the MAC address has been changed successfully
        current_mac = get_current_mac(interface)
        if current_mac == new_mac:
            print(f"MAC address successfully changed to {new_mac}")
        else:
            print("Failed to change MAC address.")

        # Restore the original MAC address if requested by the user
        restore_option = input("Do you want to restore the original MAC address? (yes/no): ").lower()
        if restore_option == "yes":
            restore_original_mac(interface, original_mac)

    except subprocess.CalledProcessError:
        print("An error occurred while changing the MAC address.")

if __name__ == "__main__":
    main()
