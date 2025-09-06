import matplotlib.patches as mpatches
from matplotlib.axes import Axes
from ._ax_functions import _axTools

__axf__ = _axTools()

def show_values(
    ax=None,
    kind="bar",
    dec=3,
    loc="top",
    prefix: str = "",
    xpad: float = 0,
    ypad: float = 0,
    kw_values={},
):
    my_kw = {"dec": dec, "xpad": xpad, "ypad": ypad, "loc": loc, "prefix": prefix}

    if kind == "bar":
        __axf__.show_values_bar(ax=ax, args=my_kw, **kw_values)

def get_tickslabel(ax=None, axis="x") -> list[str]:
    return __axf__.get_tickslabel(ax=ax, axis=axis)

def set_tickslabel(
    ax=None,
    axis="x",
    visible=True,
    labels: list = [],
    rotation=0,
    loc="default",
    bgcolors=None,
    shadow_line=None,
    shadow_color=None,
    **kwargs,
):

    args = {
        "axis": axis,
        "visible": visible,
        "labels": labels,
        "rotation": rotation,
        "loc": loc,
        "bgcolors": bgcolors,
    }

    if shadow_line is not None:
        args["shadow_line"] = shadow_line

    if shadow_color is not None:
        args["shadow_color"] = shadow_color

    return __axf__.set_tickslabel(ax=ax, args=args, **kwargs)

def theme(
    op: str = "spine",
    top: bool = False,
    right: bool = False,
    left: bool = False,
    bottom: bool = False,
    despine_trim: bool = False,
    despine_offset: int = 0,
    spine_butt="left",
    ax=None,
):
    return __axf__.theme(
        op=op,
        top=top,
        right=right,
        left=left,
        bottom=bottom,
        despine_trim=despine_trim,
        despine_offset=despine_offset,
        spine_butt=spine_butt,
        ax=ax,
    )

def set_title(
    ax=None,
    title: str = "",
    loc: str = "center",
    xpad: float = 0.0,
    ypad: float = 0.0,
    kw_title: dict = {},
):
    args = {
        "xpad": xpad,
        "ypad": ypad,
    }

    return __axf__.set_title(ax=ax, title=title, loc=loc, args=args, **kw_title)

def set_subtitle(
    ax=None,
    subtitle: str = "",
    loc: str = "left",
    xpad: float = 0.0,
    ypad: float = 0.0,
    kw_subtitle: dict = {},
):
    args = {
        "xpad": xpad,
        "ypad": ypad,
    }

    return __axf__.set_subtitle(
        ax=ax, subtitle=subtitle, loc=loc, args=args, **kw_subtitle
    )

def set_legend(
    ax=None,
    show: bool = True,
    title="",
    title_loc: str = "left",
    ncols: int = 1,
    loc="best",
    title_fontsize=None,
    label_fontsize=None,
    labels: list = [],
    handles: list = [],
    borderpad=0.82,
    **kwargs,
):
    return __axf__.set_legend(
        ax=ax,
        show=show,
        title=title,
        title_loc=title_loc,
        ncols=ncols,
        loc=loc,
        title_fontsize=title_fontsize,
        label_fontsize=label_fontsize,
        labels=labels,
        handles=handles,
        borderpad=borderpad,
        **kwargs,
    )

def set_alpha(ax=None, alpha: float = 1.0):
    if ax is not None:
        if isinstance(ax, Axes):
            ch = ax.get_children()
            for c in ch:
                if isinstance(c, _axTools.artistList):
                    c.set_alpha(alpha)
                elif isinstance(c, mpatches.Rectangle):
                    """All rectangles and not background rectangle"""
                    if (
                        not float(c.get_width()) == 1.0
                        and not float(c.get_height()) == 1.0
                    ):
                        c.set_alpha(alpha)
