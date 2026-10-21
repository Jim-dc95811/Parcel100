# Parcel100 Continuity / Handoff

## Current state

Parcel100 1.4 is a working Windows GUI tool that converts one 1-degree Master 4 input into up to 100 small offline parcel GeoJSON files for ArcGIS Earth.

The current production path is proven against the Florida statewide parcel FeatureServer and has been accepted in ArcGIS Earth with the new Acres field visible in the parcel popup.

## Current source

Main files:

```text
Parcel100.py
Parcel100.bat
downloads/Parcel100_v1.4.zip
```

The program uses only the Python standard library.

## Core operating contract

```text
Master 4 input
-> Read public ArcGIS FeatureServer polygon layer
-> operator selects fields
-> split Master 4 into cells 001-100
-> compute deterministic output filename
-> skip existing completed files
-> lightweight ID query per unfinished cell
-> retry transient failures
-> if needed, split a difficult cell into four internal ID-query boxes
-> de-duplicate fallback IDs
-> skip successful zero-result cells
-> batch-download populated cells
-> request EPSG:4326 geometry
-> convert Esri rings to GeoJSON
-> write one GeoJSON per populated cell
```

Current output example:

```text
W082W081N031N030-004-Parcels.geojson
```

## Florida development source

```text
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0
```

Current lean/recommended Florida fields:

```text
OWN_NAME
PHY_ADDR1
PHY_CITY
PHY_ZIPCD
PARCEL_ID
Acres
```

The code compares preferred names case-insensitively, so the service's `Acres` field is selected by the `ACRES` preference while its real field name is retained in output.

## Proven ArcGIS Earth behavior

Real Parcel100 output has been opened in ArcGIS Earth and confirmed to:

- draw parcel polygon boundaries in the correct location;
- remain clickable vector features;
- expose selected parcel metadata in the feature popup;
- expose Acres in the popup when included;
- coexist with offline/local TPKX imagery and other Earth layers;
- load far more comfortably as small cells than as one very large GeoJSON.

The parcel layer is intentionally separate from raster imagery so metadata stays queryable.

## Production field results

### Master 4: 82w,81w,30n,31n

```text
55 populated GeoJSON files
45 empty cells skipped
663,277 parcel records written
```

The v1.4 acceptance run reproduced this result and displayed Acres correctly in ArcGIS Earth.

This Master 4 includes substantial ocean/out-of-Florida area, validating empty-cell skipping.

### Master 4: 82w,81w,29n,30n

```text
92 populated GeoJSON files
8 empty cells skipped
547,183 parcel records written
about 314 MB total
```

### Grid 3: 83w,82w,30n,31n

```text
63 populated GeoJSON files
37 empty cells skipped
78,837 parcel records written
about two minutes for the full 100-cell evaluation
```

### Grid 4

```text
99 populated GeoJSON files
1 empty cell skipped
469,146 parcel records written
```

### Difficult-service validation

The Florida Statewide Cadastral service on services9 repeatedly produced transient failures. Parcel100 1.3/1.4 resilience logic recovered difficult cells by retrying and, when necessary, using the four-part ID fallback. Cell 022 recovered 11,969 parcel IDs through that fallback during testing.

## Resume behavior

Resume is a current production feature.

Before making a server request for a cell, Parcel100 computes the exact expected filename. If that file already exists in the output folder, the cell is counted as existing and skipped.

This means an interrupted run can be restarted against the same Master 4 and folder without redownloading completed cells.

Current caution: the resume rule trusts an existing expected filename as complete. It does not validate the JSON or checksum the file before skipping it.

## Why 100 cells

A roughly half-grid manual GeoJSON export was observed around 329 MB and was expensive for ArcGIS Earth to ingest.

The 0.1-degree Master 4 cells provide a useful operating scale for both:

- FeatureServer query size;
- ArcGIS Earth GeoJSON parsing/memory load.

This also aligns parcel intelligence with the existing Master 4/TPKX geographic addressing system.

## Other states / public release strategy

Parcel100 is intentionally not hardcoded to the Florida schema.

The public workflow is:

1. user locates a public ArcGIS parcel FeatureServer polygon layer;
2. user pastes `/FeatureServer/<layer id>` into Parcel100;
3. **Read Service** discovers its fields;
4. user selects that jurisdiction's useful owner/address/parcel/acres fields;
5. normal Master 4 build proceeds.

The **Recommended** selection is exact for known Florida fields first, then uses generic owner/address/parcel/APN/PIN-style keyword matching as a fallback for other services.

## Current limitations

- no authentication/token workflow;
- polygon FeatureServer layers only;
- no automatic state/county service discovery;
- no cell deduplication at shared boundaries;
- no automatic ArcGIS Earth cell loading from GPS yet;
- no built-in state profiles beyond the Florida URL/field preference;
- service terms/field meanings/data quality vary by provider;
- resume trusts an existing expected filename as complete;
- feature download retries do not yet adaptively reduce the service-advertised batch size after repeated failures.

## Strong future extensions

Do not implement these automatically without explicit project direction, but they are natural next steps:

- source profiles for known state/county parcel services;
- save/load selected-field profiles;
- optional validation of existing GeoJSON before resume-skip;
- optional checksum or manifest per Master 4;
- adaptive feature-download batch reduction after repeated 504 responses;
- integration with a future Substitute Drone launcher so GPS determines the current Master 4 cell and loads the matching parcel GeoJSON;
- load current parcel cell plus surrounding neighbors on demand;
- public examples for states with different parcel schemas.

## Presentation concept

Parcel100 is strongest when shown as a late reveal in the broader offline-map/Substitute Drone demonstration.

After showing offline multiresolution TPKX imagery, GPS, operational overlays and navigation, the demonstration can simply say:

> "Let's just verify who owns the property."

Then click the local GeoJSON parcel and show the owner/address/acres popup.

The important message is not that parcel overlays are new. The project value is that public parcel intelligence has been converted into small, deterministic, offline local files that travel with the same geographic system as the offline imagery.

## Compatibility warning

Preserve the existing Master 4 numbering and deterministic filename contract unless an intentional version change is made.

The 100-cell geography is now shared infrastructure across multiple offline-map/intelligence workflows.
