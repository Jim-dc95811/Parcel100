# Parcel100 Technical Documentation

This folder contains the technical design record and visual explainers for Parcel100.

## Technical design

- [Parcel100 GeoJSON Construction Technical Design (PDF)](Parcel100_GeoJSON_Construction_Technical_Design.pdf)

The technical design documents the complete construction path from a Master 4 input to the final per-cell GeoJSON files, including FeatureServer metadata discovery, spatial Object ID queries, batching, EPSG:4326 output, Esri ring reconstruction, file naming, resume behavior, retries, the four-part difficult-cell fallback, and observed production behavior of the tested Florida services.

## Diagrams and artwork

- [Parcel100 pipeline](images/pipeline.svg)
- [Master 4 / 100-cell numbering](images/cell_numbering.svg)
- [Esri rings to GeoJSON geometry](images/geometry_conversion.svg)
- [How Parcel100 Works — four-step explainer](images/how_parcel100_works.svg)
- [Parcel100 video thumbnail artwork](images/parcel100_thumbnail.svg)

These SVG files are repository-native, scalable versions of the Parcel100 graphics and can be opened directly in a browser or reused in documentation and video production.
