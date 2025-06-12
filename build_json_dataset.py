import os
import sys
import json
import importlib.util

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def serialize_function_call(fc):
    return {
        "name": fc.name,
        "arguments": {
            k: {
                "name": v.name,
                "value": v.value,
                "excluded_values": v.excluded_values,
                "type": v.type,
            }
            for k, v in fc.arguments.items()
        },
    }

def serialize_transition(t):
    return {
        "symbols": t.symbols,
        "from": t._from.name,
        "to": t._to.name,
    }

def serialize_node(n):
    return {
        "name": n.name,
        "is_final": getattr(n, "is_final", False),
        "transitions": [serialize_transition(t) for t in getattr(n, "transitions", [])],
    }

def process_file(filepath, world_name, prompt_name):
    spec = importlib.util.spec_from_file_location(prompt_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    nodes = [v for v in vars(module).values() if hasattr(v, "transitions")]
    alphabet = getattr(module, "alphabet", {})

    return {
        "world": world_name,
        "prompt_name": prompt_name,
        "nodes": [serialize_node(n) for n in nodes],
        "alphabet": {k: serialize_function_call(fc) for k, fc in alphabet.items()},
    }

def build_dataset(root_dir, output_file):
    dataset = []

    for world in os.listdir(root_dir):
        world_path = os.path.join(root_dir, world)
        if not os.path.isdir(world_path) or world.startswith("__"):
            continue  

        for file in os.listdir(world_path):
            if not file.endswith(".py") or file.startswith("__"):
                continue

            filepath = os.path.join(world_path, file)
            prompt_name = os.path.splitext(file)[0]
            try:
                entry = process_file(filepath, world_name=world, prompt_name=prompt_name)
                dataset.append(entry)
            except Exception as e:
                print(f"Failed to process {file} in {world}: {e}")

    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=2)

if __name__ == "__main__":
    build_dataset("dfas", "all_worlds_dataset.json")
