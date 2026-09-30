#!/usr/bin/env python3
"""Merge fresh SVR finds into the SVR Watch artifact database.

Usage: merge.py <existing_dir> <out_dir> <finds.json> [<finds.json> ...]

existing_dir: ArtifactData `list` output (out_dir) — reads <existing_dir>/listings/*.json
finds files:  JSON arrays of listings, or {"listings": [...], "comps": [...]}
Writes one JSON doc per changed listing/comp into out_dir/{listings,comps}/ and
out_dir/writes.json: batch entries (chunk to 50) for ArtifactData.
"""
import hashlib, json, re, sys, glob, os, datetime

GONE_AFTER_DAYS = 3
LIVE = {"active", "auction", "unverified"}
RANK = {"active": 3, "auction": 3, "unverified": 1}
today = datetime.date.today().isoformat()

def doc_id(l):
    vin = (l.get("vin") or "").strip().upper()
    if re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
        return vin
    return "u-" + hashlib.sha1((l.get("url") or json.dumps(l, sort_keys=True)).encode()).hexdigest()[:12]

def load_existing(d):
    out = {}
    for p in glob.glob(os.path.join(d, "**", "listings", "*.json"), recursive=True):
        with open(p) as f:
            raw = json.load(f)
        body = raw.get("data", raw) if isinstance(raw, dict) else raw
        out[os.path.splitext(os.path.basename(p))[0]] = body
    return out

def clean(l):
    keep = ["vin", "year", "body", "color", "miles", "price", "city", "state", "seller",
            "seller_type", "source", "url", "status", "ends", "notes", "flag"]
    c = {k: l.get(k) for k in keep if l.get(k) not in (None, "")}
    for k in ("miles", "price", "year"):
        if isinstance(c.get(k), str):
            n = re.sub(r"[^\d.]", "", c[k]); c[k] = int(float(n)) if n else None
    if c.get("vin"): c["vin"] = c["vin"].upper()
    if c.get("status") not in LIVE: c["status"] = "unverified"
    return c

def main():
    existing_dir, out_dir, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    existing = load_existing(existing_dir)
    finds, comps = {}, []
    for fp in files:
        with open(fp) as f:
            data = json.load(f)
        items = data.get("listings", []) if isinstance(data, dict) else data
        if isinstance(data, dict): comps += data.get("comps", [])
        for raw in items:
            if raw.get("year") not in (2017, 2018, 2019, "2017", "2018", "2019"): continue
            l = clean(raw); i = doc_id(l)
            src = {"name": l.get("source", "?"), "url": l.get("url")}
            if i in finds:
                cur = finds[i]
                if RANK.get(l["status"], 0) > RANK.get(cur["status"], 0):
                    l["sources"] = cur["sources"]; finds[i] = cur = {**cur, **l}
                if src["url"] and src["url"] not in [s["url"] for s in cur["sources"]]:
                    cur["sources"].append(src)
                for k, v in l.items(): cur.setdefault(k, v)
            else:
                l["sources"] = [src] if src["url"] else []
                finds[i] = l

    os.makedirs(os.path.join(out_dir, "listings"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "comps"), exist_ok=True)
    writes, stats = [], {"new": 0, "updated": 0, "gone": 0, "drops": 0}

    def emit(coll, i, body):
        p = os.path.join(out_dir, coll, i + ".json")
        with open(p, "w") as f: json.dump(body, f, indent=1)
        writes.append({"op": "set", "collection": coll, "doc_id": i, "file_path": os.path.abspath(p)})

    for i, l in finds.items():
        old = existing.get(i)
        if old:
            hist = list(old.get("priceHistory") or [])
            if l.get("price") is not None and (not hist or hist[-1].get("p") != l["price"]):
                if hist and l["price"] < hist[-1]["p"]: stats["drops"] += 1
                hist.append({"d": today, "p": l["price"]})
            srcs = {s["url"]: s for s in (old.get("sources") or []) + l["sources"] if s.get("url")}
            body = {**old, **l, "sources": list(srcs.values()), "priceHistory": hist,
                    "firstSeen": old.get("firstSeen", today), "lastSeen": today}
            stats["updated"] += 1
        else:
            body = {**l, "firstSeen": today, "lastSeen": today,
                    "priceHistory": [{"d": today, "p": l["price"]}] if l.get("price") is not None else []}
            stats["new"] += 1
        emit("listings", i, body)

    for i, old in existing.items():
        if i in finds or old.get("status") not in LIVE: continue
        last = old.get("lastSeen") or old.get("firstSeen") or today
        if (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)).days >= GONE_AFTER_DAYS:
            emit("listings", i, {**old, "status": "gone"}); stats["gone"] += 1

    for c in comps:
        cid = "c-" + hashlib.sha1((c.get("url") or json.dumps(c, sort_keys=True)).encode()).hexdigest()[:12]
        emit("comps", cid, c)

    with open(os.path.join(out_dir, "writes.json"), "w") as f: json.dump(writes, f, indent=1)
    live = sum(1 for i, l in finds.items()) + sum(
        1 for i, o in existing.items() if i not in finds and o.get("status") in LIVE) - stats["gone"]
    print(json.dumps({**stats, "writes": len(writes), "live_after": live}))

if __name__ == "__main__":
    main()
