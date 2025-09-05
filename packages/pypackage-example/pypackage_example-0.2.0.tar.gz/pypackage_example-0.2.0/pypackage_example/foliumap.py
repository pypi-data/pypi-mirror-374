import folium


class FoliumMap(folium.Map):
    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        super().__init__(location=center, zoom_start=zoom, **kwargs)
        folium.LayerControl().add_to(self)
