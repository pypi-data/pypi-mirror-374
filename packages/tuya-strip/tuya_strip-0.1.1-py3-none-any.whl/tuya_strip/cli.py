import tinytuya
import argparse
import sys
import json
import os
import time
import socket
from pathlib import Path
from dotenv import load_dotenv


def load_config():
    """Load configuration from various locations."""
    # Try loading from multiple locations in order of priority
    config_locations = [
        Path.cwd() / ".env",  # Current directory
        Path.home() / ".tuya-strip",  # Home directory config file
        Path.home() / ".env",  # Home directory .env
    ]
    
    for config_path in config_locations:
        if config_path.exists():
            print(f"Loading config from: {config_path}")
            load_dotenv(config_path)
            break
    else:
        # If no config file found, just try to load from environment
        load_dotenv()
    
    return {
        "DEVICE_ID": os.getenv("TUYA_DEVICE_ID"),
        "DEVICE_IP": os.getenv("TUYA_DEVICE_IP"), 
        "LOCAL_KEY": os.getenv("TUYA_LOCAL_KEY"),
        "VERSION": float(os.getenv("TUYA_VERSION", "3.3"))
    }


def setup_config():
    """Interactive setup for device credentials."""
    print("Tuya Device Setup")
    print("================")
    print("Please enter your Tuya device credentials:")
    print()
    
    device_id = input("Device ID: ").strip()
    device_ip = input("Device IP: ").strip()
    local_key = input("Local Key: ").strip()
    version = input("Version (default 3.3): ").strip() or "3.3"
    
    config_content = f"""# Tuya device configuration
TUYA_DEVICE_ID={device_id}
TUYA_DEVICE_IP={device_ip}
TUYA_LOCAL_KEY={local_key}
TUYA_VERSION={version}
"""
    
    # Save to home directory
    config_path = Path.home() / ".tuya-strip"
    config_path.write_text(config_content)
    
    print(f"\nConfiguration saved to: {config_path}")
    print("You can now use the tuya-strip commands!")


def run_with_retry(action, retries=3, delay=1):
    """Run a device action with retries and error handling."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return action()
        except socket.timeout:
            last_error = "Device connection timed out - device may be unreachable"
            print(f"Attempt {attempt} failed: {last_error}")
            if attempt < retries:
                time.sleep(delay)
        except ConnectionRefusedError:
            last_error = "Connection refused - device may be offline or wrong IP address"
            print(f"Attempt {attempt} failed: {last_error}")
            if attempt < retries:
                time.sleep(delay)
        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    print(f"All {retries} attempts failed. Last error: {last_error}")
    sys.exit(1)


def do_status(d):
    data = d.status()
    
    # Check for error responses
    if 'Error' in data:
        raise Exception(f"Device error: {data['Error']} (Code: {data.get('Err', 'Unknown')})")
    
    switches = {k: v for k, v in data.get("dps", {}).items() if k in ["1", "2", "3"]}
    energy = {
        "voltage_V": data.get("dps", {}).get("20"),
        "current_mA": data.get("dps", {}).get("18"),
        "power_W": data.get("dps", {}).get("19"),
    }
    print("Switches:", switches)
    print("Energy:", energy)


def do_on(d, num):
    result = d.set_status(True, num)
    
    # Check for error responses
    if 'Error' in result:
        raise Exception(f"Device error: {result['Error']} (Code: {result.get('Err', 'Unknown')})")
        
    print(f"Plug {num} turned ON")


def do_off(d, num):
    result = d.set_status(False, num)
    
    # Check for error responses
    if 'Error' in result:
        raise Exception(f"Device error: {result['Error']} (Code: {result.get('Err', 'Unknown')})")
        
    print(f"Plug {num} turned OFF")


def main():
    # CLI args
    parser = argparse.ArgumentParser(description="Control Tuya 3-way power strip over LAN")
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Connection timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries on failure (default: 3)"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Setup command
    subparsers.add_parser("setup", help="Setup device credentials")

    on_parser = subparsers.add_parser("on", help="Turn a plug on")
    on_parser.add_argument("plug", type=int, help="Plug number (1-3)")

    off_parser = subparsers.add_parser("off", help="Turn a plug off")
    off_parser.add_argument("plug", type=int, help="Plug number (1-3)")

    subparsers.add_parser("status", help="Show device status")

    args = parser.parse_args()

    # Handle setup command
    if args.command == "setup":
        setup_config()
        return

    # Load credentials
    config = load_config()
    DEVICE_ID = config["DEVICE_ID"]
    DEVICE_IP = config["DEVICE_IP"]
    LOCAL_KEY = config["LOCAL_KEY"]
    VERSION = config["VERSION"]

    if not all([DEVICE_ID, DEVICE_IP, LOCAL_KEY]):
        print("Missing credentials. Please run 'tuya-strip setup' to configure your device.")
        sys.exit(1)

    # Init device
    d = tinytuya.OutletDevice(
        DEVICE_ID,
        DEVICE_IP,
        LOCAL_KEY,
        connection_timeout=args.timeout
    )
    d.set_version(VERSION)

    # Run command
    if args.command == "on":
        run_with_retry(lambda: do_on(d, args.plug), retries=args.retries)
    elif args.command == "off":
        run_with_retry(lambda: do_off(d, args.plug), retries=args.retries)
    elif args.command == "status":
        run_with_retry(lambda: do_status(d), retries=args.retries)
    else:
        parser.print_help()
        sys.exit(1)
