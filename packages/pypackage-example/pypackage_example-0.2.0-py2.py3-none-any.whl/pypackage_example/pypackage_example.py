"""Main module."""

import ipyleaflet


class LeafletMap(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="400px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenStreetMap"):
        basemaps = {
            "OpenStreetMap": ipyleaflet.basemaps.OpenStreetMap.Mapnik,
            # "Stamen Terrain": ipyleaflet.basemaps.Stamen.Terrain,
            # "Stamen Toner": ipyleaflet.basemaps.Stamen.Toner,
            "CartoDB Positron": ipyleaflet.basemaps.CartoDB.Positron,
            "CartoDB DarkMatter": ipyleaflet.basemaps.CartoDB.DarkMatter,
            "OpenTopoMap": ipyleaflet.basemaps.OpenTopoMap,
            "Esri WorldImagery": ipyleaflet.basemaps.Esri.WorldImagery,
        }
        if basemap in basemaps:
            # tile_layer = basemaps[basemap]
            # url = tile_layer['url']
            # attribution = tile_layer['attribution']
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
        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add(layer)

    def add_layer_control(self):
        layer_control = ipyleaflet.LayersControl(position="topright")
        self.add(layer_control)

    def add_vector(self, vector_data):
        geo_json = ipyleaflet.GeoJSON(data=vector_data)
        self.add(geo_json)
