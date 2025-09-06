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


class FigBaseDimensions:
    """
    Container for storing the dimensions in pixels of the given frame
    """
    def __init__(self,
                 x_y_width: int = 200,
                 x_y_height: int = 200,
                 x_alt_height: int = 50,
                 alt_y_width: int = 50,
                 time_alt_width: int = 295,
                 time_alt_height: int = 50):
        self.x_y_width = x_y_width
        self.x_y_height = x_y_height
        self.x_alt_height = x_alt_height
        self.x_alt_width= x_y_width # because together
        self.alt_y_width = alt_y_width
        self.alt_y_height = x_y_height # because together
        self.time_alt_width = time_alt_width
        self.time_alt_height = time_alt_height
        

class RangeParams:
    """
    Container for numerical ranges used in visualization axis limits and normalization.

    This class encapsulates the various buffered numerical ranges (e.g., time, altitude,
    spatial coordinates, and colorbar values) that are computed and applied to plotting axes
    for consistent scaling and presentation.

    Attributes:
        time_unit_range (tuple or list, optional): The buffered range for the time unit values.
        time_unit_datetime_range (tuple or list, optional): The buffered range as datetime values.
        time_range (tuple or list, optional): The raw range of time values.
        alt_range (tuple or list, optional): The buffered range of altitude values.
        x_range (tuple or list, optional): The buffered range of x-coordinate values (e.g., longitude).
        y_range (tuple or list, optional): The buffered range of y-coordinate values (e.g., latitude).
        num_pts_range (tuple or list, optional): The buffered range for the number of points (used in aggregation).
        colorbar_range (tuple or list, optional): The range of values used for colorbar normalization.
    """

    def __init__(self,
                 time_unit_range=None,
                 time_unit_datetime_range=None,
                 time_range=None,
                 alt_range=None,
                 x_range=None,
                 y_range=None,
                 num_pts_range=None,
                 colorbar_range=None):
        """
        Initialize a new instance of the RangeParams class.

        Parameters:
            time_unit_range (tuple or list, optional): The buffered range for the time unit values. Defaults to None.
            time_unit_datetime_range (tuple or list, optional): The buffered range as datetime values. Defaults to None.
            time_range (tuple or list, optional): The raw range of time values. Defaults to None.
            alt_range (tuple or list, optional): The buffered range of altitude values. Defaults to None.
            x_range (tuple or list, optional): The buffered range of x-coordinate values (e.g., longitude). Defaults to None.
            y_range (tuple or list, optional): The buffered range of y-coordinate values (e.g., latitude). Defaults to None.
            num_pts_range (tuple or list, optional): The buffered range for the number of points (used in aggregation). Defaults to None.
            colorbar_range (tuple or list, optional): The range of values used for colorbar normalization. Defaults to None.
        """
        self.time_unit_range = time_unit_range
        self.time_unit_datetime_range = time_unit_datetime_range
        self.time_range = time_range
        self.alt_range = alt_range
        self.x_range = x_range
        self.y_range = y_range
        self.num_pts_range = num_pts_range
        self.colorbar_range = colorbar_range