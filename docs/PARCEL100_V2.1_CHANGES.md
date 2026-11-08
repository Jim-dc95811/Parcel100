# Parcel100 2.1 - what changed (2026-11-08)

> 🤖 **Using AI assistance?** Have the agent read the [CLAUDE.md](https://github.com/Jim-dc95811/ArcGIS-Earth-Unlocked/blob/main/CLAUDE.md) file first.

A re-hardening release. **A normal build writes exactly the same cell files as 2.0** (checked byte for byte). Live-tested by Jim on 2026-11-08 against a stand-in parcel server with bad records ([`parcel_test_server.py`](https://github.com/Jim-dc95811/ArcGIS-Earth-Unlocked/blob/main/tools/test-rigs/parcel_test_server.py)).

| # | Before (2.0) | Now (2.1) |
|---|---|---|
| 1 | Building into a folder that already held cell files from **another layer** or with **other fields** skipped them all as "existing files" - you kept the old layer's or old fields' files without a word. | BUILD checks each cell file already there. If it came from another layer or holds other fields, it asks: **Yes** = replace them, **No** = keep them, **Cancel** = stop. A true resume (same layer, same fields) still skips quietly. Replacing also removes an old cell the new layer has nothing in. |
| 2 | URLs copied from the browser (`.../FeatureServer/0?f=pjson`) were refused. | Accepted. |
| 3 | A login page gave `Expecting value: line 1 column 1 (char 0)`. | "The server did not send map data. It may need a login, or this is not an ArcGIS REST service URL." |
| 4 | A parcel the server sent with an empty shape `{}` stopped the whole build. | Written with its fields and no shape, and counted in the end message. |
| 5 | Letters in Coordinate precision gave `expected floating-point number...`; a Master 4 box typed as numbers said only "Invalid coordinate". | "Coordinate precision: type a whole number from 5 to 12"; the Master 4 message shows the example `82w,81w,30n,31n`. |
| 6 | The end message listed files, skipped files, empty cells and parcels together, so the numbers did not visibly add up (Jim: "math doesn't add to 100?"). | **100 cells:** written / already there / empty - always adds to 100 - and the parcel count on its own line. |

Test rig: [`parcel100_test_v21.py`](https://github.com/Jim-dc95811/ArcGIS-Earth-Unlocked/blob/main/tools/test-rigs/parcel100_test_v21.py) (runs the real build headless against the stand-in server; ALL PASS).
