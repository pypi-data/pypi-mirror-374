# KLV-System-Monitor

**KLV System Monitor** is a lightweight system monitor written in Python (PyQt5 + psutil) with a focus on **clarity, low overhead, and control**.  
It takes inspiration from **GNOME/Ubuntu System Monitor** and brings a similarly clean experience to **Linux and Windows**, while adding features that were missing elsewhere.

- **Three CPU views**: **Multi thread**, **General view**, and **Multi window** (selectable in **Preferences**).
- **Configurable smoothing and refresh**: decoupled refresh rates for plots vs. text/labels; per-subsystem EMA alphas (CPU, memory, network).
- **Tunable visuals**: line width, colors (per-core or mono), grid toggles, antialiasing, translucent fill for CPU areas, DPI scaling, and frequency labels per core.
- **Efficient updates**: process table refreshes **only when visible**; file systems view refreshes **on demand**.
- **Power tools**: filter and sort processes; clear current selection (stop following) and **kill selected** (when permitted).

---

<p align="center">
  💡 <b>If you find this project useful, please give it a ⭐ Star and consider 👁 Watch to get updates on new releases.</b><br>
  Your support helps me improve and keep adding features 🚀
</p>

---


## Feature tour

### 1) CPU — General view (single curve)
Shows total CPU usage over the last 60 seconds with a fixed **0–100%** Y-axis.
      The average CPU frequency, CPU temperature (when supported) and total CPU usage are displayed beneath the chart.
Smoothing (EMA) and antialiasing can be enabled/disabled in **Preferences**.

![CPU – General view](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/general_view.gif)

**How to read this view**
- **X-axis**: time window (seconds).  
- **Y-axis**: total CPU utilization (%).  
- **Footer**: average CPU frequency across cores, CPU temperature (if supported), and total CPU usage.

---

### 2) CPU — Multi-thread view (all cores)
Per-CPU utilization is plotted **simultaneously**, one colored line per core/thread.  
Each legend entry shows **CPU name → current % and frequency** (if frequency display is enabled).  
Line thickness, colors, smoothing and grids are configurable in **Preferences**.

![CPU – Multi-thread view](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/Thread_view.gif)

**Tips**
- Colors are persistent and can be customized.  
- Toggle extra smoothing for a look similar to GNOME System Monitor.

---

### 3) CPU — Parallel processes tracking
An example of a parallel workload starting and ramping up.  
You can see how multiple threads pick up work at the same time and how the smoothing avoids jagged spikes while keeping short-term dynamics readable.

![CPU – Parallel processes tracking](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/parallel_processes_tracking.gif)

---

### 4) CPU — Multi-window per-core view
Compact **grid of mini-plots**: one small chart per core.  
Great for many-core systems; the grid is scrollable and the number of columns is configurable.  
You can optionally show axes, match label color to plot color, or use a mono color for all mini-plots.

![CPU – Multi-window view](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/multi_window_view.gif)

---

### 5) Memory, Swap and Network
Two stacked panels:
- **Memory & Swap**: filled area chart with used memory and cache; swap status is shown on the right.  
- **Network**: receive/send rates (per second) plus totals since the start of the session.  
Both panels support optional EMA smoothing and gridlines.

![Memory, Swap and Network](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/Memory_swap_and_network.gif)

---

### 6) File Systems tab
Overview of mounted file systems and low-level disk I/O:

![File systems](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/file_system.png)

**Mounted File Systems**
- Columns: **Device**, **Mount**, **Type**, **Total**, **Used**, **Free**, **%**.  
- The percentage column includes a horizontal utilization bar.

**Disk I/O**
- Per-disk counters since boot: **reads / writes / read bytes / write bytes / read time / write time / busy ms**.

---

### 7) Processes tab
A fast, filterable process table that updates only when the tab is visible (to reduce overhead).

![Processes](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/processes.png)

**Features**
- **Filter box** (top-left): search by process name, user, or PID.  
- Click column headers to **sort** (ascending/descending).  
- Columns: **Process Name**, **User**, **% CPU**, **PID**, **Memory**, **Disk read total**, **Disk write total**, …  
- **Clear Selection**: stops following the current process (if you were tracking one).  
- **Kill Selected**: terminates selected processes (requires sufficient permissions).

The refresh interval of this tab is configurable in **Preferences**.

---

### 8) Preferences
All performance, smoothing and UI options in one place:

![Preferences](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/preferences.png)

**Global settings**
- **History window (seconds)** — width of the time window.  
- **Plot update interval (ms)** — how often lines are redrawn.  
- **Text update interval (ms)** — how often labels (%/GHz) refresh.  
- **Processes refresh interval (ms)**, **File systems refresh interval (ms)** — decoupled from plot updates.  
- **CPU / Memory / Network EMA alpha** — smoothing strength (0–0.999).  
- **Show per-CPU frequencies (and average)** — overlay GHz per core + mean.  
- **Show X/Y grid**, **Grid squares per axis**.
- **Smooth network graph (EMA)**, **Enable antialiasing**, **Fill CPU graphs with transparency**.
- **DPI scaling (%)** — adjust overall interface size.

**Multi-thread view**
- **Thread line width (px)**.  
- **Smooth graphs (EMA)** and **Extra smoothing for CPU lines (double-EMA)**.

**General view**
- **Curve color** for the single-curve CPU view.

**Multi-window**
- **Mini plot min width/height (px)**, **columns count** (grid layout).  
- **Show axes in multi-window plots**.  
- **Mono color for multi-window plots** (or per-core colors).  
- **CPU label placement** and **Match label color to plot**.

Footer buttons: **Restore Defaults**, **Apply**, **Cancel**, **OK**.

---

### Themes & Appearance

KLV System Monitor ships with multiple built-in themes ranging from light to deep dark.  
Charts, legends and UI widgets adapt automatically to the selected theme to preserve contrast and readability.

![Themes overview](https://raw.githubusercontent.com/karellopez/KLV-System-Monitor/main/assets/themes_feature.png)
<!-- If you want it to also render on PyPI, use a raw GitHub URL instead:
-->

**Highlights**
- **Theme selector** in **Preferences → Theme** (instant preview).
- High-contrast palettes for per-CPU lines and legends in both light and dark modes.
- Optional **antialiasing** for extra-smooth curves (toggle in Preferences).
- Grid visibility (X/Y), line width, mono/per-core colors, and label color matching are all configurable.
- The general CPU view keeps a fixed **0–100%** Y-axis for consistent reading across themes.


---

## Requirements

| Software  | Minimum Version | Notes                                                   |
|----------|-----------------|---------------------------------------------------------|
| **Python** | 3.10            | Installed automatically if you use the one-click installers |

---

## Installation

You can install KLV System Monitor in two ways:

### 1. One-click installers <sup>(recommended)</sup>

1. **Download** the ZIP package:  
   **[📦 One-click Installers](https://github.com/karellopez/KLV-System-Monitor/raw/main/Installers/Installers.zip
)**
2. **Extract** the ZIP file and run the script for your operating system:

| OS               | Script                           | How to Run                                                                                                                                                                                                         | Duration |
|------------------|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| **Windows 10/11**| `install_klv_system_monitor.bat` | Double-click. This will open a terminal and the installation will start.<br/>If you are not familiar to terminals, please, do not be afraid. <br/>This script do not have any permission to make undesired things. | ≈ 5 min |
| **Linux**        | `install_klv_system_monitor.sh`  | Open a terminal in the path of the installer and type: <br/>`./klv_system_monitor.sh`                                                                                                                               | ≈ 5 min |

3. After the installation finishes, you will find two shortcuts on your desktop:

| OS          | Launch                            | Uninstall                       |
|-------------|-----------------------------------|---------------------------------|
| **Windows** | `run_KLVSystemMonitor.bat`             | `uninstall_KLVSystemMonitor.bat`     |
| **Linux**   | **KLV System Monitor** (launcher) | `Uninstall KLV System Monitor`  |

---

### 2. Install in a virtual environment (advanced)

```bash
# 1. Create a virtual environment
python3 -m venv <env_name>

# 2. Activate it
source <env_name>/bin/activate          # On Windows: <env_name>\Scripts\activate

# 3. Install BIDS Manager from GitHub
pip install klv-system-monitor
```
The package declares all dependencies, so installation
pulls everything required to run the GUI and helper scripts.
All core requirements are version pinned in `pyproject.toml` to ensure
consistent installations.

After installation the following commands become available:

- `klvtop` – main GUI containing all KLV System Monitor functionalities
