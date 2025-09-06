import folium
import folium.plugins
import geopandas as gpd
from typing import Union


class FoliumMap(folium.Map):
    """Custom Folium map class for easy vector and layer management.

    Args:
        center (tuple, optional): Initial map center as (lat, lon). Defaults to (0, 0).
        zoom (int, optional): Initial zoom level. Defaults to 2.
        **kwargs: Additional keyword arguments passed to folium.Map.
    """

    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_layer_control(self):
        """Enables layer control on the map."""
        folium.LayerControl().add_to(self)

    def add_vector(
        self,
        vector_data: Union[str, gpd.GeoDataFrame, dict],
        name="Vector Layer",
        zoom_to_layer=True,
    ):
        """
        Add vector data to the map. Supports file path, GeoDataFrame, or GeoJSON-like dict.

        Args:
            vector_data (Union[str, gpd.GeoDataFrame, dict]): file path, GeoDataFrame, or GeoJSON-like dict.
            name (str, optional): Set a layer name. Defaults to "Vector Layer".
            zoom_to_layer (bool, optional): Zoom to layer extantion. Defaults to True.

        Returns: None.
        """

        if isinstance(vector_data, str):
            gdf = gpd.read_file(vector_data)
        elif isinstance(vector_data, gpd.GeoDataFrame):
            gdf = vector_data
        elif isinstance(vector_data, dict) and "features" in vector_data:
            gdf = gpd.GeoDataFrame.from_features(vector_data["features"])
        else:
            raise ValueError(
                "vector_data must be a filepath, GeoDataFrame or GeoJSON-like dict"
            )

        geojson_data = gdf.__geo_interface__

        # Zoom to layer
        if zoom_to_layer:
            minx, miny, maxx, maxy = gdf.total_bounds
            self.fit_bounds([[miny, minx], [maxy, maxx]])

        # Load GeoJSON
        folium.GeoJson(data=geojson_data, name=name).add_to(self)

    def add_split_map(
        self, left_layer="openstreetmap", right_layer="cartodbpositron", **kwargs
    ):
        """
        Add a split map with two layers for comparison.

        Args:
            left_layer (folium.Layer): Layer to show on the left side.
            right_layer (folium.Layer): Layer to show on the right side.

        Returns: None.
        """
        # # if we want to include also google maps

        # map_types = {
        #     'ROADMAP': 'm',
        #     'SATELLITE': 's',
        #     'HYBRID': 'y',
        #     'TERRAIN': 'p'
        # }
        # map_type = map_types[map_type.upper()]

        # url = (
        #     f'http://mt1.google.com/vt/lyrs={map_type.lower()}&x={{x}}&y={{y}}&z={{z}}'
        # )

        left_layer = folium.TileLayer(left_layer, **kwargs)
        right_layer = folium.TileLayer(right_layer, **kwargs)
        sbs = folium.plugins.SideBySideLayers(left_layer, right_layer)

        left_layer.add_to(self)
        right_layer.add_to(self)
        sbs.add_to(self)
