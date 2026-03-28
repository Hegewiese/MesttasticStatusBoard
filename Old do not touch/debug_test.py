#!/home/wdr/.local/share/pipx/venvs/meshtastic/bin/python3

print("DEBUG Test...")

# Test der load_nodes_from_file Funktion
def load_nodes_from_file(filename="nodes"):
    """Lädt Node-Adressen aus einer Datei."""
    nodes = []
    
    import os
    if not os.path.exists(filename):
        print(f"⚠ Datei '{filename}' nicht gefunden")
        return nodes
    
    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Überspringe leere Zeilen und Kommentare
                if not line or line.startswith('#'):
                    print(f"   Zeile {line_num}: Übersprungen - '{line}'")
                    continue
                
                # Trenne Adresse und Kommentar
                if '#' in line:
                    address = line.split('#')[0].strip()
                else:
                    address = line.strip()
                
                if address:
                    nodes.append(address)
                    print(f"   Zeile {line_num}: Gefunden - '{address}'")
                
        print(f"✅ {len(nodes)} Node(s) aus '{filename}' geladen")
        return nodes
        
    except Exception as e:
        print(f"❌ Fehler beim Lesen von '{filename}': {e}")
        return []

# Test ausführen
print("\nTeste load_nodes_from_file:")
nodes = load_nodes_from_file()
print(f"\nGefundene Nodes: {nodes}")

# Test BLE-Scan
print("\n\nTeste BLE-Scan (kurz):")
try:
    import subprocess
    result = subprocess.run(
        ["meshtastic", "--ble-scan", "--timeout", "2"],
        capture_output=True,
        text=True
    )
    print(f"Return Code: {result.returncode}")
    print(f"Stdout: {result.stdout[:100]}..." if len(result.stdout) > 100 else f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr[:100]}..." if result.stderr else "Stderr: (leer)")
except Exception as e:
    print(f"Fehler: {e}")

print("\n✅ Debug Test abgeschlossen")