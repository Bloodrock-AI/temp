#!/usr/bin/env python3
"""
Convert a “JSON-lines” file (one JSON object per line, no commas or
wrapper list) into a proper JSON array.

Input :  BFCL_v3_multi_turn_base (6).json
Output:  BFCL_v3_multi_turn_base_list.json
"""

import json
from pathlib import Path

INPUT_FILE  = Path("/Users/panosm/Desktop/Bloodrock/DFAs/temp/bfcl_dataset/bfcl_unified_dataset.json")
OUTPUT_FILE = INPUT_FILE.with_name(INPUT_FILE.stem + "_list.json")

def main() -> None:
    objects = []

    with INPUT_FILE.open(encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if raw:                      
                objects.append(json.loads(raw))

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(objects, f, indent=2, ensure_ascii=False)

    print(f"✅  Wrote {len(objects)} objects to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
