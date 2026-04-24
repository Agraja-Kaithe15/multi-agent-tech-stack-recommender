import json
from pathlib import Path

def tech_catalog_tool():
    file_path = Path(__file__).resolve().parent.parent / "data" / "tech_stack.json"
    
    with open(file_path, "r") as file:
        return json.load(file)