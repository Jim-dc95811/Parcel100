Parcel100 1.5

Purpose
-------
Build up to 100 small ArcGIS Earth-ready GeoJSON parcel files from one Master 4
1-degree box. Cell numbering matches the existing Master4 Grid Maker.

No QGIS project is required for production.
No third-party Python packages are required.

Quick start
-----------
1. Run Parcel100.bat.
2. Enter Master 4 coordinates, for example: 82w,81w,30n,31n
3. Paste a public ArcGIS FeatureServer or MapServer URL: either the service itself
   (ending in /FeatureServer or /MapServer) or one layer (ending in /<layer id>).
4. Click Read Service. If the service has several polygon layers, choose the parcel layer.
   If some layers did not respond, they are listed so you can try again later.
5. Select only the fields you want carried into ArcGIS Earth.
6. Choose an output folder.
7. Click BUILD 100 GEOJSON FILES.

Florida preset
--------------
The program starts with the Florida statewide parcel layer used during development:
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0

The Recommended selection includes these Florida fields when present:
OWN_NAME
PHY_ADDR1
PHY_CITY
PHY_ZIPCD
PARCEL_ID
Acres

The program reads the service metadata itself. For other states or counties,
replace the URL with their public ArcGIS FeatureServer polygon layer.

Output naming
-------------
Example Master 4: 82w,81w,30n,31n
W082W081N031N030-001-Parcels.geojson
...
W082W081N031N030-100-Parcels.geojson

Each file is WGS 84 / EPSG:4326 GeoJSON for direct use in ArcGIS Earth.

Resume / retry
--------------
- Existing complete GeoJSON output files are skipped automatically. Restart an interrupted build with the same Master 4 and output folder to continue from missing cells.
- Each cell is written as a .partial file and renamed only when complete. An existing cell file that is not complete GeoJSON (for example, left by an interrupted older version) is rebuilt.
- If you change the URL after Read Service, click Read Service again before building.
- Dropped or transient service requests are retried up to 3 times before the build stops.
- A download batch that keeps timing out is split in half and retried, down to single parcels.
- Every parcel ID is checked off. Parcels the service did not return are asked for once more; any still missing are listed per cell in a warning at the end (those cells are still written).
- Existing files are never overwritten automatically. Delete a cell file first if you intentionally want Parcel100 to rebuild it.

Difficult-cell fallback
-----------------------
- Retry activity is visible in the status line.
- If a normal 0.1-degree parcel-ID query repeatedly fails with a recognized transient service error, Parcel100 automatically divides that cell into four smaller internal query boxes.
- IDs returned by the four fallback queries are de-duplicated.
- Parcel100 still writes only the normal single GeoJSON file for the original cell.

Notes
-----
- The tool requests only the selected attributes, reducing file size and popup clutter.
- Empty cells are detected by the lightweight ID query and skipped.
- A failed service request is treated as an error, not as an empty cell.
- A parcel crossing a cell boundary can exist in both neighboring files so either cell retains complete parcel geometry.
- Public FeatureServer access is required while building the files. The output GeoJSON files themselves are local/offline.
