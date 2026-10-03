# F-Type SVR (2017-2019) fringe playbook

SVR VIN patterns: 2017 `SAJWJ6J8` (coupe) / `SAJWJ6K8` (convertible). 2018-19 `SAJDZ1FE` (coupe) / `SAJDZ5FE` (convertible). 2017 R AWD is `SAJWJ6DL`/`EL`, so it is not an SVR.

## Sources that work from curl (browser UA)
1. **KBB/Autotrader JSON-LD**, the best source for private sellers:
   `curl -sL --compressed -A "$UA" "https://www.kbb.com/cars-for-sale/all/jaguar/f-type/svr?searchRadius=0"`, then parse `<script type=application/ld+json>` for `vehicleIdentificationNumber`, offers.price, seller.
   - Private only: `.../used/jaguar/f-type/svr?searchRadius=0&sellerType=p`
   - Per year: `.../all/2019/jaguar/f-type/svr?searchRadius=0`
   - Detail page `kbb.com/cars-for-sale/vehicle/<id>` shows `"ownerName"`, `"daysOnSite"`, `"stockNumber"`
2. **Autolist API** (no key): `https://www.autolist.com/api/v2/search?make=Jaguar&model=F-TYPE&year_min=2017&year_max=2019&limit=50&page=N`. Filter by the VIN regex to catch mis-trimmed SVRs.
3. **CarStory**: `https://www.carstory.com/cars/jaguar/f-type/svr`. Decode `__NUXT_DATA__`. It gives street address, `days_available`, and descriptive color.
4. **iSeeCars**: `https://www.iseecars.com/used_cars-t24726-used-jaguar-f-type-svr-for-sale` (JSON-LD). Sometimes lists cars the other feeds miss (the Tampa 2017).
5. **Craigslist nationwide**: loop over the US AreaIDs from `https://reference.craigslist.org/Areas` into `https://sapi.craigslist.org/web/v8/postings/search/full?batch=<AreaID>-0-360-0-0&cc=US&lang=en&query=jaguar%20svr&searchPath=cta`. Item fields: [0]+decode.minPostingId = post id, [3] = price, the last string is the title. Also try the queries `f-type%20svr` and `jaguar%20f-type` (filter the titles by year and price). Opening a post URL redirects to `craigslist.org/view/...`; check it for "has just been Sold".
6. **Dealer VDP check**: ebizautos sites (such as motorpointroswell.com) and DealerSocket/"-c-NNNN" sites curl fine and show SOLD in the text. Dealer.com, DealerInspire, Hendrick and Harper sites all return 403.
7. **VIN reverse search** (WebSearch `"<VIN>"`) turns up salvage/IAAI history on bid.cars, bidfax and bidspace. Run it on every hit.

## Blocked or dead ends (skip on daily runs)
CarGurus, Cars.com, Carfax, TrueCar, Carvana, JD Power, CarsDirect, carsforsale.com, KSL (403), eBay (403 to curl and WebFetch), Facebook Marketplace (no content), classic.com (403), dupontregistry (JS only), Reddit/BaT/Hemmings (blocked for WebSearch). Forum classifieds turned up only WTB posts.

## Useful WebSearch queries
- `"F-TYPE SVR" used <State> <City> 2017 OR 2018 OR 2019 dealer`
- `"Pre-Owned 2018 Jaguar F-TYPE SVR"` / `"Used 2017 Jaguar F-TYPE SVR"` (most hits are dealer VDPs that are already sold)
- `carsandbids 2018 OR 2019 Jaguar F-Type SVR auction <month year>`
- `"<street address>" dealer` to name a CarStory seller from its address

## Added 2026-09-30 (noon sweep)
- WORKS: CarEdge VIN page `https://www.caredge.com/shop-cars/used/<VIN>` curls fine; gives price, dealer, in-stock or "Vehicle Not Found". It can be stale (it kept the Grand Prairie car with photos from 7/2024), so use it as a liveness hint only.
- WORKS: Carfax search API `helix.carfax.com/search/v2/vehicles?...` returns JSON even though carfax.com pages 403/503. It ignores the trim filter and skews to the Northeast, so filter by VIN regex.
- WORKS: BaT model page (curl) embeds completed results as data, good for comps. PCarMarket and jaguarforums curl fine.
- BLOCKED: Edmunds now 403s for every UA including iPhone. Cars & Bids, Collecting Cars and Sotheby's Motorsport 403; BaT, Hemmings and Mecum are rejected by WebSearch allowed_domains; Hagerty sales history needs a login; ftypeforum.com doesn't resolve.
- Craigslist: watch for Canadian cross-posts (e.g. Port Huron → Scarborough ON, CAD price) and exclude them.

## Added 2026-10-01
- CORRECTION: every CarEdge VIN page contains the strings "Vehicle Not Found" and "Sold" (template text), even for live cars. A gone car shows as a small page (~122KB) with no listing data/price; judge by price presence, not text.
- WORKS: Capital One Auto Navigator pages curl fine and include VINs (no new SVRs today).
- WORKS: Hagerty Marketplace (search ignores the query; page through all ~200 live lots), duPont Registry now renders with VINs, BaT search page carries every live lot, PCarMarket works on its new site URLs.
- BLOCKED: jaguarforums.com now 403s (worked 2026-09-30).
- Ferco Motors Miami 2019 conv (eBay 287429283044) VIN = SAJDZ5FE9KCK61153. The Carfax "Atlanta" 2017 coupe (29,458 mi, $66,590) is actually Carvana Richmond VA.

## Added 2026-10-02
- WORKS: Searching only carsandbids.com returns lot pages with the VIN in the title, plus the end date and high bid. C&B 2017 SVR coupe SAJWJ6J89HMK43732 (Winthrop ME, 8.1k mi) ended 2026-09-28 at a $54,000 high bid; sold/reserve not confirmed, so watch for a relist.
- WORKS: Small dealer sitemaps (e.g. exoticmotorsportsok.com/sitemap.xml) list every VDP including sold ones; a sold VDP's title says "(Sold)". The classic.com Edmond OK 2019 SVR is sold.
- WORKS: carsforsale.com vehicle pages load via WebFetch even though curl 403s.
- BLOCKED: Westlake Financial dealer listings, turnersv.com (403), porsche.com dealer pages (429).
- Gotcha: 2020 SVRs share the SAJDZ1FE/SAJDZ5FE prefix (10th char L). Check that the 10th char is J/K, not just the prefix.

## Added 2026-10-03
- WORKS: Carfax helix API with a single zip=66044&radius=3000 query (pages 1-10) returns all ~237 U.S. F-Type listings, replacing the 10-zip loop.
- WORKS: turnersv.com pages load through WebFetch and its sitemap through curl (the Holt MO "SVR" lead isn't in its inventory). fercomotors.com curls fine (no Jaguar in stock). duPont Registry listing pages show sold status and the sale date.
- BLOCKED: indulgencemotors.com (curl and WebFetch), ultimomotors.com (curl), and WebFetch now refuses cars.com outright.
- Check: data.json has the C&B SAJWJ6J89HMK43732 comp as sold for $77,000 (2026-09-28), but a search snippet says $54,000. Verify by hand.
