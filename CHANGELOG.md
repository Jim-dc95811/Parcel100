# Changelog

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
