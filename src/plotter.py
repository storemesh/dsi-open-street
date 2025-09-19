import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import importlib.resources

class WalkerMap:
    """
    A class to fetch, process, and visualize walkable city data from a given point.
    """
    def __init__(self, lat, lon, time_minutes=15, walk_speed_kmh=5):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        self.lat = lat
        self.lon = lon
        self.time_minutes = time_minutes
        self.walk_speed_kmh = walk_speed_kmh
        
        print("Initializing WalkerMap... Fetching and processing data. 🏗️")
        self._prepare_data()
        print("Data preparation complete. Ready to plot. ✨")

    def _prepare_data(self):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        dist = 2000
        walk_speed_mps = self.walk_speed_kmh * 1000 / 3600
        max_dist = walk_speed_mps * self.time_minutes * 60

        self.G = ox.graph_from_point((self.lat, self.lon), dist=dist, network_type="walk")
        orig_node = ox.distance.nearest_nodes(self.G, self.lon, self.lat)
        lengths = nx.single_source_dijkstra_path_length(self.G, orig_node, weight="length")
        reachable_nodes = [node for node, d in lengths.items() if d <= max_dist]
        self.subgraph = self.G.subgraph(reachable_nodes)

        node_points = [Point((data["x"], data["y"])) for _, data in self.subgraph.nodes(data=True)]
        gdf_nodes = gpd.GeoDataFrame(geometry=node_points, crs="EPSG:4326")
        area_polygon = gdf_nodes.unary_union.convex_hull
        self.gdf_area = gpd.GeoDataFrame(geometry=[area_polygon], crs="EPSG:4326")

        tags = {
            "landuse": True, "building": True, "amenity": True,
            "leisure": True, "natural": True, "shop": True, "tourism": True,
        }
        self.gdf = ox.features_from_point((self.lat, self.lon), dist=dist, tags=tags)

        self.gdf["category"] = self.gdf.apply(self._classify_feature, axis=1)
        self.gdf["service"] = self.gdf.apply(self._classify_service, axis=1)

        gdf_services = self.gdf[self.gdf["service"].notna()].copy()
        gdf_services = gdf_services.set_geometry(gdf_services.geometry.centroid)
        self.gdf_services_in_area = gpd.sjoin(gdf_services, self.gdf_area, predicate="within")

    @staticmethod
    def _classify_feature(row):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        if row.get("landuse") in ["forest", "grass", "trees"] or row.get("natural") in ["wood", "tree"]:
            return "Tree"
        if row.get("natural") == "water" and row.get("water") != "river":
            return "Water"
        if row.get("water") == "river":
            return "River"
        if pd.notna(row.get("building")) or row.get("landuse") == "construction":
            return "Building"
        return None

    @staticmethod
    def _classify_service(row):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        if row.get("landuse") == "residential" or row.get("building") in ["residential", "apartments", "house"]:
            return "Living"
        if row.get("landuse") in ["industrial", "construction"] or row.get("building") in ["industrial", "warehouse"]:
            return "Working"
        if row.get("landuse") == "retail" or row.get("building") == "retail" or pd.notna(row.get("shop")):
            return "Supplying"
        if row.get("amenity") in ["hospital", "clinic"] or row.get("building") == "hospital":
            return "Caring"
        if row.get("amenity") in ["school", "university"] or row.get("building") == "school":
            return "Learning"
        if row.get("leisure") in ["park", "pitch"] or row.get("landuse") in ["grass", "recreation_ground"] or pd.notna(row.get("tourism")):
            return "Enjoying"
        return None

    def _plot_icon(self, ax, x, y, img_path, zoom=0.03):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        img = plt.imread(img_path)
        im = OffsetImage(img, zoom=zoom)
        im.image.axes = ax
        ab = AnnotationBbox(im, (x, y), frameon=False, pad=0)
        ax.add_artist(ab)
    
    def _set_map_extent(self, ax):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        minx, miny, maxx, maxy = self.gdf_area.total_bounds
        ax.set_xlim(minx - 0.02, maxx + 0.02)
        ax.set_ylim(miny - 0.02, maxy + 0.02)
        ax.margins(0)
        ax.set_axis_off()

    def output(self):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        fig, ax = plt.subplots(figsize=(24, 24))
        category_colors = { "Tree": "green", "Water": "lightblue", "River": "lightblue", "Building": "dimgray" }
        for cat, color in category_colors.items():
            subset = self.gdf[self.gdf["category"] == cat]
            if not subset.empty:
                subset.plot(ax=ax, facecolor=color, edgecolor="black", alpha=0.3)
        
        package_path = importlib.resources.files('dsi_walking_map') # หรือชื่อ package ของคุณ
        service_emojis = {
            "Living": str(package_path / 'assets/Living.png'), "Working": str(package_path / 'assets/Working.png'),
            "Supplying": str(package_path / 'assets/Supplying.png'), "Caring": str(package_path / 'assets/Caring.png'),
            "Learning": str(package_path / 'assets/Learning.png'), "Enjoying": str(package_path / 'assets/Enjoying.png'),
        }
        for service, img_path in service_emojis.items():
            subset = self.gdf_services_in_area[self.gdf_services_in_area["service"] == service]
            if not subset.empty:
                for pt in subset.geometry:
                    self._plot_icon(ax, pt.x, pt.y, img_path, zoom=0.02)
        
        ox.plot_graph(self.G, ax=ax, node_size=0, edge_color=(0.5, 0.5, 0.5, 0.3), edge_linewidth=0.5, show=False, close=False)
        self.gdf_area.plot(ax=ax, facecolor="lightblue", edgecolor="blue", linewidth=1, alpha=0.3, label=f"{self.time_minutes}-min walking area")
        
        minx, miny, maxx, maxy = self.gdf_area.total_bounds
        ax.set_xlim(minx - 0.02, maxx + 0.02)
        ax.set_ylim(miny - 0.02, maxy + 0.02)
        
        legend_ax = fig.add_axes([0.82, 0.4, 0.15, 0.2])
        legend_ax.axis('off')
        y = 1.0
        dy = 0.15
        for service, img_path in service_emojis.items():
            img = plt.imread(img_path)
            im = OffsetImage(img, zoom=0.06)
            ab = AnnotationBbox(im, (0.1, y), frameon=False, xycoords='axes fraction')
            legend_ax.add_artist(ab)
            legend_ax.text(0.25, y, service, transform=legend_ax.transAxes, fontsize=10, va='center')
            y -= dy
            
        return fig, ax

    # --- NEW METHOD ---
    def basemap(self, area=True):
        """
        Plots the combined layers (streets, buildings, water, etc.) WITHOUT service pins.
        """
        fig, ax = plt.subplots(figsize=(24, 24))
        
        # --- Plot Category Polygons ---
        category_colors = { "Tree": "green", "Water": "lightblue", "River": "lightblue", "Building": "dimgray" }
        for cat, color in category_colors.items():
            subset = self.gdf[self.gdf["category"] == cat]
            if not subset.empty:
                subset.plot(ax=ax, facecolor=color, edgecolor="black", alpha=0.3)
        
        # --- Plot street network and boundary ---
        ox.plot_graph(self.G, ax=ax, node_size=0, edge_color=(0.5, 0.5, 0.5, 0.3), edge_linewidth=0.5, show=False, close=False)
        if area : 
            self.gdf_area.plot(ax=ax, facecolor="lightblue", edgecolor="blue", linewidth=1, alpha=0.3, label=f"{self.time_minutes}-min walking area")
        
        # --- Set map extent ---
        minx, miny, maxx, maxy = self.gdf_area.total_bounds
        ax.set_xlim(minx - 0.02, maxx + 0.02)
        ax.set_ylim(miny - 0.02, maxy + 0.02)
        
        return fig, ax

    # --- Separated Layer Methods ---

    def street(self):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        fig, ax = plt.subplots(figsize=(12, 12))
        ox.plot_graph(self.G, ax=ax, node_size=0, edge_color=(0.2, 0.2, 0.2, 0.6), edge_linewidth=0.5, show=False, close=False)
        # self.gdf_area.plot(ax=ax, facecolor="lightblue", edgecolor="blue", linewidth=1, alpha=0.3)
        self._set_map_extent(ax)
        return fig, ax

    def building(self):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        fig, ax = plt.subplots(figsize=(12, 12))
        buildings = self.gdf[self.gdf["category"] == "Building"]
        if not buildings.empty:
            buildings.plot(ax=ax, facecolor='dimgray', edgecolor="black", alpha=0.3)
        # self.gdf_area.plot(ax=ax, facecolor="lightblue", edgecolor="blue", linewidth=1, alpha=0.3)
        self._set_map_extent(ax)
        return fig, ax

    def water(self):
        # ... (ส่วนนี้เหมือนเดิมทั้งหมด) ...
        fig, ax = plt.subplots(figsize=(12, 12))
        water = self.gdf[self.gdf["category"].isin(["Water", "River"])]
        if not water.empty:
            water.plot(ax=ax, facecolor="lightblue", edgecolor="lightblue", alpha=0.7)
        # self.gdf_area.plot(ax=ax, facecolor="lightblue", edgecolor="lightblue", linewidth=1, alpha=0.3)
        self._set_map_extent(ax)
        return fig, ax