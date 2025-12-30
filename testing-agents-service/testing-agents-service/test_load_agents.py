"""Test script to diagnose why some agents are not loading."""
import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load graph.json
config_path = Path(__file__).parent / "graph.json"
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
    graphs = config.get("graphs", {})

print("=" * 60)
print("Testing Agent Loading")
print("=" * 60)

for graph_id, graph_config in graphs.items():
    print(f"\n{graph_id}:")
    print(f"  Path: {graph_config['path']}")
    
    # Parse path
    path_parts = graph_config['path'].split(':')
    if len(path_parts) != 2:
        print(f"  ❌ Invalid path format")
        continue
    
    file_path = path_parts[0].lstrip('./')
    variable_name = path_parts[1]
    
    full_path = Path(__file__).parent / file_path
    print(f"  Full path: {full_path}")
    print(f"  File exists: {full_path.exists()}")
    print(f"  Variable: {variable_name}")
    
    # Try to import
    try:
        # Convert path to module name
        module_path = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        
        print(f"  Importing: {module_path}")
        module = __import__(module_path, fromlist=[variable_name])
        
        if hasattr(module, variable_name):
            agent = getattr(module, variable_name)
            print(f"  [OK] Successfully loaded agent: {type(agent).__name__}")
        else:
            print(f"  [FAIL] Module does not have variable '{variable_name}'")
            print(f"     Available: {[x for x in dir(module) if not x.startswith('_')]}")
    except Exception as e:
        print(f"  [FAIL] Error loading: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)

