import json
import math
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "Parcel100"
VERSION = "1.1"
FLORIDA_URL = "https://services5.arcgis.com/GcvM6vDlR2gM4x31/arcgis/rest/services/FL_Parcels/FeatureServer/0"
DEFAULT_MASTER4 = "82w,81w,30n,31n"
DEFAULT_PRECISION = 7
TIMEOUT = 90
RETRIES = 3

# These are only preferences for the known Florida layer. Other services are
# discovered from their own metadata and the user chooses the fields.
FLORIDA_PREFERRED_FIELDS = [
    "OWN_NAME",
    "PHY_ADDR1",
    "PHY_CITY",
    "PHY_ZIPCD",
    "PARCEL_ID",
]


def parse_coord(token, longitude):
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([NSEWnsew])\s*", token)
    if not match:
        raise ValueError(f"Invalid coordinate: {token.strip()}")
    value = float(match.group(1))
    direction = match.group(2).upper()
    if longitude and direction not in ("E", "W"):
        raise ValueError(f"Longitude must end in E or W: {token.strip()}")
    if not longitude and direction not in ("N", "S"):
        raise ValueError(f"Latitude must end in N or S: {token.strip()}")
    if longitude and value > 180:
        raise ValueError("Longitude must be 180 degrees or less.")
    if not longitude and value > 90:
        raise ValueError("Latitude must be 90 degrees or less.")
    if direction in ("W", "S"):
        value = -value
    return value


def parse_master4(text):
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 4:
        raise ValueError("Enter four coordinates: west,east,south,north")
    west = parse_coord(parts[0], True)
    east = parse_coord(parts[1], True)
    south = parse_coord(parts[2], False)
    north = parse_coord(parts[3], False)
    if west >= east:
        raise ValueError("The first longitude must be the west edge.")
    if south >= north:
        raise ValueError("The third latitude must be the south edge.")
    if not math.isclose(east - west, 1.0, abs_tol=1e-9):
        raise ValueError("Master 4 longitude edges must be exactly 1 degree apart.")
    if not math.isclose(north - south, 1.0, abs_tol=1e-9):
        raise ValueError("Master 4 latitude edges must be exactly 1 degree apart.")
    for value, name in ((west, "west"), (east, "east"), (south, "south"), (north, "north")):
        if not math.isclose(value, round(value), abs_tol=1e-9):
            raise ValueError(f"Master 4 {name} edge must be a whole degree.")
    label = "_".join(p.upper().replace(" ", "") for p in parts)
    return west, east, south, north, label


def cell_bounds(west, east, south, north):
    """Match the established Master4 Grid Maker 01-100 cell numbering."""
    records = []
    west_side = east <= 0.0
    south_side = north <= 0.0
    lon_base = abs(east) if west_side else abs(west)
    lat_base = abs(north) if south_side else abs(south)

    for cell_id in range(1, 101):
        row_digit = (cell_id - 1) // 10
        col_digit = (cell_id - 1) % 10

        if west_side:
            lon_w = -(lon_base + (col_digit + 1) / 10.0)
            lon_e = -(lon_base + col_digit / 10.0)
        else:
            lon_w = lon_base + col_digit / 10.0
            lon_e = lon_base + (col_digit + 1) / 10.0

        if south_side:
            lat_s = -(lat_base + (row_digit + 1) / 10.0)
            lat_n = -(lat_base + row_digit / 10.0)
        else:
            lat_s = lat_base + row_digit / 10.0
            lat_n = lat_base + (row_digit + 1) / 10.0

        records.append((cell_id, lon_w, lon_e, lat_s, lat_n))
    return records


def padded_master_label(master_label):
    parts = master_label.split("_")
    if len(parts) != 4:
        return master_label.replace(",", "_")

    def padded(token):
        value = int(float(token[:-1]))
        direction = token[-1].upper()
        return f"{direction}{value:03d}"

    west, east, south, north = (padded(p) for p in parts)
    return f"{west}{east}{north}{south}"


def output_name(master_label, cell_id):
    return f"{padded_master_label(master_label)}-{cell_id:03d}-Parcels.geojson"


def _request(url, params, expect_json=True):
    data = urllib.parse.urlencode(params).encode("utf-8")
    last_error = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "User-Agent": f"{APP_NAME}/{VERSION}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json, application/geo+json, */*",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                raw = response.read()
            if not expect_json:
                return raw
            result = json.loads(raw.decode("utf-8"))
            if isinstance(result, dict) and "error" in result:
                err = result["error"]
                msg = err.get("message", "ArcGIS service error") if isinstance(err, dict) else str(err)
                details = err.get("details", []) if isinstance(err, dict) else []
                if details:
                    msg += " — " + "; ".join(str(x) for x in details)
                raise RuntimeError(msg)
            return result
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < RETRIES:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(str(last_error))


def read_service(layer_url):
    layer_url = layer_url.rstrip("/")
    meta = _request(layer_url, {"f": "json"})
    if meta.get("type") not in ("Feature Layer", None):
        raise ValueError("URL does not appear to be an ArcGIS FeatureServer layer.")
    if meta.get("geometryType") != "esriGeometryPolygon":
        raise ValueError(f"Parcel100 requires a polygon layer. Service reports: {meta.get('geometryType')}")
    fields = meta.get("fields") or []
    if not fields:
        raise ValueError("No fields were reported by the service.")
    return meta


def _query_endpoint(layer_url):
    return layer_url.rstrip("/") + "/query"


def query_object_ids(layer_url, bbox):
    w, e, s, n = bbox
    params = {
        "f": "json",
        "where": "1=1",
        "geometry": f"{w:.10f},{s:.10f},{e:.10f},{n:.10f}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
        "returnGeometry": "false",
    }
    data = _request(_query_endpoint(layer_url), params)
    return data.get("objectIds") or [], data.get("objectIdFieldName")


def _signed_area(ring):
    total = 0.0
    if len(ring) < 3:
        return 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % len(ring)][0], ring[(i + 1) % len(ring)][1]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def _close_ring(ring):
    pts = [[float(p[0]), float(p[1])] for p in ring if p is not None and len(p) >= 2]
    if pts and pts[0] != pts[-1]:
        pts.append(pts[0][:])
    return pts


def _point_in_ring(point, ring):
    x, y = point
    inside = False
    if len(ring) < 4:
        return False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) if (yj - yi) != 0 else 1e-300) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def _representative_point(ring):
    # A ring vertex is adequate for the containment test in ordinary parcel data.
    # If it sits on another ring boundary, try subsequent vertices.
    if not ring:
        return (0.0, 0.0)
    for p in ring[:-1] if len(ring) > 1 else ring:
        return (p[0], p[1])
    return (ring[0][0], ring[0][1])


def esri_rings_to_geojson(rings):
    clean = [_close_ring(r) for r in (rings or [])]
    clean = [r for r in clean if len(r) >= 4 and abs(_signed_area(r)) > 0]
    if not clean:
        return None

    # Build a containment tree independent of ring winding direction. This
    # handles services that do not consistently preserve Esri winding rules.
    info = []
    for idx, ring in enumerate(clean):
        info.append({"idx": idx, "ring": ring, "area": abs(_signed_area(ring)), "parent": None, "depth": 0})

    by_area = sorted(info, key=lambda x: x["area"])
    for item in by_area:
        point = _representative_point(item["ring"])
        candidates = [x for x in info if x["area"] > item["area"] and _point_in_ring(point, x["ring"])]
        if candidates:
            item["parent"] = min(candidates, key=lambda x: x["area"])["idx"]

    index_map = {x["idx"]: x for x in info}
    for item in info:
        depth = 0
        parent = item["parent"]
        seen = set()
        while parent is not None and parent not in seen:
            seen.add(parent)
            depth += 1
            parent = index_map[parent]["parent"]
        item["depth"] = depth

    polygons = []
    for outer in [x for x in info if x["depth"] % 2 == 0]:
        coords = [outer["ring"]]
        holes = [
            x for x in info
            if x["parent"] == outer["idx"] and x["depth"] == outer["depth"] + 1
        ]
        coords.extend(h["ring"] for h in holes)
        polygons.append(coords)

    if len(polygons) == 1:
        return {"type": "Polygon", "coordinates": polygons[0]}
    return {"type": "MultiPolygon", "coordinates": polygons}


def esri_feature_to_geojson(feature, selected_fields):
    attrs = feature.get("attributes") or {}
    props = {name: attrs.get(name) for name in selected_fields}
    geom = feature.get("geometry")
    if geom is None:
        geometry = None
    elif "rings" in geom:
        geometry = esri_rings_to_geojson(geom.get("rings"))
    else:
        raise ValueError("Service returned a non-polygon geometry.")
    return {"type": "Feature", "properties": props, "geometry": geometry}


def query_features_json(layer_url, ids, fields, precision, batch_size):
    if not ids:
        return []
    features = []
    endpoint = _query_endpoint(layer_url)
    for start in range(0, len(ids), batch_size):
        batch = ids[start:start + batch_size]
        params = {
            "f": "json",
            "objectIds": ",".join(str(x) for x in batch),
            "outFields": ",".join(fields),
            "returnGeometry": "true",
            "outSR": "4326",
            "returnZ": "false",
            "returnM": "false",
            "geometryPrecision": str(precision),
        }
        data = _request(endpoint, params)
        for feature in data.get("features") or []:
            features.append(esri_feature_to_geojson(feature, fields))
    return features


def write_feature_collection(path, features, master_label, cell_id, bbox, source_url):
    w, e, s, n = bbox
    collection = {
        "type": "FeatureCollection",
        "name": path.stem,
        "bbox": [w, s, e, n],
        "master4": master_label,
        "cell": cell_id,
        "source": source_url,
        "features": features,
    }
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(collection, f, ensure_ascii=False, separators=(",", ":"))


def recommended_indices(fields):
    names = [f.get("name", "") for f in fields]
    upper = [n.upper() for n in names]
    chosen = []

    # Exact known Florida fields first.
    for preferred in FLORIDA_PREFERRED_FIELDS:
        if preferred in upper:
            chosen.append(upper.index(preferred))

    if chosen:
        return sorted(set(chosen))

    # Portable fallback for other states/counties.
    keywords = (
        "OWNER", "OWN_NAME", "OWNNAME", "ONAME",
        "ADDRESS", "ADDR", "SITE", "PHYS", "PHY_",
        "PARCEL", "PARCELID", "PARCEL_ID", "APN", "PIN",
        "CITY", "ZIP",
    )
    for i, name in enumerate(upper):
        if any(k in name for k in keywords):
            chosen.append(i)
    return sorted(set(chosen))[:12]


class Parcel100App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("860x690")
        self.minsize(760, 620)
        self.meta = None
        self.fields = []
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Master 4", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.master_var = tk.StringVar(value=DEFAULT_MASTER4)
        ttk.Entry(outer, textvariable=self.master_var).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 8))
        ttk.Label(outer, text="Example: 82w,81w,30n,31n   (west,east,south,north)").grid(row=2, column=0, columnspan=3, sticky="w")

        ttk.Label(outer, text="ArcGIS FeatureServer polygon layer URL", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.url_var = tk.StringVar(value=FLORIDA_URL)
        ttk.Entry(outer, textvariable=self.url_var).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        self.read_btn = ttk.Button(outer, text="Read Service", command=self.read_service_clicked)
        self.read_btn.grid(row=4, column=2, sticky="ew", padx=(8, 0))

        ttk.Label(outer, text="Fields to keep in each GeoJSON", font=("Segoe UI", 10, "bold")).grid(row=5, column=0, sticky="w", pady=(12, 2))

        field_frame = ttk.Frame(outer)
        field_frame.grid(row=6, column=0, columnspan=3, sticky="nsew")
        self.field_list = tk.Listbox(field_frame, selectmode=tk.EXTENDED, exportselection=False, height=16)
        field_scroll = ttk.Scrollbar(field_frame, orient="vertical", command=self.field_list.yview)
        self.field_list.configure(yscrollcommand=field_scroll.set)
        self.field_list.pack(side="left", fill="both", expand=True)
        field_scroll.pack(side="right", fill="y")

        btns = ttk.Frame(outer)
        btns.grid(row=7, column=0, columnspan=3, sticky="w", pady=(6, 8))
        ttk.Button(btns, text="Recommended", command=self.select_recommended).pack(side="left")
        ttk.Button(btns, text="Select All", command=lambda: self.field_list.select_set(0, tk.END)).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="Clear", command=lambda: self.field_list.selection_clear(0, tk.END)).pack(side="left", padx=(6, 0))

        ttk.Label(outer, text="Output folder", font=("Segoe UI", 10, "bold")).grid(row=8, column=0, sticky="w", pady=(4, 0))
        default_dir = Path.home() / "Downloads" / "Parcel100"
        self.output_var = tk.StringVar(value=str(default_dir))
        ttk.Entry(outer, textvariable=self.output_var).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        ttk.Button(outer, text="Browse", command=self.browse_output).grid(row=9, column=2, sticky="ew", padx=(8, 0))

        opts = ttk.Frame(outer)
        opts.grid(row=10, column=0, columnspan=3, sticky="w", pady=(8, 8))
        ttk.Label(opts, text="Coordinate precision:").pack(side="left")
        self.precision_var = tk.IntVar(value=DEFAULT_PRECISION)
        ttk.Spinbox(opts, from_=5, to=12, width=5, textvariable=self.precision_var).pack(side="left", padx=(6, 18))
        ttk.Label(opts, text="Up to 100 files; empty cells are skipped (01-100)").pack(side="left")

        self.build_btn = ttk.Button(outer, text="BUILD 100 GEOJSON FILES", command=self.build_clicked)
        self.build_btn.grid(row=11, column=0, columnspan=3, sticky="ew", pady=(6, 8), ipady=5)

        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100)
        self.progress.grid(row=12, column=0, columnspan=3, sticky="ew")
        self.status_var = tk.StringVar(value="Ready. Read the service first.")
        ttk.Label(outer, textvariable=self.status_var).grid(row=13, column=0, columnspan=3, sticky="w", pady=(6, 0))

        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)
        outer.columnconfigure(2, weight=0)
        outer.rowconfigure(6, weight=1)

    def set_busy(self, busy):
        state = "disabled" if busy else "normal"
        self.read_btn.configure(state=state)
        self.build_btn.configure(state=state)

    def browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get() or str(Path.home()))
        if folder:
            self.output_var.set(folder)

    def read_service_clicked(self):
        if self.worker and self.worker.is_alive():
            return
        self.set_busy(True)
        self.status_var.set("Reading service metadata...")
        self.worker = threading.Thread(target=self._read_service_worker, daemon=True)
        self.worker.start()

    def _read_service_worker(self):
        try:
            meta = read_service(self.url_var.get().strip())
            fields = [f for f in meta.get("fields", []) if f.get("type") != "esriFieldTypeGeometry"]
            self.after(0, self._load_fields, meta, fields)
        except Exception as exc:
            self.after(0, self._error, f"Could not read service:\n\n{exc}")

    def _load_fields(self, meta, fields):
        self.meta = meta
        self.fields = fields
        self.field_list.delete(0, tk.END)
        for f in fields:
            name = f.get("name", "")
            alias = f.get("alias", "")
            line = name if not alias or alias == name else f"{name}    [{alias}]"
            self.field_list.insert(tk.END, line)
        self.select_recommended()
        max_count = meta.get("maxRecordCount", 2000)
        layer_name = meta.get("name", "Feature layer")
        self.status_var.set(f"Loaded {len(fields)} fields from {layer_name}. Max record count: {max_count}.")
        self.set_busy(False)

    def select_recommended(self):
        self.field_list.selection_clear(0, tk.END)
        if not self.fields:
            return
        for idx in recommended_indices(self.fields):
            self.field_list.selection_set(idx)
        if self.field_list.curselection():
            self.field_list.see(self.field_list.curselection()[0])

    def _selected_field_names(self):
        return [self.fields[i].get("name") for i in self.field_list.curselection()]

    def build_clicked(self):
        if self.worker and self.worker.is_alive():
            return
        if self.meta is None:
            messagebox.showerror(APP_NAME, "Read the FeatureServer first.")
            return
        try:
            master = parse_master4(self.master_var.get())
            precision = int(self.precision_var.get())
            if precision < 5 or precision > 12:
                raise ValueError("Coordinate precision must be between 5 and 12.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return
        fields = self._selected_field_names()
        if not fields:
            messagebox.showerror(APP_NAME, "Select at least one field to keep.")
            return
        out_dir = Path(self.output_var.get().strip())
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Cannot create output folder:\n{exc}")
            return

        self.progress["value"] = 0
        self.set_busy(True)
        self.status_var.set("Starting...")
        self.worker = threading.Thread(
            target=self._build_worker,
            args=(master, fields, precision, out_dir),
            daemon=True,
        )
        self.worker.start()

    def _build_worker(self, master, fields, precision, out_dir):
        west, east, south, north, label = master
        cells = cell_bounds(west, east, south, north)
        max_count = int(self.meta.get("maxRecordCount") or 2000)
        batch_size = max(1, min(max_count, 2000))
        url = self.url_var.get().strip().rstrip("/")
        total_features = 0
        files_written = 0
        empty_cells = 0
        try:
            for index, (cell_id, w, e, s, n) in enumerate(cells, start=1):
                self.after(0, self.status_var.set, f"Cell {cell_id:03d}: finding parcels...")
                ids, _ = query_object_ids(url, (w, e, s, n))
                if not ids:
                    empty_cells += 1
                    self.after(0, self.status_var.set, f"Cell {cell_id:03d}: EMPTY - skipped")
                    self.after(0, self.progress.configure, {"value": index})
                    continue

                self.after(0, self.status_var.set, f"Cell {cell_id:03d}: downloading {len(ids):,} parcels...")
                features = query_features_json(url, ids, fields, precision, batch_size)
                total_features += len(features)
                path = out_dir / output_name(label, cell_id)
                write_feature_collection(path, features, label, cell_id, (w, e, s, n), url)
                files_written += 1
                self.after(0, self.progress.configure, {"value": index})
            self.after(0, self._build_done, out_dir, total_features, files_written, empty_cells)
        except Exception as exc:
            self.after(0, self._error, f"Build stopped:\n\n{exc}")

    def _build_done(self, out_dir, total_features, files_written, empty_cells):
        self.set_busy(False)
        self.status_var.set(
            f"Complete: {files_written} GeoJSON files, {empty_cells} empty cells skipped, "
            f"{total_features:,} parcel records written."
        )
        messagebox.showinfo(
            APP_NAME,
            f"Complete.\n\n{files_written} GeoJSON files written to:\n{out_dir}"
            f"\n\n{empty_cells} empty cells skipped."
        )

    def _error(self, message):
        self.set_busy(False)
        self.status_var.set("Stopped.")
        messagebox.showerror(APP_NAME, message)


def main():
    app = Parcel100App()
    app.mainloop()


if __name__ == "__main__":
    main()
