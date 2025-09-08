"""Main module."""

import os
import ipyleaflet
import geopandas as gpd
from typing import Union


class LeafletMap(ipyleaflet.Map):
    """Custom Leaflet map class based on ipyleaflet.Map.

    Args:
        center (list, optional): Initial map center as [lat, lon]. Defaults to [20, 0].
        zoom (int, optional): Initial zoom level. Defaults to 2.
        height (str, optional): Map height in pixels or CSS units. Defaults to "400px".
        **kwargs: Additional keyword arguments passed to ipyleaflet.Map.

    Attributes:
        layout (ipywidgets.Layout): Layout object for map sizing.
        scroll_wheel_zoom (bool): Enables scroll wheel zooming.

    Methods:
        add_basemap(basemap="OpenStreetMap"):
            Adds a basemap layer from predefined options.

        add_basemap2(basemap="OpenTopoMap"):
            Adds a basemap layer using dynamic basemap string.

        add_layer_control():
            Adds a layer control widget to the map.

        add_vector(vector_data, name="Vector Layer", zoom_to_layer=True, style=None, hover_style=None):
            Adds vector data to the map from file path, GeoDataFrame, or GeoJSON-like dict.

            Args:
                vector_data (str | geopandas.GeoDataFrame | dict): Vector data source.
                name (str, optional): Layer name. Defaults to "Vector Layer".
                zoom_to_layer (bool, optional): Zooms to vector bounds. Defaults to True.
                style (dict, optional): Style for vector features. Defaults to None.
                hover_style (dict, optional): Hover style for vector features. Defaults to None.

            Raises:
                ValueError: If vector_data type is not supported.
    """

    def __init__(self, center=[20, 0], zoom=2, height="400px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenStreetMap"):
        """Adds a basemap layer from predefined options.

        Args:
            basemap (str, optional): Name of the basemap to add.
                Options are "OpenStreetMap", "CartoDB Positron", "CartoDB DarkMatter",
                "OpenTopoMap", "Esri WorldImagery". Defaults to "OpenStreetMap".

        Raises:
            ValueError: If the basemap name is not recognized.
        """
        basemaps = {
            "OpenStreetMap": ipyleaflet.basemaps.OpenStreetMap.Mapnik,
            "CartoDB Positron": ipyleaflet.basemaps.CartoDB.Positron,
            "CartoDB DarkMatter": ipyleaflet.basemaps.CartoDB.DarkMatter,
            "OpenTopoMap": ipyleaflet.basemaps.OpenTopoMap,
            "Esri WorldImagery": ipyleaflet.basemaps.Esri.WorldImagery,
        }
        if basemap in basemaps:
            tile_layer = ipyleaflet.TileLayer(
                url=basemaps[basemap]["url"],
                attribution=basemaps[basemap]["attribution"],
            )
            self.add_layer(tile_layer)
        else:
            raise ValueError(
                f"Basemap '{basemap}' not recognized. Available options: {list(basemaps.keys())}"
            )

    def add_basemap2(self, basemap="OpenTopoMap"):
        """Adds a basemap layer using a dynamic basemap string.

        Args:
            basemap (str, optional): Name of the basemap to add. Should match an attribute in ipyleaflet.basemaps.
                Defaults to "OpenTopoMap".

        Raises:
            ValueError: If the basemap name is not recognized.
        """

        try:
            url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        except:
            raise ValueError(
                f"Basemap '{basemap}' not recognized. Available options: {list(ipyleaflet.basemaps.keys())}"
            )

        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_layer_control(self):
        """Adds a layer control widget to the map.

        This allows toggling visibility of layers on the map.
        """
        layer_control = ipyleaflet.LayersControl(position="topright")
        self.add(layer_control)

    def add_vector(
        self,
        vector_data: Union[str, gpd.GeoDataFrame, dict],
        name="Vector Layer",
        zoom_to_layer=True,
        style=None,
        hover_style=None,
        **kwargs,
    ):
        """Adds vector data to the map from file path, GeoDataFrame, or GeoJSON-like dict.

        Args:
            vector_data (str | geopandas.GeoDataFrame | dict): Vector data source.
            name (str, optional): Layer name. Defaults to "Vector Layer".
            zoom_to_layer (bool, optional): Zooms to vector bounds. Defaults to True.
            style (dict, optional): Style for vector features. Defaults to None.
            hover_style (dict, optional): Hover style for vector features. Defaults to None.

        Raises:
            ValueError: If vector_data type is not supported.
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

        # Setting style and hover style
        if style is None:
            style = {"color": "blue", "fillOpacity": 0.4}

        if hover_style is None:
            hover_style = {"color": "red", "fillOpacity": 0.7}

        # Load GeoJSON
        geo_json = ipyleaflet.GeoJSON(
            data=geojson_data, name=name, style=style, hover_style=hover_style, **kwargs
        )
        self.add(geo_json)

    def add_raster(self, raster_data: str, **kwards) -> None:
        """Add raster data to the map using localtileserver.

        Args:
            raster_data (str): path to the raster file.
        """
        from localtileserver import TileClient, get_leaflet_tile_layer

        tc = TileClient(raster_data)
        tile_layer = get_leaflet_tile_layer(tc, **kwards)
        self.add(tile_layer)
        self.center = tc.center()
        self.zoom = tc.default_zoom

    def add_staticImage(self, image_path: str, bounds: list = None, **kwargs) -> None:
        """Add a static image to the map.

        Args:
            image_path (str): path to the image file.
            bounds (list): bounds of the image in [[south, west], [north, east]] format.
        """
        # if not os.path.isfile(image_path):
        #     raise ValueError(f"Image file '{image_path}' does not exist.")

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]

        image_layer = ipyleaflet.ImageOverlay(url=image_path, bounds=bounds, **kwargs)

        self.add(image_layer)
        self.fit_bounds(bounds)

    def add_video(self, video_path: str, bounds: list = None, **kwargs) -> None:
        """Add a video to the map.

        Args:
            video_path (str): path to the video file.
            bounds (list): bounds of the video in [[south, west], [north, east]] format.
        """
        # if not os.path.isfile(video_path):
        #     raise ValueError(f"Video file '{video_path}' does not exist.")

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]

        video_layer = ipyleaflet.VideoOverlay(url=video_path, bounds=bounds, **kwargs)

        self.add(video_layer)
        self.fit_bounds(bounds)

    def add_webservice(
        self, url: str, lyr_name: str = "WMS Layer", transparent=True, **kwargs
    ) -> None:
        """Add a web service layer to the map.

        Args:
            url (str): URL of the web service.
            name (str, optional): Name of the layer. Defaults to "WMS Layer".
            **kwargs: Additional keyword arguments passed to the WMSLayer.
        """
        wms_layer = ipyleaflet.WMSLayer(
            url=url, layers=lyr_name, transparent=transparent, **kwargs
        )
        self.add(wms_layer)
