# Legal, Data and Privacy Notes

Parcel100 is software for querying public ArcGIS FeatureServer polygon layers and writing selected features/attributes to local GeoJSON files. It does not itself provide parcel ownership data.

## Source rights and service rules

The operator is responsible for confirming that the source service may be accessed, queried, retained and reused for the intended purpose.

A layer being visible in a public web map does not automatically answer every question about redistribution, bulk downloading, commercial use, privacy, or retention. Review the publisher's terms, metadata and applicable law.

Parcel100 does not bypass authentication, tokens, paywalls, access controls or private services.

## Public-record data

Parcel services can expose owner names, mailing addresses, physical/site addresses, parcel identifiers, acreage/area fields, assessed values, sale information and other public-record attributes.

Select only the fields needed for the intended field workflow. The lean Florida v1.4 demonstration uses owner name, physical address, city, ZIP code, parcel ID and Acres rather than copying the entire tax/assessment schema.

Users are responsible for handling exported records consistently with applicable privacy, public-record, agency and organizational requirements.

## Accuracy

Parcel GIS is not a land survey or title opinion.

Boundaries can be generalized, shifted, incomplete or stale. Attribute data can lag ownership changes. A physical/site address may not represent current occupancy, and a mailing address can belong to an owner or entity located elsewhere. Acreage/area attributes can also differ from surveyed or deeded area.

For legal boundary, title, ownership, access, acreage or tax decisions, verify with the responsible property appraiser, recorder, deed, survey or other authoritative source.

## Operational use

Parcel100 output can be useful for situational awareness, planning and field reference, but critical operational decisions should not depend on an unverified parcel layer alone.

## Florida preset

Parcel100 v1.4 includes this public Florida parcel FeatureServer URL as a convenience preset:

```text
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0
```

Florida parcel-data attribution:

**Florida's county property appraisers; Florida Department of Revenue Property Tax Oversight.**

The preset is not a claim of ownership of the data and does not change the publisher's rights, terms, update schedule or responsibilities.

## Trademarks and independence

ArcGIS and ArcGIS Earth are trademarks/products of Esri. QGIS is an independent open-source GIS project.

Parcel100 is an independent project and is not affiliated with or endorsed by Esri, QGIS, the Florida Department of Revenue, FloridaGIO, or any state/county property appraiser.

## Software license

The Parcel100 source code in this repository is released under the MIT License. See [LICENSE](LICENSE).

The MIT License applies to the software, not to third-party parcel data downloaded through the software.
