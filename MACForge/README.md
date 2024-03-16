# MACForge

MACForge is a Python script designed to facilitate the modification of Media Access Control (MAC) addresses for network interfaces. Let's break down how it works:

## User Interaction

MACForge interacts with the user through the command-line interface (CLI). It prompts the user to input the name of the network interface they wish to modify and optionally provides a new MAC address.

## Input Validation

The script validates the user input to ensure that the interface name is not empty and that the provided MAC address (if any) follows the correct format.

## Original MAC Address Retrieval

Before making any changes, MACForge retrieves the original MAC address of the specified network interface. This step allows the script to restore the original MAC address later if desired.

## Random MAC Address Generation

If the user does not provide a specific MAC address, MACForge generates a random MAC address with the locally administered bit set. This feature enhances privacy and security by preventing tracking based on a fixed MAC address.

## MAC Address Modification

Using subprocess calls, MACForge disables the specified network interface, changes its MAC address to the new value (if provided), and then re-enables the interface. This process effectively modifies the MAC address of the selected network interface.

## Verification

After changing the MAC address, MACForge verifies whether the modification was successful by comparing the current MAC address with the new one. If they match, the script confirms that the MAC address change was successful; otherwise, it indicates that the modification failed.

## Optional MAC Address Restoration

MACForge offers the user the option to restore the original MAC address of the network interface. If the user chooses to do so, the script reverts the MAC address to its original value.

## Error Handling

MACForge incorporates error handling mechanisms to gracefully handle exceptions that may occur during the execution of subprocess commands or other operations. It provides informative error messages to assist users in troubleshooting issues.

By encapsulating these functionalities, MACForge provides a convenient and user-friendly tool for altering MAC addresses, enabling users to enhance privacy, security, and network management capabilities.
