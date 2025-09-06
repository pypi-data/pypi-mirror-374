# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from .art_handler import ArtHandler
from .corona_handler import CoronaHandler
from .default_max_handler import DefaultMaxHandler
from .vray_handler import VrayHandler
from .redshift_handler import RedshiftHandler

__all__ = ["DefaultMaxHandler", "get_render_handler"]


def get_render_handler(renderer: str = "Default_Scanline_Renderer") -> DefaultMaxHandler:
    """
    Returns the render handler instance for the given renderer.

    Args:
    :param renderer: The renderer to get the render handler of. Defaults to "Default_Scanline_Renderer".
    :type renderer: (str, optional)

    :returns: the Render Handler instance for the given renderer.
    """
    if renderer == "ART_Renderer":
        return ArtHandler()
    elif renderer == "Corona":
        return CoronaHandler()
    elif renderer.startswith("V_Ray_GPU_"):
        return VrayHandler(gpu=True)
    elif renderer.startswith("V_Ray_"):
        return VrayHandler(gpu=False)
    elif renderer == "Redshift_Renderer":
        return RedshiftHandler()
    else:
        return DefaultMaxHandler()
