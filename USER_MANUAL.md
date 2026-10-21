# Parcel100 User Manual

## Purpose

Parcel100 creates up to 100 small offline parcel GeoJSON files from one Master 4 1-degree box. The files are designed for direct use in ArcGIS Earth as clickable vector layers with selected parcel attributes preserved.

The program is intended to hide the repetitive GIS/server work from the operator. You provide a geographic Master 4 box and a public ArcGIS FeatureServer polygon layer; Parcel100 does the cell-by-cell querying and GeoJSON production.

## Requirements

- Windows 10/11
- Python 3 available through the Windows `py` launcher
- Internet access while building GeoJSON files
- A public ArcGIS FeatureServer polygon-layer URL
- ArcGIS Earth for the intended viewing workflow

No QGIS installation is required for production and no third-party Python packages are required.

## Start Parcel100

Keep these two files in the same folder:

```text
Parcel100.py
Parcel100.bat
```

Double-click:

```text
Parcel100.bat
```

The GUI opens as **Parcel100 1.4**.

## 1. Enter the Master 4 box

Enter exactly four whole-degree edges in this order:

```text
west,east,south,north
```

Example:

```text
82w,81w,30n,31n
```

The box must be exactly 1 degree wide and 1 degree tall.

Parcel100 subdivides the box into the established 100 Master 4 cells, each approximately 0.1 degree by 0.1 degree in geographic coordinates.

## 2. Enter the FeatureServer layer URL

The URL must point to a polygon layer, normally ending in:

```text
/FeatureServer/0
```

or another numeric layer ID.

Florida preset:

```text
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0
```

For another state or county, paste that jurisdiction's public parcel FeatureServer layer URL instead.

A web-map URL is not the same thing as the FeatureServer layer URL. Parcel100 needs the data layer itself.

## 3. Click Read Service

Click:

```text
Read Service
```

Parcel100 reads the layer metadata and populates the field list.

The status line reports the number of fields and the service's reported maximum record count.

If the field list remains empty, verify that:

- the URL points directly to a FeatureServer layer;
- the service is public/reachable;
- the layer is a polygon layer.

## 4. Select fields to keep

The field list controls what parcel attributes are written into every GeoJSON feature.

For the Florida statewide layer, the current lean field set is:

```text
OWN_NAME
PHY_ADDR1
PHY_CITY
PHY_ZIPCD
PARCEL_ID
Acres
```

Click **Recommended** to select those fields when they exist.

Other jurisdictions use different names, so inspect the aliases shown beside each field and select what is useful for your purpose.

Useful categories commonly include:

```text
Owner name
Physical/site address
City
ZIP/postal code
Parcel/APN/PIN identifier
Acres / area field
Public-land flag
```

Avoid selecting everything unless you truly need it. Fewer attributes produce smaller, cleaner field files and simpler ArcGIS Earth popups.

## 5. Choose the output folder

Use **Browse** or type a folder path.

Parcel100 creates the folder if necessary.

## 6. Coordinate precision

Default:

```text
7
```

This controls the coordinate precision requested from the FeatureServer for the returned WGS 84 geometry.

The supported GUI range is 5 through 12.

For ordinary parcel display, the default is a good balance between geometry detail and file size.

## 7. Build the files

Click:

```text
BUILD 100 GEOJSON FILES
```

Parcel100 processes the Master 4 cells in order.

Before making any server request for a cell, Parcel100 computes the exact expected output filename. If that file already exists in the output folder, the cell is treated as completed and skipped. This is the current resume behavior.

For each unfinished cell it first asks the service only for matching object IDs. If there are no matching parcel IDs, the cell is marked empty and skipped.

A successful empty-cell result is different from a server failure. A network/service error is retried and is never silently treated as an empty cell.

If a normal 0.1-degree object-ID query repeatedly fails with a transient error such as a timeout, 502/503/504, remote-end-close, or connection reset, Parcel100 automatically divides that cell into four smaller internal query envelopes. It queries each quarter, de-duplicates the IDs, and then continues the normal feature download for the original cell.

For populated cells, Parcel100 downloads the parcel features in service-sized batches and writes one GeoJSON file.

## Output naming

Example Master 4:

```text
82w,81w,30n,31n
```

Example files:

```text
W082W081N031N030-004-Parcels.geojson
W082W081N031N030-005-Parcels.geojson
W082W081N031N030-006-Parcels.geojson
```

The three-digit cell number matches the established Master 4 cell addressing.

Only populated unfinished cells are written.

## Completion message

At the end Parcel100 reports:

- number of GeoJSON files written during the current run;
- number of existing files skipped;
- number of empty cells skipped;
- total parcel records written during the current run.

A field-tested Florida run produced:

```text
55 GeoJSON files
45 empty cells skipped
663,277 parcel records written
```

Parcel100 1.4 reproduced this result in its acceptance run, with the new `Acres` field visible and working in ArcGIS Earth.

A second Master 4 produced:

```text
92 GeoJSON files
8 empty cells skipped
547,183 parcel records written
about 314 MB total
```

These are real-world examples, not guaranteed sizes or speeds.

## Resume an interrupted build

Rerun Parcel100 with the same Master 4 and the same output folder.

Any expected GeoJSON filename already present is skipped before a server query is made. Missing cells continue normally.

Current caution: Parcel100 trusts an existing expected filename as complete. If you intentionally want to rebuild a cell, delete that cell's GeoJSON first.

## Open the results in ArcGIS Earth

In ArcGIS Earth, add one or more `.geojson` files as local data.

The parcel polygons remain vector features. Click a parcel to open the feature popup and inspect the selected fields.

A practical offline stack is:

```text
TPKX imagery
+ local Parcel100 GeoJSON
+ other operational vector layers/pins
```

Do not flatten the parcel layer into raster MBTiles/TPKX if you want the parcel attributes to remain clickable.

## Why the files are split

GeoJSON is not a tiled database like MBTiles/TPKX. Very large GeoJSON files can take substantial time and memory to parse in a viewer.

The 100-cell design keeps each feature collection geographically small and lets the operator load only the area needed.

It also keeps FeatureServer queries manageable and naturally skips ocean/out-of-state/out-of-coverage cells.

## Boundary behavior

Parcel100 queries each cell using an `intersects` spatial relationship.

A parcel crossing a cell edge can therefore appear in both neighboring GeoJSON files. This is intentional. Each cell remains independently useful and retains the full parcel geometry.

## Other states

Parcel100 is not limited to Florida.

To try another jurisdiction:

1. Find a public ArcGIS parcel FeatureServer polygon layer.
2. Paste the layer URL into Parcel100.
3. Click **Read Service**.
4. Select that jurisdiction's owner/address/parcel/acres fields.
5. Enter a Master 4 covering the desired area.
6. Build.

Coverage and schema vary widely. Some states publish statewide parcel layers; others publish county-by-county layers.

## Troubleshooting

### Read Service fails

Check the URL in a browser. It should resolve to an ArcGIS REST layer page and report polygon geometry.

### Build pauses and shows retry text

That is expected resilience behavior. Parcel100 retries transient request failures up to three times. A repeatedly failing full-cell ID query may then switch automatically to the four-part fallback.

### Build stops on one cell

A persistent service or connectivity problem is treated as an error. Re-run after confirming the source service is available. Completed files already in the output folder will be skipped.

### ArcGIS Earth shows nothing

Confirm the GeoJSON was produced by Parcel100 and that the view is near the Master 4 area. Parcel100 requests output geometry in EPSG:4326 / WGS 84.

### Popup has too much information

Rebuild with fewer selected fields.

### Acres is missing

The source service must actually expose an acreage/area field. For the current Florida preset, `Acres` is included in the Recommended selection. Other jurisdictions may use a different field name or provide no acreage attribute.

### Some parcels appear in two files

Expected at cell boundaries. Parcel100 preserves complete parcel geometry instead of clipping parcels to the cell edge.

## Data caution

Parcel GIS is reference data. It can be stale, generalized, misaligned, or different from a surveyed/legal boundary. Owner/address/acres data may represent assessment records rather than current occupancy or surveyed acreage.

For critical property decisions, verify against the responsible property appraiser, recorder, survey, deed, or other authoritative source.
