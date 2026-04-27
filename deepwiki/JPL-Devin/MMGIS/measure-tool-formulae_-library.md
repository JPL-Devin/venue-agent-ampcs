# Page: Measure Tool & Formulae_ Library

# Measure Tool & Formulae_ Library

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [private/api/2ptsToProfile.py](private/api/2ptsToProfile.py)
- [private/api/BandsToProfile.py](private/api/BandsToProfile.py)
- [src/essence/Basics/Formulae_/Formulae_.js](src/essence/Basics/Formulae_/Formulae_.js)
- [src/essence/Tools/Measure/MeasureTool.css](src/essence/Tools/Measure/MeasureTool.css)
- [src/essence/Tools/Measure/MeasureTool.js](src/essence/Tools/Measure/MeasureTool.js)
- [src/external/Leaflet/Leaflet.PolylineMeasure.css](src/external/Leaflet/Leaflet.PolylineMeasure.css)
- [src/external/Leaflet/Leaflet.PolylineMeasure.js](src/external/Leaflet/Leaflet.PolylineMeasure.js)
- [src/external/attributions.js](src/external/attributions.js)

</details>



The Measure system in MMGIS provides a comprehensive suite for spatial quantification, including 2D/3D distance measurement, azimuth calculation, elevation profiling, and Line of Sight (LOS) analysis. This functionality is supported by the `Formulae_` utility library, which centralizes mathematical operations for planetary GIS.

## Measure Tool Architecture

The `MeasureTool` is a React-based interactive component that integrates with both the Leaflet 2D map and the Lithosphere/Cesium 3D globe. It manages a persistent state of clicked coordinates and uses a "rubber-band" visual style for real-time feedback.

### Key Implementation Details
- **Coordinate Management**: Clicked points are stored in the `clickedLatLngs` array [src/essence/Tools/Measure/MeasureTool.js:31-31]().
- **Rendering**: Uses a dedicated Leaflet layer `measureToolLayer` [src/essence/Tools/Measure/MeasureTool.js:30-30]() for 2D and interfaces with `Globe_` for 3D interactions via event listeners on the Lithosphere container [src/essence/Tools/Measure/MeasureTool.js:71-89]().
- **Data Visualization**: Elevation profiles are rendered using `Chart.js` and `react-chartjs-2` [src/essence/Tools/Measure/MeasureTool.js:16-17]().
- **External Integration**: Leverages `Leaflet.PolylineMeasure` for core Leaflet polyline handling and tooltip management [src/external/Leaflet/Leaflet.PolylineMeasure.js:24-29]().

### Measurement Modes
The tool supports three primary modes defined in `availableModes` [src/essence/Tools/Measure/MeasureTool.js:35-36]():
1. **Segment**: Measures distance between the last two points only.
2. **Continuous**: Accumulates distance across all points in the sequence.
3. **Continuous Color**: Similar to continuous, but often used for visual differentiation of segments.

### Elevation Profiling Data Flow
The tool generates profiles by sampling points between anchors and querying backend GDAL-based scripts. The number of samples can be adjusted (default 100) [src/essence/Tools/Measure/MeasureTool.js:37-37]().

| Component | Role | Source |
| :--- | :--- | :--- |
| `MeasureTool.getDems()` | Retrieves available DEM paths from mission configuration (`dem` or `layerDems`). | [src/essence/Tools/Measure/MeasureTool.js:119-119]() |
| `2ptsToProfile.py` | Python script using GDAL to extract band values along a line between two points. | [private/api/2ptsToProfile.py:1-12]() |
| `BandsToProfile.py` | Queries specific raster bands at a single point or range of bands. | [private/api/BandsToProfile.py:1-6]() |

**Sources:** [src/essence/Tools/Measure/MeasureTool.js:1-60](), [src/external/Leaflet/Leaflet.PolylineMeasure.js:24-41](), [src/essence/Tools/Measure/MeasureTool.js:119-122](), [private/api/2ptsToProfile.py:163-171]()

---

## Formulae_ Utility Library

The `Formulae_` library (often referenced as `F_`) is a singleton containing reusable mathematical and conversion logic. It handles planetary radii adjustments, unit conversions, and spatial calculations.

### Core Mathematical Functions
- **Haversine Distance**: Calculates great-circle distance between two points on a sphere.
- **`azElDistBetween`**: Computes Azimuth, Elevation, and Distance between two sets of coordinates [src/essence/Basics/Formulae_/Formulae_.js:7-7]().
- **`linearScale`**: Maps a value from one domain to another range [src/essence/Basics/Formulae_/Formulae_.js:57-63]().
- **`destinationFromBearing`**: Calculates a new coordinate given a start point, bearing, and distance.

### Planetary Support
The library allows setting the major and minor radii of the target body, defaulting to Mars (3396190m) [src/essence/Basics/Formulae_/Formulae_.js:23-24]().
- **`setRadius(which, radius)`**: Updates `radiusOfPlanetMajor` or `radiusOfPlanetMinor` [src/essence/Basics/Formulae_/Formulae_.js:48-53]().
- **`getEarthToPlanetRatio()`**: Returns the ratio between Earth's radius and the current planet's major radius [src/essence/Basics/Formulae_/Formulae_.js:54-56]().

### System Interaction Diagram
This diagram shows how the `MeasureTool` utilizes the `Formulae_` library and backend scripts to process spatial data.

```mermaid
graph TD
    subgraph "Frontend: MeasureTool.js"
        [MeasureToolComponent] --> [clickMap/clickGlobe]
        [clickMap/clickGlobe] --> [clickedLatLngsArray]
        [clickedLatLngsArray] --> [recomputeLineOfSight]
        [recomputeLineOfSight] --> [ChartJSRendering]
    end

    subgraph "Utility: Formulae_.js"
        [F_linearScale]
        [F_azElDistBetween]
        [F_setRadius]
    end

    subgraph "Backend: Python API"
        [2ptsToProfile_py]
        [BandsToProfile_py]
        [great_circle_calculator_py]
    end

    [MeasureToolComponent] -- "Coordinate Scaling" --> [F_linearScale]
    [MeasureToolComponent] -- "Bearing/Azimuth" --> [F_azElDistBetween]
    [MeasureToolComponent] -- "Fetch Profile Data" --> [2ptsToProfile_py]
    [2ptsToProfile_py] -- "Great Circle Math" --> [great_circle_calculator_py]
```
**Sources:** [src/essence/Basics/Formulae_/Formulae_.js:1-63](), [src/essence/Tools/Measure/MeasureTool.js:122-122](), [src/essence/Basics/Formulae_/Formulae_.js:48-56](), [private/api/2ptsToProfile.py:17-21]()

---

## Line of Sight (LOS) Analysis

The Measure Tool includes a 1D Line of Sight analysis feature. It calculates visibility between an observer and a target over a terrain profile generated from a DEM.

### LOS Parameters
- **`observerHeight`**: Height of the observer above the surface (default 2m) [src/essence/Tools/Measure/MeasureTool.js:40-40]().
- **`targetHeight`**: Height of the target above the surface (default 0m) [src/essence/Tools/Measure/MeasureTool.js:41-41]().
- **`recomputeLineOfSight()`**: Logic that iterates through profile samples to determine if the line between observer and target is obstructed by the terrain profile data [src/essence/Tools/Measure/MeasureTool.js:122-122]().

### UI Visualization
- **Observer Marker**: A green dot (`#measureSVGObserver`) on the profile chart represents the observer's position, calculated using `F_.linearScale` [src/essence/Tools/Measure/MeasureTool.js:104-116]().
- **LOS Overlay**: An SVG overlay on the chart displays visibility status across the profile [src/essence/Tools/Measure/MeasureTool.css:157-164]().

**Sources:** [src/essence/Tools/Measure/MeasureTool.js:38-42](), [src/essence/Tools/Measure/MeasureTool.js:100-117](), [src/essence/Tools/Measure/MeasureTool.css:110-116]()

---

## BottomBar UI Controls

The `BottomBar` provides global utility controls that interact with the current state of the map, coordinates, and tools.

### Key Features
- **Copy Link**: Uses `QueryURL.writeCoordinateURL` to generate a deep-link to the current view and coordinates.
- **Screenshot**: Captures the current map state using `HTML2Canvas`. This involves a complex z-index reordering of Leaflet panes to ensure vector layers and tiles are rendered correctly in the output image.
- **Naming Convention**: Screenshots are automatically named using the mission, current time, and coordinates: `mmgis-[mission]_[time]_[lat]_[lng]`.

### Entity Mapping
The following diagram maps UI elements to their implementation logic in the codebase.

```mermaid
graph LR
    subgraph "UI Component: BottomBar"
        [mdi-open-in-new_Link]
        [mdi-camera_Screenshot]
    end

    subgraph "Logic: BottomBar_js"
        [QueryURL_writeCoordinateURL]
        [HTML2CanvasLogic]
    end

    subgraph "Support Libraries"
        [Formulae_js_F_copyToClipboard]
        [Formulae_js_F_downloadCanvas]
        [Layers_js_L_configData]
    end

    [mdi-open-in-new_Link] --> [QueryURL_writeCoordinateURL]
    [QueryURL_writeCoordinateURL] --> [Formulae_js_F_copyToClipboard]
    [mdi-camera_Screenshot] --> [HTML2CanvasLogic]
    [HTML2CanvasLogic] --> [Formulae_js_F_downloadCanvas]
    [HTML2CanvasLogic] -- "Get Mission Name" --> [Layers_js_L_configData]
```
**Sources:** [src/essence/Tools/Measure/MeasureTool.js:1-20](), [src/essence/Basics/Formulae_/Formulae_.js:1-56](), [src/essence/Tools/Measure/MeasureTool.css:1-193]()

---

## Coordinate Display & Conversion

The system manages the display of cursor location and elevation in the UI, supporting multiple projection states and unit types.

### Coordinate States
The system maintains several coordinate representations:
- **`ll`**: Longitude/Latitude (standard decimal degrees).
- **`en`**: Easting/Northing (meters).
- **`cproj`**: Primary Projected coordinates.
- **`sproj`**: Secondary Projected coordinates.
- **`site`**: Local level (Y, X, -Z) coordinates used for rover-centric missions.

### Precision and Units
Each state defines its own precision and units, such as degrees (°) for lat/lon or meters (m) for projected systems. The `Formulae_` library provides `radiusOfPlanetMajor` and `radiusOfPlanetMinor` to ensure accurate distance calculations across different planetary bodies [src/essence/Basics/Formulae_/Formulae_.js:23-24]().

**Sources:** [src/essence/Basics/Formulae_/Formulae_.js:23-26](), [src/essence/Basics/Formulae_/Formulae_.js:48-56](), [private/api/2ptsToProfile.py:129-159]()
