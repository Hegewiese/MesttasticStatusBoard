#!/usr/bin/env python3
"""
main.py - Meshtastic Status Board Main Application
A comprehensive tool for discovering, connecting to, and monitoring Meshtastic devices.
"""

import sys
import os
import subprocess
import threading
import time
import re
from datetime import datetime

NODES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nodes")


def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")

    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Check virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print("✓ Running in virtual environment")
    else:
        print("⚠ Not running in virtual environment (recommended)")

    return True


def load_nodes():
    """Load known nodes from the nodes file."""
    nodes = []

    if not os.path.exists(NODES_FILE):
        print("⚠ 'nodes' file not found")
        return nodes

    try:
        with open(NODES_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Extract address and comment
                if '#' in line:
                    parts = line.split('#', 1)
                    address = parts[0].strip()
                    comment = parts[1].strip()
                else:
                    address = line.strip()
                    comment = ""

                if address:
                    nodes.append({
                        'address': address,
                        'comment': comment,
                        'type': determine_node_type(address)
                    })

        print(f"✓ Loaded {len(nodes)} known node(s) from 'nodes' file")

        # Print nodes in one line
        if nodes:
            node_addresses = [node['address'] for node in nodes]
            print(f"  Nodes loaded from nodes file: {' '.join(node_addresses)}")

        return nodes

    except Exception as e:
        print(f"❌ Error loading nodes: {e}")
        return []


def determine_node_type(address):
    """Determine the type of node based on its address format."""
    # MAC address format (with colons)
    if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', address):
        return 'BLE'
    # MAC address without colons
    elif re.match(r'^[0-9A-Fa-f]{12}$', address):
        return 'BLE'
    # Node ID format
    elif address.startswith('!'):
        return 'NODE_ID'
    # TCP/IP format
    elif ':' in address and '.' in address:
        return 'TCP'
    # Serial port
    elif address.startswith('/dev/'):
        return 'SERIAL'
    else:
        return 'UNKNOWN'


def scan_devices():
    """Scan for available Meshtastic devices using multiple methods."""
    print("\n🔍 Scanning for Meshtastic devices...")

    devices = []

    # Method 1: BLE Scan
    print("  Scanning BLE devices...")
    ble_devices = scan_ble()
    devices.extend(ble_devices)

    # Method 2: Serial ports
    print("  Checking serial ports...")
    serial_devices = scan_serial()
    devices.extend(serial_devices)

    # Method 3: Meshtastic info
    print("  Checking auto-detected devices...")
    auto_devices = scan_auto_detected()
    devices.extend(auto_devices)

    # Remove duplicates
    unique_devices = []
    seen_addresses = set()

    for device in devices:
        addr = device.get('address', '')
        if addr and addr not in seen_addresses:
            seen_addresses.add(addr)
            unique_devices.append(device)

    print(f"\n✓ Found {len(unique_devices)} unique device(s)")
    return unique_devices


def scan_ble():
    """Scan for BLE devices."""
    devices = []

    try:
        result = subprocess.run(
            ["meshtastic", "--ble-scan", "--timeout", "5"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout:
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and line != "BLE scan finished":
                    # Extract MAC address
                    mac_pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                    match = re.search(mac_pattern, line)

                    if match:
                        address = match.group(0)
                        devices.append({
                            'address': address,
                            'type': 'BLE',
                            'info': line,
                            'method': 'BLE Scan'
                        })

    except Exception as e:
        print(f"    ⚠ BLE scan error: {e}")

    return devices


def scan_serial():
    """Scan for serial devices."""
    devices = []

    serial_ports = [
        "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3",
        "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3",
    ]

    for port in serial_ports:
        if os.path.exists(port):
            devices.append({
                'address': port,
                'type': 'SERIAL',
                'info': f"Serial port {port}",
                'method': 'Port Scan'
            })

    return devices


def scan_auto_detected():
    """Scan for auto-detected devices."""
    devices = []

    try:
        result = subprocess.run(
            ["meshtastic", "--info", "--timeout", "3"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout:
            # Parse the output for device information
            lines = result.stdout.split('\n')
            current_device = {}

            for line in lines:
                line = line.strip()
                # Use maxsplit=1 to safely handle values that contain colons (e.g. MAC addresses)
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'Connected to':
                        if current_device:
                            devices.append(current_device)
                        current_device = {
                            'address': value,
                            'type': 'AUTO',
                            'info': value,
                            'method': 'Auto-detected'
                        }

            if current_device:
                devices.append(current_device)

    except Exception as e:
        print(f"    ⚠ Auto-detect error: {e}")

    return devices


def display_devices(devices, known_nodes):
    """Display found devices in a formatted way."""
    if not devices:
        print("\n⚠ No devices found")
        return

    print("\n" + "=" * 70)
    print("FOUND DEVICES")
    print("=" * 70)

    for i, device in enumerate(devices, 1):
        address = device.get('address', 'Unknown')
        device_type = device.get('type', 'Unknown')
        info = device.get('info', '')
        method = device.get('method', 'Unknown')

        # Check if this is a known node
        is_known = any(node['address'] == address for node in known_nodes)
        known_marker = "⭐ " if is_known else "  "

        print(f"\n{known_marker}Device {i}:")
        print(f"  Type:     {device_type}")
        print(f"  Address:  {address}")
        print(f"  Method:   {method}")
        if info and info != address:
            print(f"  Info:     {info}")

        if is_known:
            # Find the comment for this node
            for node in known_nodes:
                if node['address'] == address:
                    if node['comment']:
                        print(f"  Known as: {node['comment']}")
                    break


def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 70)
    print("MESHTASTIC STATUS BOARD")
    print("=" * 70)
    print("1. Scan for devices")
    print("2. Show known nodes")
    print("3. Test connection to known nodes")
    print("4. Monitor messages")
    print("5. Check system status")
    print("6. Update nodes list")
    print("7. Send message to node every 1 min")
    print("0. Exit")
    print("=" * 70)


def show_known_nodes(nodes):
    """Display known nodes."""
    if not nodes:
        print("\n⚠ No known nodes")
        return

    print("\n" + "=" * 70)
    print("KNOWN NODES")
    print("=" * 70)

    for i, node in enumerate(nodes, 1):
        address = node['address']
        comment = node['comment']
        node_type = node['type']

        print(f"\n{i}. {address}")
        print(f"   Type:    {node_type}")
        if comment:
            print(f"   Comment: {comment}")


def test_connections(nodes):
    """Interactively test a connection: pick node, pair if needed, verify, send test message."""
    if not nodes:
        print("\n⚠ No nodes to test")
        return

    print("\n" + "=" * 70)
    print("TEST CONNECTION")
    print("=" * 70)

    print("\nSelect a node to test:")
    for i, node in enumerate(nodes, 1):
        line = f"  {i}. {node['address']}  ({node['type']})"
        if node['comment']:
            line += f"  # {node['comment']}"
        print(line)
    print("  a. Test all nodes")

    selection = input("\nSelect (number or 'a'): ").strip().lower()

    if selection == 'a':
        nodes_to_test = nodes
    else:
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(nodes):
                nodes_to_test = [nodes[idx]]
            else:
                print(f"⚠ Please enter 1-{len(nodes)} or 'a'")
                return
        except ValueError:
            print("⚠ Invalid selection")
            return

    successful = 0
    for node in nodes_to_test:
        if _test_single_node(node):
            successful += 1

    if len(nodes_to_test) > 1:
        print(f"\n📊 Results: {successful}/{len(nodes_to_test)} successful connections")


def _test_single_node(node):
    """Run meshtastic --info, showing a BLE scan progress bar, then print all output."""
    address = node['address']
    comment = node['comment']
    node_type = node['type']

    print(f"\n{'─' * 50}")
    print(f"Node : {address}")
    if comment:
        print(f"Info : {comment}")
    print(f"Type : {node_type}")
    print("─" * 50)

    if node_type == 'BLE':
        cmd = ["meshtastic", "--ble", address, "--info"]
    elif node_type == 'SERIAL':
        cmd = ["meshtastic", "--port", address, "--info"]
    else:
        cmd = ["meshtastic", "--info"]

    print(f"\n$ {' '.join(cmd)}\n")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Drain output in background so the pipe never fills and blocks meshtastic
        collected = []
        def _read():
            for line in proc.stdout:
                collected.append(line)
        reader = threading.Thread(target=_read, daemon=True)
        reader.start()

        # Progress bar covers the ~10 s BLE scan phase
        if node_type == 'BLE':
            bar_width = 40
            scan_secs = 10
            start = time.time()
            while proc.poll() is None:
                elapsed = time.time() - start
                if elapsed >= scan_secs:
                    break
                filled = int(bar_width * elapsed / scan_secs)
                bar = '█' * filled + '░' * (bar_width - filled)
                print(f"\r  Scanning for Nodes [{bar}] {int(elapsed)}s / {scan_secs}s",
                      end='', flush=True)
                time.sleep(0.1)
            elapsed = time.time() - start
            print(f"\r  Scanning BLE [{'█' * bar_width}] {elapsed:.1f}s        \n")

        proc.wait()
        reader.join(timeout=10)

        print(''.join(collected), end='')
        return proc.returncode == 0

    except KeyboardInterrupt:
        try:
            proc.terminate()
            proc.wait()
        except Exception:
            pass
        print("\nStopped.")
        return False
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        return False


def test_ble_connection_with_pairing(address):
    """BLE connection check used by send_to_node_every_minute."""
    cmd = ["meshtastic", "--ble", address, "--info"]
    print(f"\n$ {' '.join(cmd)}\n")
    try:
        result = subprocess.run(cmd, timeout=60)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("\n⚠ Command timed out after 60 s")
        return False
    except Exception as e:
        print(f"\n⚠ Error: {e}")
        return False


def check_system_status():
    """Check system status and Meshtastic installation."""
    print("\n🖥️ System Status Check")
    print("=" * 40)

    # Check Meshtastic CLI
    try:
        result = subprocess.run(
            ["which", "meshtastic"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Meshtastic CLI installed")

            version_result = subprocess.run(
                ["meshtastic", "--version"],
                capture_output=True,
                text=True
            )
            if version_result.returncode == 0:
                print(f"  Version: {version_result.stdout.strip()}")
        else:
            print("✗ Meshtastic CLI not found in PATH")
    except Exception as e:
        print(f"⚠ Error checking Meshtastic CLI: {e}")

    # Check Bluetooth
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "bluetooth"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Bluetooth service is active")
        else:
            print("✗ Bluetooth service is not active")
    except Exception:
        print("⚠ Could not check Bluetooth status")

    # Check Python packages
    try:
        import importlib.metadata
        packages = ['meshtastic', 'pyserial', 'requests', 'tabulate', 'pyyaml']

        print("\n📦 Python Packages:")
        for pkg in packages:
            try:
                version = importlib.metadata.version(pkg)
                print(f"  ✓ {pkg}: {version}")
            except importlib.metadata.PackageNotFoundError:
                print(f"  ✗ {pkg}: Not installed")
    except Exception as e:
        print(f"⚠ Error checking packages: {e}")


def update_nodes_list(devices):
    """Update the nodes file with discovered devices."""
    if not devices:
        print("\n⚠ No devices to add to nodes list")
        return

    print("\n📝 Updating nodes list...")

    # Load existing nodes
    existing_nodes = load_nodes()
    existing_addresses = {node['address'] for node in existing_nodes}

    new_nodes = []
    for device in devices:
        address = device.get('address', '')
        if address and address not in existing_addresses:
            new_nodes.append({
                'address': address,
                'comment': f"Discovered on {datetime.now().strftime('%Y-%m-%d')}",
                'type': device.get('type', 'UNKNOWN')
            })

    if not new_nodes:
        print("✓ No new devices to add")
        return

    # Append new nodes to file
    try:
        with open(NODES_FILE, 'a') as f:
            f.write("\n# Automatically added devices\n")
            for node in new_nodes:
                line = f"{node['address']}  # {node['comment']}\n"
                f.write(line)

        print(f"✓ Added {len(new_nodes)} new device(s) to 'nodes' file")
        for node in new_nodes:
            print(f"  - {node['address']}")

    except Exception as e:
        print(f"❌ Error updating nodes file: {e}")


def send_to_node_every_minute():
    """Send a message to a selected node every 1 minute with detailed debugging."""
    print("\n📨 Message Scheduler")
    print("=" * 50)

    # Step 1: Ask user which node to use
    print("\n1️⃣  SELECT NODE")
    print("-" * 30)

    # Load known nodes
    known_nodes = load_nodes()

    if not known_nodes:
        print("⚠ No known nodes found")
        print("Please add nodes to your 'nodes' file first")
        return

    # Display nodes with numbers
    print("Choose a node to send TO:")
    for i, node in enumerate(known_nodes, 1):
        print(f"  {i}. {node['address']}", end="")
        if node['comment']:
            print(f"  # {node['comment']}")
        else:
            print()

    print("  s. Scan for connected devices")
    print("  m. Manually enter node address")

    # Get user selection
    selected_node = None
    while True:
        selection = input("\nSelect node (number, 's', or 'm'): ").strip().lower()

        if selection == 's':
            # Scan for connected devices
            print("\n🔍 Scanning for connected devices...")
            devices = scan_devices()
            if not devices:
                print("⚠ No devices found. Using known nodes instead.")
                continue

            # Display found devices
            print("\nFound devices:")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device['address']} ({device['type']})")

            device_choice = input("Select device (number): ").strip()
            try:
                idx = int(device_choice) - 1
                if 0 <= idx < len(devices):
                    selected_node = {
                        'address': devices[idx]['address'],
                        'type': devices[idx]['type'],
                        'comment': 'Discovered device'
                    }
                    break
                else:
                    print("⚠ Invalid selection")
            except ValueError:
                print("⚠ Please enter a number")

        elif selection == 'm':
            # Manually enter node address
            address = input("Enter node address: ").strip()
            if address:
                selected_node = {
                    'address': address,
                    'type': determine_node_type(address),
                    'comment': 'Manual entry'
                }
                break
            else:
                print("⚠ Address cannot be empty")

        else:
            # Select from known nodes
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(known_nodes):
                    selected_node = known_nodes[idx]
                    break
                else:
                    print(f"⚠ Please enter 1-{len(known_nodes)}, 's', or 'm'")
            except ValueError:
                print(f"⚠ Please enter 1-{len(known_nodes)}, 's', or 'm'")

    print(f"\n✅ Selected node: {selected_node['address']}")
    if selected_node['comment']:
        print(f"   Comment: {selected_node['comment']}")
    print(f"   Type: {selected_node['type']}")

    # Step 2: Connect to node and show connection status
    print("\n2️⃣  CONNECTION TEST")
    print("-" * 30)

    print(f"Testing connection to {selected_node['address']}...")

    connection_successful = False

    if selected_node['type'] == 'BLE':
        connection_successful = test_ble_connection_with_pairing(selected_node['address'])
    else:
        try:
            if selected_node['type'] == 'SERIAL':
                result = subprocess.run(
                    ["meshtastic", "--port", selected_node['address'], "--info", "--timeout", "5"],
                    capture_output=True,
                    text=True,
                    timeout=7
                )
            else:
                result = subprocess.run(
                    ["meshtastic", "--info", "--timeout", "5"],
                    capture_output=True,
                    text=True,
                    timeout=7
                )

            if result.returncode == 0:
                print(f"  ✅ Connection successful")
                connection_successful = True

                print("  📊 Connection details:")
                lines = result.stdout.split('\n')
                for line in lines[:10]:
                    if line.strip():
                        print(f"     {line.strip()}")
                if len(lines) > 10:
                    print(f"     ... and {len(lines) - 10} more lines")
            else:
                print(f"  ❌ Connection failed")
                if result.stderr:
                    print("  🔍 Error details:")
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines[:5]:
                        if line.strip():
                            print(f"     {line.strip()}")

        except subprocess.TimeoutExpired:
            print(f"  ⚠ Connection timed out")
        except Exception as e:
            print(f"  ⚠ Error: {str(e)}")

    if not connection_successful:
        print("\n⚠ Connection test failed")
        proceed = input("Proceed anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            return

    # Step 3: Get message details
    print("\n3️⃣  MESSAGE SETUP")
    print("-" * 30)

    print("\n💬 Enter the message to send (or press Enter for default):")
    default_message = f"Hello from Meshtastic Status Board to {selected_node['address']}"
    user_message = input(f"Message [default: '{default_message}']: ").strip()

    if not user_message:
        user_message = default_message

    print("\n⏰ How many minutes should I send messages?")
    print("   Enter number of minutes (0 for infinite, Ctrl+C to stop):")

    try:
        minutes_input = input("Minutes [default: 5]: ").strip()
        if not minutes_input:
            minutes = 5
        else:
            minutes = int(minutes_input)
            if minutes < 0:
                print("⚠ Negative value not allowed, using default: 5 minutes")
                minutes = 5
    except ValueError:
        print("⚠ Invalid input, using default: 5 minutes")
        minutes = 5

    # Summary
    print("\n📋 SCHEDULE SUMMARY")
    print("-" * 30)
    print(f"   Node: {selected_node['address']}")
    print(f"   Type: {selected_node['type']}")
    if selected_node['comment']:
        print(f"   Info: {selected_node['comment']}")
    print(f"   Message: '{user_message}'")
    if minutes == 0:
        print(f"   Duration: Infinite (until Ctrl+C)")
    else:
        print(f"   Duration: {minutes} minute(s)")
    print(f"   Interval: Every 1 minute")

    confirm = input("\nStart message scheduler? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return

    if minutes == 0:
        print("\n🔄 Starting infinite message loop (press Ctrl+C to stop)")
    else:
        print(f"\n🔄 Sending messages for {minutes} minute(s)")

    # Step 4: Start sending messages with detailed debugging
    print("\n4️⃣  MESSAGE SENDING")
    print("-" * 30)

    message_count = 0   # successful sends
    attempt_count = 0   # total attempts (used for loop limit)
    # Initialise before try so the finally block can always reference it
    start_time = time.time()

    try:
        while True:
            if minutes > 0 and attempt_count >= minutes:
                print(f"\n✅ Completed {attempt_count} attempt(s), {message_count} sent successfully")
                break

            # Prepare message with timestamp
            current_time = time.strftime("%H:%M:%S")
            full_message = f"{user_message} - {current_time}"

            print(f"\n📤 Message #{attempt_count + 1} at {current_time}")
            print(f"   To: {selected_node['address']}")
            print(f"   Content: '{full_message}'")

            # Send message with detailed debugging
            try:
                print("   🔧 Sending process:")

                # Build command based on node type
                if selected_node['type'] == 'BLE':
                    cmd = ["meshtastic", "--ble", selected_node['address'], "--sendtext", full_message]
                    print(f"      Command: meshtastic --ble {selected_node['address']} --sendtext '{full_message}'")
                elif selected_node['type'] == 'SERIAL':
                    cmd = ["meshtastic", "--port", selected_node['address'], "--sendtext", full_message]
                    print(f"      Command: meshtastic --port {selected_node['address']} --sendtext '{full_message}'")
                else:
                    cmd = ["meshtastic", "--sendtext", full_message]
                    print(f"      Command: meshtastic --sendtext '{full_message}'")

                print("      Executing...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                print("      Command completed")
                print(f"      Return code: {result.returncode}")

                if result.returncode == 0:
                    print(f"   ✅ Message sent successfully")
                    message_count += 1
                    attempt_count += 1

                    if result.stdout.strip():
                        print("      Output:")
                        for line in result.stdout.strip().split('\n'):
                            if line.strip():
                                print(f"        {line.strip()}")
                else:
                    print(f"   ❌ Failed to send message")
                    attempt_count += 1

                    if result.stderr.strip():
                        print("      Error output:")
                        error_lines = result.stderr.strip().split('\n')
                        for line in error_lines[:10]:
                            if line.strip():
                                print(f"        {line.strip()}")
                        if len(error_lines) > 10:
                            print(f"        ... and {len(error_lines) - 10} more error lines")

                    if result.stdout.strip():
                        print("      Standard output:")
                        for line in result.stdout.strip().split('\n')[:5]:
                            if line.strip():
                                print(f"        {line.strip()}")

            except subprocess.TimeoutExpired:
                print(f"   ⚠ Sending timed out after 15 seconds")
                print("      Possible issues:")
                print("      - Device not responding")
                print("      - Connection lost")
                print("      - Bluetooth pairing required")
                attempt_count += 1
            except Exception as e:
                print(f"   ⚠ Unexpected error: {str(e)}")
                print(f"      Error type: {type(e).__name__}")
                attempt_count += 1

            # Wait for 1 minute before next message
            if minutes == 0 or attempt_count < minutes:
                print(f"\n   ⏳ Waiting 1 minute for next message...")
                wait_start = time.time()
                for i in range(60, 0, -1):
                    time.sleep(1)
                    if i % 10 == 0:
                        elapsed = time.time() - wait_start
                        print(f"      {i} seconds remaining (elapsed: {elapsed:.1f}s)", end='\r')
                print(" " * 60, end='\r')  # Clear line

    except KeyboardInterrupt:
        elapsed_time = time.time() - start_time
        print(f"\n\n👋 Stopped by user after {attempt_count} attempt(s), {message_count} sent successfully")
        print(f"   Total time: {elapsed_time:.1f} seconds")
        print(f"   Average interval: {elapsed_time / max(attempt_count, 1):.1f} seconds per attempt")

    except Exception as e:
        print(f"\n💥 Error in message scheduler: {e}")
        import traceback
        print("Traceback:")
        traceback.print_exc()

    finally:
        print("\n📨 Message scheduler stopped")
        print(f"   Total attempts: {attempt_count}, successfully sent: {message_count}")
        if attempt_count > 0:
            total_time = time.time() - start_time
            print(f"   Total time: {total_time:.1f} seconds")
            print(f"   Average: {total_time / attempt_count:.1f} seconds per attempt")


def main():
    """Main application function."""
    print("\n🚀 Starting Meshtastic Status Board")
    print("=" * 40)

    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please run setup.sh first")
        return

    # Load known nodes
    known_nodes = load_nodes()

    while True:
        display_menu()

        try:
            choice = input("\nSelect option (0-7): ").strip()

            if choice == '0':
                print("\n👋 Goodbye!")
                break

            elif choice == '1':
                devices = scan_devices()
                display_devices(devices, known_nodes)

                if devices:
                    add_choice = input("\nAdd devices to known nodes? (y/N): ").strip().lower()
                    if add_choice == 'y':
                        update_nodes_list(devices)
                        # Reload known nodes
                        known_nodes = load_nodes()

            elif choice == '2':
                show_known_nodes(known_nodes)

            elif choice == '3':
                test_connections(known_nodes)

            elif choice == '4':
                # TODO: Implement live message monitoring via meshtastic --export-config or a listener
                print("\n📡 Message monitoring is not yet implemented.")
                print("   As a workaround, run the meshtastic CLI directly:")
                print("   meshtastic --listen")

            elif choice == '5':
                check_system_status()

            elif choice == '6':
                devices = scan_devices()
                update_nodes_list(devices)
                # Reload known nodes
                known_nodes = load_nodes()

            elif choice == '7':
                send_to_node_every_minute()

            else:
                print("⚠ Invalid choice. Please enter 0-7")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            break
        except EOFError:
            print("\n\n👋 No input available. Exiting...")
            break
        except Exception as e:
            print(f"\n⚠ Error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)