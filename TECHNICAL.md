# Parcel100 Technical Notes

## Version

Current public source: **Parcel100 1.1**.

## Design goal

Parcel100 converts one Master 4 1-degree box into up to 100 geographically indexed parcel GeoJSON files without requiring QGIS in the production path.

The production chain is:

```text
Master 4 input
    -> 100 geographic cells
    -> FeatureServer object-ID query per cell
    -> skip empty cells
    -> batched feature queries for populated cells
    -> Esri polygon rings -> GeoJSON Polygon/MultiPolygon
    -> EPSG:4326 GeoJSON files
```

## Dependencies

Python standard library only:

- `json`
- `math`
- `re`
- `threading`
- `time`
- `urllib`
- `pathlib`
- `tkinter`

No `requests`, GDAL, Fiona, GeoPandas, Shapely, ArcPy, or QGIS Python environment is required.

## Master 4 input

The parser requires exactly four whole-degree edges in this order:

```text
west,east,south,north
```

Example:

```text
82w,81w,30n,31n
```

The longitude span and latitude span must each be exactly 1 degree.

## Cell addressing

Parcel100 intentionally matches the established Master4 Grid Maker 01-100 addressing logic.

The 1-degree box is divided into 10 rows and 10 columns. The implementation is hemisphere-aware and uses absolute decimal-degree position so the same cell-number concept works east/west and north/south of the equator.

Output uses three digits:

```text
001
002
...
100
```

Example filename:

```text
W082W081N031N030-055-Parcels.geojson
```

## Service discovery

The GUI accepts a direct ArcGIS FeatureServer **layer** URL.

Parcel100 requests:

```text
f=json
```

from the layer endpoint and verifies:

- a field schema is present;
- geometry type is `esriGeometryPolygon`.

The field list shown in the GUI comes from the service metadata, including field aliases when available.

The Florida field suggestions are only preferences for the known statewide layer. Other services are discovered dynamically.

## Empty-cell probe

Before downloading full feature records, each cell is queried with:

```text
where=1=1
geometry=<west,south,east,north>
geometryType=esriGeometryEnvelope
inSR=4326
spatialRel=esriSpatialRelIntersects
returnIdsOnly=true
returnGeometry=false
```

If the service successfully returns no object IDs, the cell is marked empty and no GeoJSON file is written.

A service/network failure is not treated as empty. The build stops with an error after retries.

This distinction matters for Master 4 boxes that include ocean, another state, or any area outside the selected parcel service's coverage.

## Feature retrieval

For populated cells, Parcel100 uses the returned object IDs and requests features in batches.

Batch size is derived from the layer's reported `maxRecordCount`, capped at 2,000 records per request in v1.1.

The feature request includes:

```text
objectIds=<batch ids>
outFields=<only user-selected fields>
returnGeometry=true
outSR=4326
returnZ=false
returnM=false
geometryPrecision=<GUI precision>
```

This means unnecessary source attributes are never requested in the heavy feature-download pass.

## Output CRS

Parcel100 requests the server to return geometry in:

```text
EPSG:4326 / WGS 84
```

This avoids the manual reprojection step that was required during early QGIS testing and produces GeoJSON coordinates suitable for ArcGIS Earth.

The Florida source service used during development is not stored in WGS 84, but ArcGIS FeatureServer performs the requested `outSR=4326` transformation.

## Esri polygon geometry conversion

ArcGIS REST polygon geometry is returned as `rings`.

Parcel100 converts those rings into valid GeoJSON `Polygon` or `MultiPolygon` geometry.

The conversion does not rely solely on ring winding direction. Instead it:

1. closes rings when necessary;
2. drops zero-area/invalid-short rings;
3. calculates absolute ring area;
4. determines containment relationships between rings;
5. builds a containment-depth tree;
6. treats even-depth rings as polygon shells and direct odd-depth children as holes;
7. emits `Polygon` for one shell group or `MultiPolygon` for multiple groups.

This is intended to handle ordinary parcel geometry from services that do not preserve Esri winding rules consistently.

## Cell-boundary duplication

The spatial relationship is `intersects`, not a clipping operation.

If a parcel intersects two adjacent Master 4 cells, the complete parcel can appear in both output files.

This is intentional. A single cell remains independently useful and does not contain a chopped parcel at the boundary.

The tradeoff is some duplicated storage along cell edges.

## GeoJSON structure

Each file is written as a compact JSON `FeatureCollection` containing:

```text
type
name
bbox
master4
cell
source
features
```

Each feature contains:

```text
type = Feature
properties = selected source attributes
geometry = Polygon or MultiPolygon
```

JSON is written without decorative whitespace to reduce file size.

## Coordinate precision

GUI range:

```text
5 through 12
```

Default:

```text
7
```

The value is sent to the FeatureServer as `geometryPrecision`.

Higher precision increases coordinate text length and therefore GeoJSON size. The best value depends on the source geometry and intended use.

## Retry behavior

Network/service requests use:

```text
TIMEOUT = 90 seconds
RETRIES = 3
```

Between failed attempts Parcel100 waits progressively longer.

ArcGIS JSON responses containing an `error` object are surfaced as failures rather than silently accepted.

## Threading

Metadata reads and builds run in a worker thread so the Tk GUI remains responsive enough to update progress/status while network requests are active.

The 100 cells are processed sequentially in v1.1. The program intentionally does not fire 100 simultaneous requests at a public GIS service.

## Output performance rationale

GeoJSON is a text-based feature collection, not an indexed tile store. Very large exports can be expensive for viewers to parse and hold as vector objects.

The 100-cell architecture was selected after field testing larger exports. A roughly half-grid test produced a GeoJSON around 329 MB, while individual 0.1-degree production cells commonly landed in the low-MB to tens-of-MB range depending on parcel density.

The cell design therefore serves both:

- server-side query manageability;
- viewer-side memory/load manageability.

## Florida development service

Current built-in preset:

```text
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0
```

Current preferred Florida fields:

```text
OWN_NAME
PHY_ADDR1
PHY_CITY
PHY_ZIPCD
PARCEL_ID
```

These are defaults/preferences, not a requirement of the engine.

## Real-world validation record

Owner-reported production runs during v1.1 development:

```text
Master 4: 82w,81w,30n,31n
55 populated files
45 empty cells skipped
663,277 parcel records written
```

```text
Master 4: 82w,81w,29n,30n
92 populated files
8 empty cells skipped
547,183 parcel records written
about 314 MB total
```

Multiple output cells were opened together in ArcGIS Earth and parcel features were visually confirmed to draw, align geographically, and expose the selected attributes in the feature popup.

These observations are field results, not universal performance guarantees.

## Current limitations

- Polygon FeatureServer layers only.
- Public/reachable services only; no login/token workflow in v1.1.
- No automatic parcel-service discovery by state/county name.
- No clipping of parcels to cell boundaries.
- No deduplication across neighboring cell files.
- No automatic loading/unloading of cells inside ArcGIS Earth.
- No national parcel data is bundled with the program.
- Source quality, update schedule, allowed uses and field semantics remain the responsibility of the source provider/operator.

## Preservation rule

The program's core production behavior should remain deterministic:

```text
one Master 4 input
-> same 100 cell addresses
-> same output naming
-> only populated cells written
```

Changes that alter cell numbering, naming, or output geometry should be treated as compatibility changes and tested against the Master 4 system before release.
