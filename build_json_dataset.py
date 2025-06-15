import os
import sys
import json
import importlib.util
import importlib
from typing import Any

SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

def snake_to_pascal(name: str) -> str:
    return ''.join(word.capitalize() for word in name.split('_'))

def serialize_function_call(fc: Any) -> dict:
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

def serialize_transition(t: Any) -> dict:
    return {
        "symbols": t.symbols,
        "from": t._from.name,
        "to": t._to.name,
    }

def serialize_node(n: Any) -> dict:
    return {
        "name": n.name,
        "is_final": getattr(n, "is_final", False),
        "transitions": [serialize_transition(t) for t in getattr(n, "transitions", [])],
    }

# Special-case overrides: filename (no .py) -> actual class name
# Manual overrides for class names that do not match PascalCase of filename
WORLD_CLASS_OVERRIDES = {
    "crud": "CRUD",
    "computations": "Maths",
}

# Files to explicitly skip in the 'worlds' directory
SKIP_WORLD_FILES = {"__init__.py", "world.py"}

def load_prompt_map(worlds_dir: str = "worlds") -> dict[str, list[str]]:
    prompt_map = {}
    worlds_path = os.path.join(PROJECT_ROOT, worlds_dir)

    for file in os.listdir(worlds_path):
        if not file.endswith(".py") or file in SKIP_WORLD_FILES:
            continue

        module_name = os.path.splitext(file)[0]
        class_name = WORLD_CLASS_OVERRIDES.get(module_name, snake_to_pascal(module_name))

        try:
            full_module = f"{worlds_dir}.{module_name}".replace("/", ".")
            module = importlib.import_module(full_module)
            world_class = getattr(module, class_name)
            world_instance = world_class()
            prompt_map[module_name] = [p["prompt"] for p in world_instance.prompts]
        except Exception as e:
            print(f"❌ Failed to load prompts from {file}: {e}")
    return prompt_map



def process_file(filepath: str, world_name: str, prompt_name: str, prompt_text: str) -> dict:
    spec = importlib.util.spec_from_file_location(prompt_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    nodes = [v for v in vars(module).values() if hasattr(v, "transitions")]
    alphabet = getattr(module, "alphabet", {})

    return {
        "prompt_id": prompt_name,
        "world": world_name,
        "prompt": prompt_text,
        "nodes": [serialize_node(n) for n in nodes],
        "alphabet": {k: serialize_function_call(fc) for k, fc in alphabet.items()},
    }

def build_dataset(root_dir: str, output_file: str, worlds_dir: str = "worlds"):
    dataset = []
    prompt_map = load_prompt_map(worlds_dir)

    for world in os.listdir(root_dir):
        world_path = os.path.join(root_dir, world)
        if not os.path.isdir(world_path) or world.startswith("__"):
            continue

        for file in sorted(os.listdir(world_path)):
            if not file.endswith(".py") or file.startswith("__"):
                continue

            filepath = os.path.join(world_path, file)
            prompt_name = os.path.splitext(file)[0]
            try:
                idx = int(prompt_name.split("_")[-1]) - 1
                world_key = world.lower()
                prompt_text = prompt_map.get(world_key, [])[idx]
                entry = process_file(filepath, world_name=world, prompt_name=prompt_name, prompt_text=prompt_text)
                dataset.append(entry)
            except Exception as e:
                print(f"❌ Failed to process {file} in {world}: {e}")

    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=2)

if __name__ == "__main__":
    dfas_path = os.path.join(PROJECT_ROOT, "dfas")
    output_path = os.path.join(PROJECT_ROOT, "all_worlds_dataset.json")
    build_dataset(dfas_path, output_path)
