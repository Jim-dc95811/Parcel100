# Parcel100 Release Checklist

Use this checklist before publishing a new Parcel100 package.

## Program startup

- `Parcel100.py` compiles without syntax errors.
- `Parcel100.bat` starts the GUI on a normal Windows Python 3 installation.
- GUI title/version matches the intended release.

## Service discovery

- Florida preset loads successfully.
- **Read Service** populates the field list.
- Field aliases display where available.
- Non-polygon FeatureServer layers are rejected clearly.
- Bad/unreachable service URLs produce an error instead of hanging silently.

## Master 4 compatibility

- Input order remains `west,east,south,north`.
- Whole-degree 1 x 1 box validation still works.
- Cell numbering remains compatible with the Master4 Grid Maker.
- Output filenames remain deterministic.

Example:

```text
82w,81w,30n,31n
-> W082W081N031N030-001-Parcels.geojson
```

## Field behavior

- User can select only desired fields.
- Florida **Recommended** still selects:

```text
OWN_NAME
PHY_ADDR1
PHY_CITY
PHY_ZIPCD
PARCEL_ID
```

- Custom-service fields are not incorrectly replaced by Florida names.

## Empty cells and errors

- Valid zero-result cells are skipped.
- No empty GeoJSON file is written for skipped cells.
- A service/network failure is not misreported as an empty cell.
- Completion totals accurately report files written and empty cells skipped.

## Feature retrieval

- Object-ID query works for populated cells.
- Feature download batches respect reported service limits.
- Only selected attributes are requested.
- `returnZ=false` and `returnM=false` remain in the feature query.
- Output geometry is requested in EPSG:4326.

## Geometry

Test at least:

- simple parcel polygon;
- parcel with a hole if available;
- multipart/multipolygon parcel;
- cell-edge parcel that intersects two neighboring cells.

Confirm the GeoJSON opens in a real GIS/viewer and the geometry is visually correct.

## ArcGIS Earth acceptance

- Open at least one current-release GeoJSON in ArcGIS Earth.
- Confirm parcel geometry lands in the expected location.
- Click a parcel and verify selected attributes appear in the popup.
- Load several neighboring cells together and confirm they coexist cleanly.

## Package

The ZIP should contain:

```text
Parcel100/
  Parcel100.py
  Parcel100.bat
  README.txt
```

- ZIP filename includes the correct release version.
- README quick-start text matches current behavior.
- Repository `downloads/` link points to the current package.

## Documentation

Review/update as needed:

- `README.md`
- `USER_MANUAL.md`
- `TECHNICAL.md`
- `CHANGELOG.md`
- `CONTINUITY.md`
- `LEGAL.md`
- `CREDITS.md`

## Public-data caution

Before documenting a new preset/service:

- confirm the URL is publicly accessible;
- identify the publisher/source;
- do not imply ownership of the parcel data;
- do not bundle downloaded owner records in the repository;
- avoid claiming survey/legal accuracy;
- note that source terms and update schedules remain provider-specific.
