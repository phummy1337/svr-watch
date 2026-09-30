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
