# SVR Watch daily sweep

Dashboard: https://claude.ai/artifact/BMfFQbb7bqKYVoffuEJsVw (db collections: `listings`, `comps`, `meta/status`)
Target: every current U.S. listing of a 2017–2019 Jaguar F-Type SVR. U.S. only, SVR trim only.

## Steps
1. `D=runs/$(date +%F)`. Dump current db: ArtifactData `list` on `listings` (limit 1000) with `out_dir: <abs path to $D/existing>`.
2. Sweep sources per `fringe_playbook.md` (curl with a browser UA, WebSearch, WebFetch; no browser tools). Minimum each day:
   - KBB/Autotrader JSON-LD (all + `sellerType=p`), Autolist API, CarStory, iSeeCars, Carfax JSON (worked 2026-09-30 for the majors sweep), Edmunds (iPhone UA)
   - Craigslist nationwide sapi loop (`jaguar svr`, `f-type svr`)
   - WebSearch: live BaT / Cars & Bids / eBay SVR auctions; fresh dealer VDPs ("Used 2018 Jaguar F-TYPE SVR" etc.)
   - Re-check every existing live listing URL once; if a page says SOLD/unavailable, don't include it (merge marks it gone after 3 missed days).
   - VIN-reverse-search any NEW VIN for salvage/auction history; set `flag` (e.g. "Salvage history") if found.
   Use parallel subagents (major / auctions / fringe) when possible.
3. Write finds to `$D/finds.json`: array of {vin, year, body, color, miles, price, city, state, seller, seller_type, source, url, status: active|auction|unverified, ends, notes, flag}. Comps (closed auctions) as `{"listings":[],"comps":[...]}` in `$D/comps.json` only when new ones closed. Each comp needs `sold: true|false` and the FINAL hammer price. Never record a mid-auction or last-seen bid as the result: if the final price can't be confirmed (C&B/BaT 403), WebSearch the lot title + "sold for" and re-check the next day before writing it.
   VIN check: 2017 `SAJWJ6J8`/`SAJWJ6K8`; 2018–19 `SAJDZ1FE`/`SAJDZ5FE`. Drop non-VIN finds that duplicate a VIN'd car (same miles/price/city).
4. `python3 merge.py $D/existing $D/out $D/finds.json [$D/comps.json]`
5. Apply `$D/out/writes.json` with ArtifactData `batch` (≤50 per batch). Then `update` `meta/status`: `lastRun` (today), `sourcesChecked`, `blocked`, `summary` (one or two plain sentences: new cars, price drops, cars gone).
6. Publish to GitHub Pages (https://phummy1337.github.io/svr-watch/): ArtifactData `list` each of `listings`, `comps`, `meta` (limit 1000) with `out_dir: <abs path to $D/final>`, then
   `python3 export.py $D/final && git add data.json fringe_playbook.md && git commit -m "Sweep $(date +%F)" && git push`.
   If svr-watch.html changed, also run `./build.sh` and commit index.html.
7. If there are NEW listings or price drops, send a push notification with the one-line summary.
