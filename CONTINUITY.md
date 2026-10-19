# Parcel100 Continuity / Handoff

## Current state

Parcel100 1.1 is a working Windows GUI tool that converts one 1-degree Master 4 input into up to 100 small offline parcel GeoJSON files for ArcGIS Earth.

The current production path is proven against the Florida statewide parcel FeatureServer.

## Current source

Main files:

```text
Parcel100.py
Parcel100.bat
downloads/Parcel100_v1.1.zip
```

The program uses only the Python standard library.

## Core operating contract

```text
Master 4 input
-> Read public ArcGIS FeatureServer polygon layer
-> operator selects fields
-> split Master 4 into cells 001-100
-> lightweight ID query per cell
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
```

## Proven ArcGIS Earth behavior

Real Parcel100 output has been opened in ArcGIS Earth and confirmed to:

- draw parcel polygon boundaries in the correct location;
- remain clickable vector features;
- expose selected parcel metadata in the feature popup;
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

This Master 4 includes substantial ocean/out-of-Florida area, validating empty-cell skipping.

### Master 4: 82w,81w,29n,30n

```text
92 populated GeoJSON files
8 empty cells skipped
547,183 parcel records written
about 314 MB total
```

Individual cells ranged from small files into the tens of MB depending on parcel density.

## Why 100 cells

A roughly half-grid manual GeoJSON export was observed around 329 MB and was expensive for ArcGIS Earth to ingest.

The 0.1-degree Master 4 cells provide a useful operating scale for both:

- FeatureServer query size;
- ArcGIS Earth GeoJSON parsing/memory load.

This also aligns parcel intelligence with the existing Master 4/TKPX geographic addressing system.

## Other states / public release strategy

Parcel100 is intentionally not hardcoded to the Florida schema.

The public workflow is:

1. user locates a public ArcGIS parcel FeatureServer polygon layer;
2. user pastes `/FeatureServer/<layer id>` into Parcel100;
3. **Read Service** discovers its fields;
4. user selects that jurisdiction's useful owner/address/parcel fields;
5. normal Master 4 build proceeds.

The **Recommended** selection is exact for known Florida fields first, then uses generic owner/address/parcel/APN/PIN-style keyword matching as a fallback for other services.

## Current limitations

- no authentication/token workflow;
- polygon FeatureServer layers only;
- no automatic state/county service discovery;
- no automatic reload/resume from a partially completed run;
- no cell deduplication at shared boundaries;
- no automatic ArcGIS Earth cell loading from GPS yet;
- no built-in state profiles beyond the Florida URL/field preference;
- service terms/field meanings/data quality vary by provider.

## Strong future extensions

Do not implement these automatically without explicit project direction, but they are natural next steps:

- source profiles for known state/county parcel services;
- save/load selected-field profiles;
- optional resume mode for interrupted large runs;
- cell manifest/index file;
- integration with a future Substitute Drone launcher so GPS determines the current Master 4 cell and loads the matching parcel GeoJSON;
- load current parcel cell plus surrounding neighbors on demand;
- public examples for states with different parcel schemas.

## Presentation concept

Parcel100 is strongest when shown as a late reveal in the broader offline-map/Substitute Drone demonstration.

After showing offline multiresolution TPKX imagery, GPS, operational overlays and navigation, the demonstration can simply say:

> "Let's just verify who owns the property."

Then click the local GeoJSON parcel and show the owner/address popup.

The important message is not that parcel overlays are new. The project value is that public parcel intelligence has been converted into small, deterministic, offline local files that travel with the same geographic system as the offline imagery.

## Compatibility warning

Preserve the existing Master 4 numbering and deterministic filename contract unless an intentional version change is made.

The 100-cell geography is now shared infrastructure across multiple offline-map/intelligence workflows.
