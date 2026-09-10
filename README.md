# CTS Revit Plugin

[pyRevit](https://github.com/pyrevitlabs/pyRevit) extension developed by CTS BIM with productivity tools for BIM and MEP modeling in Autodesk Revit.

The extension adds a **CTS** tab to the Revit ribbon, organized into five panels: **Annotation**, **Hanger**, **Modeling**, **QC**, and **Support**.

## Compatibility

- Autodesk Revit **2023 to 2026**
- Requires [pyRevit](https://github.com/pyrevitlabs/pyRevit/releases) to be installed

## Installation

### 1. Install pyRevit

> Skip this step if pyRevit is already installed in Revit.

Go to the [pyRevit releases page](https://github.com/pyrevitlabs/pyRevit/releases) and download the latest version (at the time of this guide, `pyRevit 5.2.0.25181 Installer`).

![pyRevit download page](docs/install/01-pyrevit-download.png)

Run the installer (it's recommended to close Revit during installation). After installing, open Revit and confirm the **pyRevit** tab appears in the ribbon — if it doesn't, restart Revit.

### 2. Download the CTS Plugin (latest version)

Download the latest CTS Plugin package from the [Releases page](https://github.com/cts-bim/CTS-Revit-Plugin/releases). Every version is published there, with its release notes and the corresponding `.zip`.

> Download the `.zip` named after the version (e.g., `CTS-Revit-Plugin-Version-4.0.zip`), not the auto-generated **Source code** files.

The plugin is distributed as a `.zip` file and must be extracted before use. After extracting, move the entire plugin folder (e.g., `CTS Revit Plugin Version X.0`) to:

```
C:\Users\<YourUser>\AppData\Roaming
```

Tip: type `%appdata%` in the Windows File Explorer address bar to jump straight to this folder.

![Plugin folder inside %appdata%\Roaming](docs/install/03-appdata-folder.png)

### 3. Connect the Plugin to Revit via pyRevit

With pyRevit installed and the CTS Plugin folder in the right place, click the pyRevit arrow icon at the bottom-left corner of the Revit window.

![pyRevit arrow in the ribbon](docs/install/04-pyrevit-arrow.png)

Select **Settings** from the menu.

![pyRevit menu with the Settings option](docs/install/05-pyrevit-settings-menu.png)

In the settings window, open **Custom Extension Directories**, click **Add folder**, and select the plugin folder placed in `%appdata%\Roaming` in the previous step (e.g., `C:\Users\User\AppData\Roaming\CTS Revit Plugin Version X.0`).

![Add Folder dialog in pyRevit settings](docs/install/06-add-folder-dialog.png)

Click **Save Settings and Reload**. After reloading, the **CTS** tab should appear in the Revit ribbon.

![Resulting CTS tab in the ribbon](docs/install/07-cts-tab-result.png)

### 4. Updating the CTS Plugin

When a new version is released, repeat steps 2 and 3: download the latest version, extract the folder, move it to `%appdata%\Roaming`, and add the folder again in pyRevit's settings.

> **Important**: before adding the new version, delete the old plugin folder from the system to avoid conflicts between versions.

## Tools

### Annotation Panel

| Tool | Description |
|---|---|
| **Smart Concat** | Concatenates values from multiple parameters of the selected elements (Pipe Accessories, Fabrication Hangers, Pipes, Mechanical Equipment, etc.) into a single parameter, via a guided form. |
| **Views By Scope Box** | Duplicates a selected Floor Plan once per selected Scope Box, naming each new view with a user-defined prefix + Scope Box name. |
| **Center The View** | Centers the viewport on the active sheet and aligns the viewport title directly below it. |
| **Grids 3D to 2D** | Converts all grids visible in the active view from 3D to 2D (view-specific) extents in one click. |
| **Views To Sheet** | Creates sheets for the selected views, auto-numbering them with a given prefix, applying the chosen title block, and centering the view on the sheet. |

> **Views By Scope Box** is a split button — *Center The View*, *Grids 3D to 2D*, and *Views To Sheet* are grouped under it.

### Hanger Panel

| Tool | Description |
|---|---|
| **Rod Length Adjuster** | Adjusts the rod length of the selected MEP Fabrication Hangers by an imperial value typed by the user — positive to lengthen (`1' 6"`, `+6"`), negative to shorten (`-1' 10 5/8"`, `-6"`). Elements from other categories are skipped and reported in the final summary. |
| **Hanger without Host** | Finds Fabrication Hangers without a host in the project and isolates them in the active view for review. |
| **Connect Hanger** | Automatically connects/hosts a selected Fabrication Hanger onto a selected straight Fabrication pipe. |

> **Rod Length Adjuster** is a split button — *Hanger without Host* and *Connect Hanger* are grouped under it.

### Modeling Panel

| Tool | Description |
|---|---|
| **Flip Elements** | Flips the selected MEP Fabrication Parts, skipping pinned elements or elements that aren't Fabrication Parts. |
| **MEP Face Aligner** | Moves the selected pipes (native or Fabrication) to align a side (top/bottom/left/right, screen-relative) against a chosen reference element's face. |
| **Rotate 90° CW** | Rotates the selected MEP Fabrication Parts 90° clockwise, automatically skipping pinned elements. |
| **Align By X / Y / Z** | Aligns a selected element to a reference element along the model's X, Y, or Z axis, using connector geometry. |

### QC Panel

| Tool | Description |
|---|---|
| **Duplicate Finder** | Checks the active view for overlapping duplicates: elements sharing Category + Family and occupying the same space are isolated in the view and listed in the output window. The categories to analyse are picked when the command runs (Fabrication Pipework, Fabrication Hangers, Pipe Accessories, Mechanical Equipment, and Generic Models). |
| **Parameter Cleaner** | Clears all visible text-type instance parameters (shared/project), plus Mark and Comments, on the selected elements. |

### Support Panel

| Tool | Description |
|---|---|
| **Update** | Direct link to the [CTS BIM repositories on GitHub](https://github.com/orgs/cts-bim/repositories), where new versions are published and issues can be reported. |

## Authors

- **Bruno Dias**
- **Pedro Oliveira**
