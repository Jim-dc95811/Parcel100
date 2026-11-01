# Parcel100 Technical Documentation

This folder contains the implementation record and visual explainers for Parcel100.

## Current technical notes

- [Current Parcel100 v1.5 technical notes](../TECHNICAL.md)
- [Parcel100 1.5 change document](PARCEL100_V1.5_CHANGES.md)

These notes reflect the current source, including service-root discovery, resume with incomplete-cell rebuild, visible retries, four-part difficult-cell fallback, batch splitting, the per-parcel completeness check, the Florida Acres field, and `.partial` then rename file writes.

## Detailed architecture record

- [Parcel100 GeoJSON Construction Technical Design (PDF)](Parcel100_GeoJSON_Construction_Technical_Design.pdf)

The PDF is the detailed v1.3 engineering record for the core extraction/conversion architecture. Its retry/resume/fallback design remains relevant to v1.5, but use `TECHNICAL.md` for the current release state and field-selection details.

## Current ArcGIS Earth acceptance evidence

- [Parcel100 popup in ArcGIS Earth](../images/parcel100_popup_arcgis_earth.jpg)

This screenshot shows Parcel100 output in ArcGIS Earth with parcel ID, owner, physical address, city, ZIP and Acres visible as clickable attributes.

## Diagrams and artwork

- [Parcel100 pipeline](images/pipeline.svg)
- [Master 4 / 100-cell numbering](images/cell_numbering.svg)
- [Esri rings to GeoJSON geometry](images/geometry_conversion.svg)
- [How Parcel100 Works — four-step explainer](images/how_parcel100_works.svg)
- [Parcel100 video thumbnail artwork](images/parcel100_thumbnail.svg)

These SVG files are repository-native, scalable versions of the Parcel100 graphics and can be opened directly in a browser or reused in documentation and video production.
