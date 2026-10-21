# Finding a Parcel FeatureServer in Your State or County

Parcel100 is not limited to Florida, but it needs the **actual ArcGIS FeatureServer polygon layer URL** that publishes the parcel data.

The hardest part for a new user is often finding that URL. A public web map is only the front end; Parcel100 needs the data service underneath it.

## What you are looking for

A working Parcel100 source normally looks like:

```text
https://services#.arcgis.com/.../arcgis/rest/services/.../FeatureServer/0
```

The final number can be `0`, `1`, `2`, etc. depending on which layer contains the parcel polygons.

## Method 1: ArcGIS Online item page

If you find an official parcel web map:

1. Open its ArcGIS Online item/details page.
2. Look for **Items used**, **Layers**, or the parcel feature layer listed by the map.
3. Open the parcel feature layer item.
4. Look for the service URL or open the REST endpoint.
5. Continue until you are at the actual numbered FeatureServer layer.

Do not stop at a URL like:

```text
https://www.arcgis.com/apps/mapviewer/...
```

That is the map application, not the parcel layer.

## Method 2: ArcGIS REST Services Directory

Government GIS sites often expose an ArcGIS REST services directory.

Search the site or web for terms such as:

```text
<state> parcel FeatureServer
<county> parcels ArcGIS REST
<county> property FeatureServer
<state GIS> cadastral FeatureServer
```

A useful REST layer page will usually show information such as:

```text
Name
Type: Feature Layer
Geometry Type: esriGeometryPolygon
Fields
Object ID Field
Max Record Count
Spatial Reference
```

Parcel100 requires polygon geometry.

## Method 3: QGIS as a discovery/verification tool

QGIS can be useful for verifying a candidate ArcGIS REST service before using Parcel100.

1. Open **Data Source Manager**.
2. Choose **ArcGIS REST Server**.
3. Add the FeatureServer URL.
4. Connect and add the parcel layer.
5. Zoom into a neighborhood/property scale.
6. Confirm parcel polygons draw.
7. Open the attribute table or Identify tool and confirm the fields contain useful parcel information.

Once the service is verified, production can move to Parcel100; no QGIS project is required for the actual 100-cell build.

## Verify the fields

Different jurisdictions use different field names.

Common examples:

```text
OWNER
OWN_NAME
OWNER_NAME
SITE_ADDR
PHY_ADDR1
ADDRESS
APN
PIN
PARCEL_ID
PARCELNO
ACRES
ACREAGE
AREA
```

Parcel100 shows both the field name and alias reported by the service so you can choose the fields that matter.

The current Florida preset's Recommended selection includes owner name, physical address, city, ZIP, parcel ID and Acres when those fields are present.

## Statewide vs county-by-county

Some states publish one statewide parcel service. Others do not.

Possible arrangements include:

- one statewide parcel FeatureServer;
- separate county FeatureServers;
- regional services;
- parcel data published only through downloads instead of a public FeatureServer;
- public maps whose underlying service requires authentication or has restrictions.

Parcel100 v1.4 works with one public polygon FeatureServer layer at a time.

## Confirm coverage before a large build

A Master 4 can cross:

- state lines;
- county lines;
- ocean;
- areas outside the service's jurisdiction.

That is okay. Parcel100 sends a lightweight ID query for each unfinished one of the 100 cells and skips cells where the selected service returns no parcels.

If a cell intersects the service coverage, only the features exposed by that service are returned.

If a public service is unstable, Parcel100 retries transient failures. A full-cell ID query that repeatedly fails with a recognized transient error can automatically switch to four smaller internal ID-query envelopes without changing the normal one-file-per-cell output.

## Resume behavior

If a long build is interrupted, use the same Master 4 and the same output folder. Parcel100 checks the deterministic expected filename before querying each cell and skips existing outputs.

If you intentionally want to rebuild a cell, delete that cell's GeoJSON first.

## Do not assume public means unrestricted

Before bulk downloading or redistributing parcel data, review the publisher's metadata, terms and applicable laws.

Parcel100 does not bypass login requirements or access controls.

## Florida reference example

The known-good Florida development layer is:

```text
https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0
```

Use it as a reference for what a valid Parcel100 source URL looks like, not as a template that every jurisdiction will match exactly.
