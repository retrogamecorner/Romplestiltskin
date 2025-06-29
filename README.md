# Romplestiltskin - ROM Collection Manager

**Created by Mr. Steve Mellor**

## Introduction

Welcome to Romplestiltskin! This tool is designed to help you manage, verify, and curate your retro game ROM collections. By leveraging emulator DAT files (like those from No-Intro), Romplestiltskin helps you identify what you have, what's missing, and whether your ROMs are correctly named and verified.

## The Problem It Solves

Many retro gaming enthusiasts accumulate large collections of ROMs from various sources. It can be challenging to:

*   Know if a collection for a specific system is complete.
*   Ensure ROMs are correctly named according to standard conventions.
*   Verify the integrity of ROM files using checksums (CRC).
*   Filter collections based on personal preferences (e.g., specific regions, no prototypes, only verified dumps).
*   Manage duplicate ROMs from different regions.

Romplestiltskin aims to simplify these tasks, providing a clear overview and powerful tools to get your collection in perfect order.

## Core Features

*   **DAT File Integration:** Load XML DAT files (e.g., from [No-Intro](https://datomatic.no-intro.org/index.php?page=download&s=64)) to get an authoritative list of games for a system.
*   **Comprehensive ROM Database:** Creates an internal database from DAT files, tagging games with attributes like:
    *   Major Name (e.g., "Super Mario Bros.")
    *   Region (USA, Europe, Japan, etc.)
    *   Language(s)
    *   Status (Beta, Demo, Prototype/Sample, Unlicensed)
    *   Release Version/Revision
    *   Unofficial Translations
    *   Verified Dump status
*   **ROM Scanning & Verification:**
    *   Scan your local ROM folders.
    *   Verify ROMs against the DAT information using CRC checksums and file sizes.
    *   Automatic filename correction suggestions for incorrectly named ROMs.
*   **Quick Folder Access:** Instantly open the ROM folder for the selected system directly from the main interface.
*   **Clear Visual Feedback:**
    *   Dual-panel view: DAT game list on one side, your collection on the other.
    *   Color-coded tabs and lists to quickly identify status:
        *   **Correct (Green Check):** Your ROM is verified and correctly named.
        *   **Missing (Yellow Question Mark):** A ROM from the DAT file is not in your collection.
        *   **Ignored (Gray Ban):** A ROM you have chosen to ignore.
        *   **Unrecognised (Orange Warning Triangle):** A file in your ROM folder that is not in the DAT file.
        *   **Broken (Red Exclamation Circle):** A ROM that is corrupt or has a bad checksum.
*   **File Management:**
    *   Rename ROMs to match DAT standards.
    *   Move unrecognized files to a dedicated 'extra' folder.
    *   Move broken files to a dedicated 'broken' folder or (optionally) delete them.
*   **Powerful Filtering:**
    *   Filter the DAT game list based on any of the parsed attributes (Region, Language, Status, etc.).
    *   Manage duplicate games by prioritizing regions (e.g., prefer USA versions over European or Japanese).
    *   Manually hide specific titles from the DAT view.
    *   Move ROMs that don't match your filter criteria to a 'filtered' folder, helping you keep only the ROMs you want.
*   **Missing ROMs List:**
    *   Generate a list of ROMs that are in the (filtered) DAT list but not in your collection.
    *   Export this list to a `.txt` file.
    *   Smart detection: Understands that if you have one acceptable regional version of a game (based on your filters), you might not consider other regional versions "missing."
*   **User-Configurable Paths:** Set your preferred locations for DAT files, the internal database, and managed ROM folders.
*   **Multi-Disc Game Handling (Initial Support):**
    *   Identifies multi-disc games based on `(Disc *)` naming.
    *   Allows moving these to a dedicated 'multi' folder.
    *   *(Future versions will enhance handling, e.g., for m3u playlist generation for .chd files).*

## Naming Conventions & Tags Understood

Romplestiltskin parses standard No-Intro naming conventions, including (but not limited to):

*   **Regions:** `(USA)`, `(Europe)`, `(Japan)`, `(Brazil)`, `(Germany)`, `(En,Fr,De)`, etc.
*   **Languages:** `(En)`, `(Fr)`, `(De)`, `(M3)` (multilanguage), etc.
*   **Status:** `(Proto)` (Prototype), `(Beta)`, `(Demo)`, `(Unl)` (Unlicensed), `(Sample)`.
*   **Verification:** `[!]` (Verified Dump), or `status="verified"` from DAT XML.
*   **Revisions:** `(Rev A)`, `(v1.1)`, `(PRG1)`, `[a]` (alternate), etc.
*   **Translations:** `[T+Eng]` (unofficial translation to English).
*   **Other:** `[o]` (overdump), `[p]` (pirate), `[h]` (hack), `[t]` (trained/modified).

## Technical Requirements (Initial Release)

*   **Operating System:** Windows (packaged as a standalone executable).
*   **Framework:** Built with Python.
*   Users will need to download DAT files from sources like No-Intro.

## How It Works (High-Level)

1.  **Configure:** Tell Romplestiltskin where your DAT files are stored.
2.  **Load System:** Select a system (e.g., "Atari - Atari 2600"). The tool loads the corresponding DAT file and populates its game database.
3.  **Scan ROMs:** Point the tool to your ROM folder for that system.
4.  **Verify & View:** Romplestiltskin scans your ROMs, verifies them against the DAT, and displays both lists with color-coded statuses.
5.  **Manage:** Use the tools to rename files, move unwanted/broken ROMs.
6.  **Filter:** Customize the DAT game list according to your preferences (regions, types, etc.). Run the filter to move non-matching ROMs from your collection into a 'filtered' folder.
7.  **Report:** Generate a list of missing ROMs based on your active filters.

## Future Development

*   **Cross-Platform Native Ports:** Official support for macOS, Linux.
*   **Mobile Version:** A compatible version for Android.
*   **Advanced Multi-Disc Handling:** More sophisticated tools for managing multi-disc titles (e.g., creating m3u playlists for emulators that use .chd files).
*   **Support for other DAT formats** (if requested and feasible).
*   **User-defined profiles for filters.**

## Contributing

*(Details on how to contribute, coding standards, etc., will be added here once the project is more mature.)*

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

You are free to:
*   **Share** — copy and redistribute the material in any medium or format
*   **Adapt** — remix, transform, and build upon the material

Under the following terms:
*   **Attribution** — You must give appropriate credit to Steve Mellor, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
*   **NonCommercial** — You may not use the material for commercial purposes.
*   **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

For the full license text, please see the `LICENSE` file included in this repository or visit:
[https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Disclaimer

We do not include, provide, or endorse the acquisition of any game files or copyrighted material. Users are responsible for ensuring they have the legal right to use any game files they process with this tool. This is provided as-is, and you use it at your own risk.
