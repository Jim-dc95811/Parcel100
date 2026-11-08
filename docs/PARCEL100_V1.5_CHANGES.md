# Parcel100 1.5 - change document

**Released:** 2026-11-01
**Type:** discovery and hardening release.
**Download:** [`archive/Parcel100_v1.5.zip`](../archive/Parcel100_v1.5.zip)

**For a normal build the output is unchanged.** Master 4 cells, file names, the ID query and its four-part fallback, batching, polygon conversion and the GeoJSON layout are the same as 1.4. For an ordinary service, 1.5 writes the same 100 files as 1.4, byte for byte.

## What changed

### 1. Paste the service, not just the layer (Jim's 1.5)

**1.4** needed the exact polygon layer URL, ending in `/FeatureServer/<layer id>`.

**1.5** also accepts the service itself, ending in `/FeatureServer` or `/MapServer`. Read Service checks the layers:
- one polygon layer: it is used directly;
- several polygon layers: a chooser lists them so you pick the parcels.

### 2. Discovery tells you what it could not check

- The status line shows `Checking layer N of M: <name>...` while it works.
- A layer that does not respond (for example a 504 from a busy server) is listed in orange in the chooser. If it might be the parcel layer, Cancel and try again later, or paste that layer's own URL.
- If no polygon layer could be confirmed because layers did not respond, Read Service says which ones, instead of reporting that the service has no polygon layer.
- A URL copied with `/query` or `/query?...` on the end is accepted.

### 3. An interrupted build can no longer leave a broken cell

**1.4** wrote each cell straight into its final `.geojson`. If the window was closed part-way through a write, a half-written file was left behind. On the next run, resume saw the file name and skipped it, so that cell stayed broken.

**1.5:**
- Writes each cell as `.geojson.partial` and renames it only when complete.
- On resume, checks that an existing cell file is complete GeoJSON. One that is not (for example, left by an older version) is rebuilt and listed in the completion message.

### 4. Every parcel is accounted for (write and warn)

**1.4** never checked that the service returned every parcel it listed for a cell. A server that quietly returned fewer was written short, with no warning.

**1.5:**
- Checks every parcel ID off as features arrive. To do that it also requests the object-ID field, but only the fields you chose are written.
- Asks once more for any parcels that are missing.
- If some are still missing, writes the cell and lists it in a warning at the end, e.g.:

```text
WARNING: the service did not return some parcels, even after asking again.
These cells were written without them:
  Cell 037: 2 of 36 parcels
To try those cells again later, delete their files and build again.
```

### 5. Timed-out download batches are split

**1.4:** a feature batch that kept timing out (504 and similar) stopped the whole build after three tries.

**1.5:** such a batch is split in half and each half is requested, down to single parcels. The status line shows `batch of N parcels timed out - splitting...`. A non-timeout error, or one parcel that keeps failing, still stops the build.

### 6. The build uses the layer that was read

**1.4** built from whatever was in the URL box at BUILD time, even if it had been edited after Read Service, so the field list could belong to a different layer.

**1.5** remembers the layer that was read. If the URL box is changed afterwards, BUILD asks you to click Read Service again.

The window title and package README show 1.5. `Parcel100.bat` is unchanged.

## Verification

- **Live acceptance:** Jim Gaddy tested 1.5 on Windows with ArcGIS Earth on 2026-11-01 and confirmed it working well.
- **Regression against 1.4:** run against a stand-in ArcGIS FeatureServer (3,600 parcels over 100 cells), so not a live service. All 100 GeoJSON files were byte-identical to 1.4, apart from the test server's port number in the `source` line.
- **Hardening tests:**

| Scenario | 1.4 | 1.5 |
|---|---|---|
| Window closed while writing cell 37, then resumed | broken cell kept and skipped | no broken file; a planted truncated file was rebuilt |
| Server leaves out parcels in every request | 2,800 of 3,600 written, no warning | 3,400 written after asking again; the 200 never returned reported per cell |
| Server times out on batches over 20 parcels | build stopped | all 3,600 written |
| URL edited after Read Service | built from the new URL | asks for Read Service again |

- **Discovery tests:** a service root with a timed-out layer listed it as unchecked; a root where every polygon layer timed out gave the "could not be confirmed" message naming them; layer URLs, point layers, MapServer roots and `/query?...` URLs behaved as described above.

## Checksums

| File | SHA-256 |
|---|---|
| `Parcel100.py` 1.5 | `ba0627bcfccf65e866a1515f1d70ad8069b4d8475d6542e20431bdbe613235b1` |
| `Parcel100.py` 1.4 (previous) | `5693c5c663e349569fad8e764ea790111ca044e9b2eed4bfba80b1511a9e408c` |

The download zip is rebuilt automatically by the repository's GitHub Actions workflow (now set to `Parcel100_v1.5.zip`), so its own checksum can change with each rebuild; the `Parcel100.py` inside it is the file above. `archive/Parcel100_v1.4.zip` stays in the repository so existing links keep working.
