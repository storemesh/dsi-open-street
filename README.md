# DSI Walking Map 🚶‍♀️🗺️

A Python library to fetch, process, and visualize walkable city data from OpenStreetMap. Given a central coordinate, it calculates the area reachable within a specified walking time and generates various map visualizations.

---

## ✨ Features

* **Walkable Area Calculation**: Computes the reachable street network and its corresponding area (convex hull) based on walking time and speed.
* **OSM Data Fetching**: Downloads land use, buildings, amenities, and other features from OpenStreetMap.
* **Automatic Feature Classification**: Categorizes geographic features into logical groups like 'Building', 'Water', and 'Tree', and classifies amenities into services like 'Living', 'Caring', and 'Enjoying'.
* **Rich Visualizations**:
    * Generate a complete map (`output`) with all layers and custom service icons.
    * Generate a clean basemap (`basemap`) without service icons.
    * Generate individual maps for each primary layer: `street`, `building`, and `water`.
---

## 🚀 Installation

To install the library, clone this repository and run the following command from the root directory (`DSI-MAP/`):