# Changelog

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
