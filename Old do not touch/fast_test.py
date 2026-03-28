#!/home/wdr/.local/share/pipx/venvs/meshtastic/bin/python3

import subprocess
import signal
import sys

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException()

def test_node_with_timeout(node, timeout=2):
    """Teste eine Node mit Timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        result = subprocess.run(
            ["meshtastic", "--ble", node, "--info", "--timeout", str(timeout)],
            capture_output=True,
            text=True
        )
        signal.alarm(0)  # Timeout zurücksetzen
        return result
    except TimeoutException:
        print(f"  ⏰ Timeout nach {timeout} Sekunden")
        return None
    except Exception as e:
        signal.alarm(0)
        print(f"  ⚠ Ausnahme: {type(e).__name__}: {str(e)[:50]}...")
        return None

print("Schneller Nodes-Test...")

# Lade Nodes
nodes = []
try:
    with open('nodes', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '#' in line:
                address = line.split('#')[0].strip()
            else:
                address = line.strip()
            if address:
                nodes.append(address)
    print(f"Gefundene Nodes: {nodes}")
except Exception as e:
    print(f"Fehler: {e}")
    nodes = []

# Teste jede Node
for node in nodes:
    print(f"\nTeste Node: {node}")
    result = test_node_with_timeout(node, 2)
    
    if result is None:
        print(f"  ❌ Timeout oder Fehler")
    elif result.returncode == 0:
        print(f"  ✅ Erfolg!")
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines[:3]:  # Zeige nur erste 3 Zeilen
                if line:
                    print(f"    {line}")
    else:
        print(f"  ❌ Fehlgeschlagen (Code: {result.returncode})")
        if result.stderr:
            error = result.stderr.strip()
            if error:
                print(f"    Fehler: {error[:80]}...")

print("\n✅ Test abgeschlossen")