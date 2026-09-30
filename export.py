#!/usr/bin/env python3
"""Build data.json for the GitHub Pages copy from an ArtifactData dump.

Usage: export.py <dump_dir>   (dump_dir holds listings/, comps/, meta/ from ArtifactData list out_dir)
"""
import glob, json, os, sys

dump = sys.argv[1]
def docs(coll):
    out = []
    for p in sorted(glob.glob(os.path.join(dump, coll, "*.json"))):
        with open(p) as f:
            out.append({"_id": os.path.splitext(os.path.basename(p))[0], **json.load(f)})
    return out

meta = docs("meta")
data = {"listings": docs("listings"), "comps": docs("comps"),
        "meta": next((m for m in meta if m["_id"] == "status"), None)}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json"), "w") as f:
    json.dump(data, f, indent=1)
print(f"{len(data['listings'])} listings, {len(data['comps'])} comps")
