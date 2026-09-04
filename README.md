# <img src="VolumeSpan_internal/icons/volumespan_cd_icon.svg" width="32" height="32"> VolumeSpan™ <img src="VolumeSpan_internal/icons/volumespan_cd_icon.svg" width="32" height="32">
**An automated optical disc backup staging utility utilizing native NTFS hardlinks.**

---

## Overview
VolumeSpan™ is a backup staging application designed to partition large local directory trees sequentially into fixed-capacity optical disc volumes (e.g., **BD-0001**, **BD-0002**) using native NTFS hardlinks. It allows you to organize data for optical burning—such as BDXL, BD-R, DVD, and CD media—without duplicating files or consuming additional hard drive space.

**Primary Environment:** Developed and tested on **Python 3.14.5** using the **PyQt6** framework. It is intended for archivists and system administrators who require deterministic volume splitting, multi-tier fallback capacity management, and zero-footprint staging.

### The Staging & Partitioning Engine
The utility leverages a sequential bin-packing algorithm paired with NTFS filesystem hardlinks.

Key operational features include:
1. **Zero Storage Duplication:** Staged disc volume directories are populated using native NTFS hardlinks (`os.link`), which point directly to the underlying file data on disk without consuming additional physical storage space.
2. **Multi-Tier Media Fallbacks:** Configure a primary media target (such as BDXL 128 GB) alongside up to three smaller fallback tiers (such as BD-R 25 GB or DVD-9). When the final tail volume or small initial dataset fits within a smaller tier, VolumeSpan™ automatically steps down the disc size to conserve higher-capacity media.
3. **Deterministic Sequential Partitioning:** Files are processed and allocated in strict directory and alphabetical order. This ensures predictable volume spans and simple restoration (copying discs sequentially back into a single folder).
4. **Interactive Simulation & Index Export:** Runs an in-depth simulation displaying an interactive tree view of every disc volume, relative paths, file sizes, media types, and capacity fill percentages before staging. Includes a **Save As Index** feature to export a formatted `.txt` report of the partitioned disc structures with suggested disc ID ranges.
5. **Safe Staging Target Cleanup:** Includes a specialized cleanup utility that traverses staging targets bottom-up, verifying that file link counts are greater than 1 (`st_nlink > 1`) before unlinking. Standalone, non-hardlinked files (`st_nlink == 1`) are strictly preserved to prevent accidental data loss.
6. **Robust Volume & Path Validation:** Enforces strict validation to prevent staging inside the source directory, blocks cross-volume partitioning, and prevents operations across network shares (UNC paths) and mapped network drives.

---

## Feature Reference

| Option | Description |
| :--- | :--- |
| **Disc ID Tracking** | Defines the starting label (e.g., `BD-0001`) and automatically increments numerical suffixes across volumes while displaying the last generated ID. |
| **Primary Media Ceiling** | Sets the maximum disc capacity preset (BDXL QL/TL, BD-R DL/SL, DVD-9/5, CD-R) or allows custom GiB ceilings with UDF filesystem safety margins. |
| **Multi-Tier Fallbacks** | Configures up to three fallback media tiers with custom capacity thresholds for automated tail-volume optimization. |
| **Dry Run Simulation & Index** | Scans source folders, opens an interactive report detailing volume counts and file allocations, and allows exporting structured index text files (`.txt`) of the disc set. |
| **Hardlink Backup Generation** | Instantly constructs the disc directory hierarchy and NTFS hardlinks in the staging folder for direct burning. |
| **Clean Staging Target** | Safely removes generated staging folders and unlinks hardlink copies while protecting original standalone files. |
| **Theme Engine** | Supports Dark, Light, and System-synced UI modes via a custom QPalette implementation. |

---

## Assets & Licensing
This software is released under the **GNU General Public License v3**.

### Icon Credits
* **File:** `volumespan_cd_icon.svg`
    * **Asset:** Compact Disc Cd SVG Vector
    * **Source:** <a href="https://www.svgrepo.com/svg/224282/compact-disc-cd" target="_blank">https://www.svgrepo.com/svg/224282/compact-disc-cd</a>
    * **License:** <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank">CC0 License</a>
    * **Modifications:** Modified by pwshAgyjkcrg761.

---

## Dependencies
* **OS:** Microsoft Windows 10 / 11 (NTFS file system required).
* **Python:** 3.14.5+ (Recommended).
* **PyQt6:** Required for the Graphical User Interface.

## Support & Maintenance
**This repository is provided "as-is" for archival purposes.** The author is not actively looking for feedback, feature requests, or bug reports. The issue tracker is disabled.

## Disclaimer
*VolumeSpan™ is a backup staging utility. The author is not responsible for data loss resulting from filesystem errors, media degradation, or improper disc burning practices. Always verify backup disc integrity after burning.*

---
> **Document Control**<br>
> *This document is up-to-date with the following version of VolumeSpan™.*<br>
> *2026.09.04__08.40.53*