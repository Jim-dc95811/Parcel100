# Credits

## Project direction and field validation

**Jim Gaddy** conceived the operational use case, supplied the Master 4 architecture, performed the real FeatureServer experiments, defined the field workflow, tested large parcel exports, validated the 100-cell production approach, and confirmed the resulting GeoJSON layers in ArcGIS Earth.

## AI coding and documentation assistance

**OpenAI's ChatGPT** assisted with ArcGIS FeatureServer query design, Python implementation, geometry conversion logic, troubleshooting, documentation and repository preparation.

This acknowledgment is not a claim of OpenAI sponsorship or endorsement.

## Technologies and specifications

Parcel100 relies on publicly documented technologies rather than proprietary bundled parcel data:

- Python standard library
- Tkinter GUI toolkit
- ArcGIS REST Feature Service query interface
- GeoJSON feature format
- WGS 84 / EPSG:4326 geographic coordinates

## Companion project

Parcel100 uses the 01-100 cell addressing established by the companion Master 4 Grid Maker in:

`Jim-dc95811/QGIS-Mbtile-to-ArcGIS-Earth-TPKX`

The shared geography allows offline raster imagery and parcel-intelligence cells to use the same deterministic Master 4 addressing system.

## Data providers

Parcel data belongs to its respective publishers/providers. The built-in Florida preset points to a public statewide parcel FeatureServer used during development. Parcel100 does not claim ownership of those records.
