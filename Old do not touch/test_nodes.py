#!/home/wdr/.local/share/pipx/venvs/meshtastic/bin/python3

print("Teste Nodes-Verbindungen...")

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
    try:
        import subprocess
        print(f"  Führe Befehl aus: meshtastic --ble {node} --info --timeout 3")
        result = subprocess.run(
            ["meshtastic", "--ble", node, "--info", "--timeout", "3"],
            capture_output=True,
            text=True
        )
        
        print(f"  Return Code: {result.returncode}")
        if result.returncode == 0:
            print(f"  ✅ Erfolg!")
            if result.stdout:
                print(f"  Ausgabe: {result.stdout[:100]}...")
        else:
            print(f"  ❌ Fehlgeschlagen")
            if result.stderr:
                print(f"  Fehler: {result.stderr[:100]}...")
                
    except Exception as e:
        print(f"  ⚠ Ausnahme: {type(e).__name__}: {str(e)[:50]}...")

print("\n✅ Test abgeschlossen")