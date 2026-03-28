#!/usr/bin/env python3
"""
connectAndSendNews.py - Initialization and connection script for Meshtastic
Checks for required installations and provides status information.
"""

import sys
import subprocess
import importlib.util
import importlib.metadata
import os


def check_virtual_environment():
    """Check if running in a virtual environment."""
    in_venv = sys.prefix != sys.base_prefix

    if in_venv:
        print(f"✓ Running in virtual environment")
        print(f"  Python executable: {sys.executable}")
        print(f"  Virtual environment path: {sys.prefix}")
        if 'venv' in sys.prefix:
            print(f"  This appears to be the local 'venv' directory")
        return True
    else:
        print("✗ Not running in a virtual environment")
        print("  Consider creating one with: python3 -m venv venv")
        return False


def check_python_version():
    """Check if Python is installed and get version."""
    try:
        version = sys.version_info
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is installed")
        return True
    except Exception as e:
        print(f"✗ Error checking Python version: {e}")
        return False


def check_meshtastic_installation():
    """Check if Meshtastic Python module is installed."""
    # Simple approach: just try to import it
    try:
        import meshtastic
        
        # Get version
        version = getattr(meshtastic, '__version__', 'unknown')
        
        # Also try importlib.metadata for better version info
        try:
            import importlib.metadata
            version = importlib.metadata.version("meshtastic")
        except Exception:
            pass  # Keep the version from getattr
        
        print(f"✓ Meshtastic Python module is installed (version: {version})")
        return True
    except ImportError:
        print("✗ Meshtastic Python module is NOT installed")
        print("  Install it with: pip install meshtastic")
        return False
    except Exception as e:
        print(f"✗ Error checking Meshtastic installation: {e}")
        return False


def check_meshtastic_cli():
    """Check if Meshtastic CLI tool is installed."""
    try:
        result = subprocess.run(
            ['which', 'meshtastic'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            cli_path = result.stdout.strip()
            version_result = subprocess.run(
                ['meshtastic', '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            print(f"✓ Meshtastic CLI tool is installed at: {cli_path}")
            if version_result.returncode == 0:
                print(f"  Version: {version_result.stdout.strip()}")
            else:
                print(f"  (Could not determine version)")
            return True
        else:
            print("✗ Meshtastic CLI tool is NOT installed in PATH")
            return False
    except Exception as e:
        print(f"✗ Error checking Meshtastic CLI: {e}")
        return False


def check_system_commands():
    """Check if system commands are available."""
    for cmd in ['python3', 'pip3']:
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"✓ {cmd} is available at: {result.stdout.strip()}")
            else:
                print(f"✗ {cmd} is NOT available in PATH")
        except Exception as e:
            print(f"✗ Error checking {cmd}: {e}")


def check_local_venv():
    """Check if local venv directory exists."""
    if os.path.exists("venv"):
        print("✓ Local 'venv' directory exists")
        if os.path.exists("venv/bin/python3"):
            print("  Contains valid Python executable")
        if os.path.exists("venv/bin/activate"):
            print("  Contains activation script")
        return True
    else:
        print("✗ Local 'venv' directory does not exist")
        print("  Create it with: python3 -m venv venv")
        return False


def main():
    """Main function to run all checks."""
    print("=" * 60)
    print("Meshtastic Installation Check")
    print("=" * 60)

    print("\n0. Checking virtual environment status...")
    venv_active = check_virtual_environment()

    print("\n1. Checking local venv directory...")
    local_venv_exists = check_local_venv()

    print("\n2. Checking Python installation...")
    python_ok = check_python_version()

    print("\n3. Checking system commands...")
    check_system_commands()

    print("\n4. Checking Meshtastic CLI tool...")
    meshtastic_cli_ok = check_meshtastic_cli()

    print("\n5. Checking Meshtastic Python module...")
    meshtastic_py_ok = check_meshtastic_installation()

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)

    requirements_met = []
    if python_ok:
        requirements_met.append("Python")
    if meshtastic_cli_ok:
        requirements_met.append("Meshtastic CLI tool")
    if meshtastic_py_ok:
        requirements_met.append("Meshtastic Python module")

    if requirements_met:
        print("✓ The following requirements are met:")
        for req in requirements_met:
            print(f"  - {req}")

    missing = []
    if not python_ok:
        missing.append("Python is not properly installed")
    if not meshtastic_py_ok:
        missing.append("Meshtastic Python module is not installed")

    if missing:
        print("\n✗ The following requirements are missing:")
        for req in missing:
            print(f"  - {req}")

        if local_venv_exists and not venv_active:
            print("\n💡 You have a local 'venv' directory but it's not active!")
            print("  Activate it with: source venv/bin/activate")
            print("  Then install Meshtastic: pip install meshtastic")
        elif not local_venv_exists:
            print("\n💡 Consider creating a virtual environment:")
            print("  python3 -m venv venv")
            print("  source venv/bin/activate")
            print("  pip install meshtastic")
        else:
            print("\nTo install Meshtastic Python module, run:")
            print("  pip install meshtastic")
    else:
        print("\n✓ All requirements are met. Ready to connect to Meshtastic!")

    print("\nNote: The Meshtastic CLI tool and Python module are separate.")
    print("The CLI tool is for command-line operations,")
    print("while the Python module is for programmatic access.")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()