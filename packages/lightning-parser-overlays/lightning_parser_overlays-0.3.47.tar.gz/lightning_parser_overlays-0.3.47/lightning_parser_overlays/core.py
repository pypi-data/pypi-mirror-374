import matplotlib
matplotlib.use(backend='Agg')  # Use non-GUI backend suitable for multiprocessing
from typing import List, Dict, Tuple, Optional, Union
import numpy as np
from PIL import Image
import re
import os
import multiprocessing
from matplotlib.figure import Figure
from matplotlib.colorbar import Colorbar

class FigureDetails:
    def __init__(self, 
                 fig: Union[Figure, Image.Image, np.ndarray],
                 uses_lat: bool = True,
                 uses_lon: bool = True,
                 uses_alt: bool = False):
        # exactly two of the three must be True
        if (int(uses_lat) + int(uses_lon) + int(uses_alt)) != 2:
            raise ValueError("Each FigureDetails must use exactly two of {lat, lon, alt}.")
        self.fig = fig
        self.uses_lat = uses_lat
        self.uses_lon = uses_lon
        self.uses_alt = uses_alt

class ColorbarDetails:
    def __init__(self, colorbar: Colorbar):
        self.colorbar = colorbar

class Overlay:
    """
    Overlay Object That Provides Necessary Information For Adding More Graphs.
    Each contained FigureDetails must use exactly two of {lat, lon, alt}.
    """
    def __init__(self,
                 overlay_name: str,
                 figures: List[FigureDetails],
                 colorbar_name: Optional[str] = None,
                 colorbar_details: Optional[ColorbarDetails] = None):
        if not figures:
            raise ValueError("Overlay requires at least one FigureDetails.")
        for fd in figures:
            # already validated in FigureDetails, but double-check for safety
            if (int(fd.uses_lat) + int(fd.uses_lon) + int(fd.uses_alt)) != 2:
                raise ValueError(f"{overlay_name}: each FigureDetails must be lat/lon, lat/alt, or lon/alt.")
        if (colorbar_name is None) ^ (colorbar_details is None):
            raise ValueError("colorbar_name and colorbar_details must be both provided or both None.")

        self.overlay_name = overlay_name
        self.figures = figures     
        self.colorbar_name = colorbar_name
        self.colorbar_details = colorbar_details