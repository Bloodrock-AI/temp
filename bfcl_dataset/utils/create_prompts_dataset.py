#!/usr/bin/env python3
"""
prepare_bfcl.py  –  merge prompts, answers & worlds  (final-final)
──────────────────────────────────────────────────────────────────
Creates a flat JSON-Lines dataset for LLM function-calling.

For every example it keeps:
  • prompt_id
  • inferred world (based on tools in first answer sequence)
  • first user prompt
  • first element of initial_config  (others dropped)
  • first answer sequence as expected_sequences (wrapped in a list)

To use:  change PROMPTS_FILE, ANSWERS_FILE, WORLDS_DIR below, then
         run  `python prepare_bfcl.py`.
"""

PROMPTS_FILE = "/Users/panosm/Desktop/Bloodrock/DFAs/temp/bfcl_dataset/prompts_dataset_list.json"     
ANSWERS_FILE = "/Users/panosm/Desktop/Bloodrock/DFAs/temp/bfcl_dataset/answers_list.json"      
WORLDS_DIR   = "/Users/panosm/Desktop/Bloodrock/DFAs/temp/bfcl_dataset/worlds"           
OUTPUT_FILE  = "/Users/panosm/Desktop/Bloodrock/DFAs/temp/bfcl_dataset/bfcl_dataset_final.json"       

import glob, json, os, re
from typing import Dict, List, Set, Any

def load_objects(path: str) -> List[dict]:
    """Load either JSON-Lines or a JSON array file."""
    with open(path, encoding="utf-8") as f:
        # detect format by first non-whitespace char
        while True:
            ch = f.read(1)
            if not ch or not ch.isspace():
                break
        f.seek(0)
        return json.load(f) if ch == "[" else [json.loads(line) for line in f if line.strip()]

def dump_jsonl(rows: List[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def load_worlds(dir_: str) -> Dict[str, Set[str]]:
    """Return {world_name → set(tool_name)} for every *.json in dir_."""
    worlds: Dict[str, Set[str]] = {}
    for fp in glob.glob(os.path.join(dir_, "*.json")):
        name = os.path.splitext(os.path.basename(fp))[0]
        with open(fp, encoding="utf-8") as f:
            worlds[name] = {tool["name"] for tool in json.load(f)}
    return worlds

_FN_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*\(")
def fn_name(call: str) -> str:
    m = _FN_RE.match(call)
    return m.group(1) if m else call.strip()

def choose_world(fnset: Set[str], worlds: Dict[str, Set[str]]) -> str:
    best, score = "unknown", 0
    for w, tools in worlds.items():
        overlap = sum(fn in tools for fn in fnset)
        if overlap > score or (overlap == score and overlap > 0 and w < best):
            best, score = w, overlap
    return best

# def first_config_entry(cfg: Any) -> Any:
#     """
#     Return a dict containing only the first key-value pair
#     of `cfg` (assuming `cfg` is a mapping). If cfg is not a
#     dict or is empty, return cfg unchanged.
#     """
#     if isinstance(cfg, dict) and cfg:
#         key = next(iter(cfg))
#         return {key: cfg[key]}
#     return cfg


def load_dfa_specs(dir_: str) -> Dict[str, dict]:
    """
    Load DFA specs and map them to prompt_id by extracting the part
    of the filename starting from 'multi' (e.g. messages_multi_turn_2.json → multi_turn_2).
    """
    dfa_map: Dict[str, dict] = {}
    for fp in glob.glob(os.path.join(dir_, "*.json")):
        fname = os.path.splitext(os.path.basename(fp))[0]
        match = re.search(r"(multi\w*)", fname)
        if not match:
            continue
        prompt_id = match.group(1)
        with open(fp, encoding="utf-8") as f:
            dfa_map[prompt_id] = json.load(f)
    return dfa_map



def build_dataset() -> List[dict]:
    prompts = {p["id"]: p for p in load_objects(PROMPTS_FILE)}
    answers = {a["id"]: a for a in load_objects(ANSWERS_FILE)}
    worlds  = load_worlds(WORLDS_DIR)
    dfa_specs = load_dfa_specs("/Users/panosm/Desktop/Bloodrock/DFAs/temp/bfcl_dataset/dfas")  # ← your DFA folder

    merged, skipped = [], 0
    for pid, p in prompts.items():
        ans_entry = answers.get(pid)
        if not ans_entry or not ans_entry["ground_truth"]:
            skipped += 1
            continue

        first_seq = ans_entry["ground_truth"][0]
        fnset: Set[str] = {fn_name(call) for call in first_seq}
        world = choose_world(fnset, worlds)

        merged.append({
            "prompt_id":          pid,
            "world":              world,
            "prompt":             p["question"][0][0]["content"],
            "initial_config":     p.get("initial_config", {}),
            "involved_classes":   p.get("involved_classes", []),
            "expected_sequences": [first_seq],
            "CORE":           dfa_specs.get(pid, None)
        })

    print(f"✓ merged {len(merged)} examples   (skipped {skipped})")
    return merged


if __name__ == "__main__":
    dataset = build_dataset()
    dump_jsonl(dataset, OUTPUT_FILE)
    print(f"↳ wrote {OUTPUT_FILE}")

