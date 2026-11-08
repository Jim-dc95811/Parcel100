# Changelog


## Parcel100 2.0 - the 2.0 Reference (2026-11-08)

- The whole ArcGIS Earth Unlocked family moved to 2.0 as one reference point (Jim). Program = 1.5 with only the version text changed (diff-checked). The workflow now builds `downloads/Parcel100_v2.0.zip`; older zips moved to `archive/`.

## 1.5.2 - 2026-11-08

Ready to Fly: `Parcel100.bat` - the launcher now gets the PC ready first: it finds Python or installs it for you (just for you, no admin - answer **Y**), then starts the tool. New file `System Files\Ready_To_Fly.ps1` (log: `System Files\Ready_To_Fly_log.txt`). Program byte-identical to the previous release. Live-tested by Jim 2026-11-08.

## 1.5.1 - 2026-11-06

One obvious file (Jim's packaging rule): the zip holds a `Parcel100_v1.5.1` folder with `Parcel100.bat` and `System Files\Parcel100.py`. The README text file is no longer in the download. Program unchanged (1.5).

## 1.5 - 2026-11-01

Discovery and hardening release; normal output is byte-identical to 1.4. Details: [docs/PARCEL100_V1.5_CHANGES.md](docs/PARCEL100_V1.5_CHANGES.md).

- Paste a FeatureServer/MapServer service root or a layer URL; several polygon layers bring up a chooser.
- Discovery shows its progress, lists layers that did not respond, and accepts URLs ending in `/query`.
- Cells are written as `.partial` and renamed when complete; on resume an incomplete existing cell is rebuilt.
- Every parcel ID is checked; missing parcels are asked for once more and any still missing are reported per cell (write and warn).
- A download batch that keeps timing out is split in half and retried.
- The build uses the layer that was read; changing the URL afterwards asks for Read Service again.

## 1.4 - 2026-10-21

- Added `Acres` to the Florida **Recommended** field selection when present.
- Confirmed ArcGIS Earth popup workflow with the acreage column visible alongside parcel ID, owner name, and physical address fields.
- Confirmed a full acceptance run producing 55 GeoJSON files, skipping 45 empty cells, and writing 663,277 parcel records.

## 1.3 - 2026-10-19

- Added visible retry status so slow or unstable services do not look like a frozen application.
- Added four-part difficult-cell fallback for repeated transient full-cell ID-query failures.
- Quarter-query results are de-duplicated and still produce one normal output GeoJSON for the original cell.
- Existing resume behavior remains unchanged.

## 1.2 - 2026-10-19

- Added automatic skip/resume behavior for existing GeoJSON output files.
- Added retry handling for dropped/failed service requests before aborting a build.
- Existing files are not overwritten automatically.

## 1.1 - 2026-10-19

- Added empty-cell detection before full feature download.
- Empty cells are skipped instead of producing meaningless GeoJSON files.
- Service/query failures remain errors and are not treated as empty cells.
- Completion status now reports files written, empty cells skipped and total parcel records written.
- Field-tested against the Florida statewide parcel service with two full Master 4 production runs.

## 1.0 - 2026-10-19

- Initial Parcel100 GUI.
- Master 4 whole-degree input.
- 100-cell geographic subdivision matching the existing Master4 Grid Maker numbering.
- Public ArcGIS FeatureServer polygon-layer metadata discovery.
- Selectable output fields.
- Florida statewide parcel service preset and recommended Florida fields.
- Batched object-ID based feature retrieval.
- WGS 84 / EPSG:4326 output geometry.
- Esri ring conversion to GeoJSON Polygon/MultiPolygon.
- Deterministic ArcGIS Earth-ready GeoJSON filenames.
- Python standard library only; no QGIS project required for production.
