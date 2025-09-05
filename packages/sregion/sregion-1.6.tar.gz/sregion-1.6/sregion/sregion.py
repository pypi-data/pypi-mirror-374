import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path

import astropy.units as u
import astropy.wcs as pywcs
from astropy.coordinates import Angle

from shapely.geometry import Polygon

__all__ = ["SRegion", "patch_from_polygon"]


def _parse_circle(spli, ncircle=32):
    """
    Parse circle from split string

    Parameters
    ----------
    spli : list
        List of circle parameters ``['x', 'y', 'radius']``

    ncircle : int
        Number of points to sample around the diameter of the circle

    Returns
    -------
    poly_i : array-like
        2D xy array

    """
    if len(spli) != 3:
        msg = f"Input does not have three elements ({spli})"
        raise ValueError(msg)

    x0, y0 = np.asarray(spli[:2], dtype=float)
    cosd = np.cos(y0 / 180 * np.pi)

    r0 = spli[2]
    if r0.endswith('"'):
        scl = float(r0[:-1]) / 3600
    elif r0.endswith("'"):
        scl = float(r0[:-1]) / 60
    else:
        try:
            scl = float(r0)
        except ValueError:
            scl = 1.0

        cosd = 1.0

    _theta = np.linspace(0, 2 * np.pi, ncircle + 1)[:-1]
    _xc = np.cos(_theta)
    _yc = np.sin(_theta)

    poly_i = np.array([_xc / cosd * scl + x0, _yc * scl + y0]).T
    return poly_i


def _parse_box(spli):
    """
    Parse box from split string

    Parameters
    ----------
    spli : list
        List of box parameters ``['x', 'y', 'width', 'height']``

    Returns
    -------
    poly_i : array-like
        2D xy array
    """
    if len(spli) != 4:
        msg = f"Input does not have four elements ({spli})"
        raise ValueError(msg)

    # Extract center of box
    x0, y0 = np.asarray(spli[:2], dtype=float)
    dx, dy = spli[2], spli[3]

    # Parse optional sky coordinates    
    if dx.endswith('"'):
        cosd = np.cos(y0 / 180.0 * np.pi)
        half_width = float(dx[:-1]) / 3600 / cosd / 2
    elif dx.endswith("'"):
        cosd = np.cos(y0 / 180.0 * np.pi)
        half_width = float(dx[:-1]) / 60 / cosd / 2
    else:
        try:
            half_width = float(dx) / 2
        except ValueError:
            half_width = 1.0

    if dy.endswith('"'):
        cosd = np.cos(y0 / 180.0 * np.pi)
        half_height = float(dy[:-1]) / 3600 / 2
    elif dy.endswith("'"):
        cosd = np.cos(y0 / 180.0 * np.pi)
        half_height = float(dy[:-1]) / 60 / 2
    else:
        try:
            half_height = float(dy) / 2
        except ValueError:
            half_height = 1.0

    poly_i = np.array(
        [
            [x0 - half_width, y0 - half_height],
            [x0 + half_width, y0 - half_height],
            [x0 + half_width, y0 + half_height],
            [x0 - half_width, y0 + half_height],
        ]
    )
    return poly_i


def _wrap_xy(xy):
    """
    Wrap x coordinate as an angle

    Parameters
    ----------
    xy : (M,2) array
        Coordinates

    Returns
    -------
    wxy: (M,2) array
        Array with first column wrapped at 360 degrees

    """
    wxy = xy * 1.0
    ra = Angle(xy[:, 0] * u.deg).wrap_at(360 * u.deg).value
    wxy[:, 0] = ra
    return wxy


def _parse_sregion(sregion, ncircle=32, verbose=False, **kwargs):
    """
    Parse an S_REGION string with CIRCLE, POLYGON or BOX

    Parameters
    ----------
    sregion : str
        Region string

    Returns
    -------
    poly : list
        List of 2D xy arrays

    """
    if hasattr(sregion, "decode"):
        decoded = sregion.decode("utf-8").strip().upper()
    else:
        decoded = sregion.strip().upper()

    # Strip out prefix for some STS-C regions
    for strip_string in ["UNION", "ICRS", "FK5", "IMAGE", "WORLD"]:
        if (strip_string in decoded) & verbose:
            print("Strip {0} from {1}".format(strip_string, sregion))

        decoded = decoded.replace(strip_string, "")

    decoded = decoded.strip()
    if decoded.startswith("("):
        decoded = decoded[1:]

    if decoded.endswith(")"):
        decoded = decoded[:-1]

    decoded = decoded.strip()
    polyspl = (
        decoded.replace("POLYGON", "xxx").replace("CIRCLE", "xxx").replace("BOX", "xxx")
    )
    polyspl = polyspl.split("xxx")

    poly = []
    for pp in polyspl:
        if not pp:
            continue

        # strip out ()
        pp = pp.replace("(", "").replace(")", "")

        # ',' or ' ' delimiters
        if "," in pp:
            spl = pp.strip().split(",")
        else:
            spl = pp.strip().split()

        for ip, p in enumerate(spl):
            # Find index of first float
            try:
                _ = float(p)
                break
            except ValueError:
                continue

        if len(spl[ip:]) == 3:
            # Circle
            poly_i = _parse_circle(spl[ip:], ncircle=ncircle)
        elif len(spl[ip:]) == 4:
            # Box
            poly_i = _parse_box(spl[ip:])
        else:
            poly_i = np.asarray(spl[ip:], dtype=float).reshape((-1, 2))

        if len(poly_i) < 2:
            continue
        poly.append(poly_i)

    return poly


class SRegion(object):
    SREGION_PREFIX = "POLYGON ICRS"

    def __init__(self, inp, label=None, wrap=True, get_convex_hull=False, pad=None, **kwargs):
        """
        Helper class for parsing an S_REGION strings and general polygon
        tools

        Parameters
        ----------
        inp : str, (M,2) array, `~astropy.wcs.WCS`, `shapely.geometry.polygon.Polygon`

            Can be a "S_REGION" string, an array, or an `astropy.wcs.WCS`
            object from which the corners will be extracted with
            `~astropy.wcs.WCS.calc_footprint`.

        label : str
            Optional label attached to regions and patches

        wrap : bool
            Wrap first dimension as an angle between (0, 360) degrees

        get_convex_hull : bool
            Compute a `scipy.spatial.ConvexHull` from ``inp`` before generating
        """
        if isinstance(inp, str):
            self.xy = _parse_sregion(inp, **kwargs)

        elif hasattr(inp, "sum"):
            # NDarray
            sh = inp.shape
            if inp.ndim != 2:
                raise ValueError(f"Input shape {sh} is not (M,2)")
            else:
                if inp.shape[1] != 2:
                    if inp.shape[0] != 2:
                        raise ValueError(f"Input shape {sh} is not (M,2)")
                    else:
                        inp = inp.T

            if get_convex_hull:
                from scipy.spatial import ConvexHull
                inp = inp[ConvexHull(inp).vertices, :]

            self.xy = [inp]

        elif isinstance(inp, list):
            self.xy = inp

        elif isinstance(inp, pywcs.WCS):
            self.xy = [inp.calc_footprint()]

        elif hasattr(inp, "buffer"):
            # Shapely polygon
            if hasattr(inp, "geoms"):
                self.xy = [np.array(p.boundary.xy).T for p in inp.geoms]
            elif hasattr(inp, "__len__"):
                self.xy = [np.array(p.boundary.xy).T for p in inp]
            else:
                self.xy = [np.array(inp.boundary.xy).T]

        else:
            raise IOError("input must be ``str``, ``list``, or ``np.array``")

        if wrap:
            self.xy = [_wrap_xy(xy_i) for xy_i in self.xy]

        self.inp = inp
        self.ds9_properties = ""
        self.label = label
        self.is_wrapped = wrap

        if pad is not None:
            self.pad(scale=pad, in_place=True, **kwargs)

    @property
    def N(self):
        return len(self.xy)

    @property
    def centroid(self):
        return [np.mean(fp, axis=0) for fp in self.xy]

    def sky_buffer(self, buffer_deg):
        """
        Buffer polygons accounting for cos(dec)
        """

        new_xy = []
        for xy, c in zip(self.xy, self.centroid):
            cosd = np.array([1, np.cos(c[1] / 180 * np.pi)])
            p = Polygon((xy - c) * cosd).convex_hull.buffer(buffer_deg)
            xyp = np.array(p.boundary.xy).T
            new_xy.append((xyp / cosd) + c)

        self.xy = new_xy

    @property
    def path(self):
        """
        `~matplotlib.path.Path` object
        """
        return [Path(fp) for fp in self.xy]

    @property
    def shapely(self):
        """
        `~shapely.geometry.Polygon` object.
        """
        return [Polygon(fp).convex_hull for fp in self.xy]

    @property
    def geoms(self):
        """
        compatibility for shapely >= 1.8, 2.0
        """
        if hasattr(self.shapely, "geoms"):
            return self.shapely.geoms
        else:
            return self.shapely

    @property
    def area(self):
        """
        Area of shapely polygons
        """
        return [sh.area for sh in self.geoms]

    def sky_area(self, unit=u.arcmin**2):
        """
        Assuming coordinates provided are RA/Dec degrees, compute area
        """
        cosd = np.cos(self.centroid[0][1] / 180 * np.pi)
        return [(sh.area * cosd * u.deg**2).to(unit) for sh in self.geoms]

    def matplotlib_patch(self, **kwargs):
        """
        `~matplotlib.patches.PathPatch` object
        """
        if "label" not in kwargs:
            kwargs["label"] = self.label

        patches = [PathPatch(Path(xy), **kwargs) for xy in self.xy]

        return patches

    def descartes_patch(self, **kwargs):
        """
        `~descartes.PolygonPatch` object

        Deprecated because descartes doesn't seem to work with shapely>=2.0
        """
        from descartes import PolygonPatch

        if "label" not in kwargs:
            kwargs["label"] = self.label

        return [PolygonPatch(p, **kwargs) for p in self.geoms]

    def patch(self, **kwargs):
        """
        general patch object
        """
        try:
            return self.descartes_patch(**kwargs)
        except IndexError:
            return self.matplotlib_patch(**kwargs)
        except ImportError:
            return self.matplotlib_patch(**kwargs)

    def get_patch(self, **kwargs):
        """
        `~descartes.PolygonPatch` object

        ** Deprecated, use patch **
        """
        return self.patch(**kwargs)

    def add_patch_to_axis(self, ax, **kwargs):
        """
        Add patches to a plot axis

        Parameters
        ----------
        ax : matplotlib axis
            Axis in which do draw patches

        kwargs : dict
            Keyword arguments passed to `~sregion.SRegion.get_patch`

        """
        for patch in self.get_patch(**kwargs):
            ax.add_patch(patch)

    def union(self, shape=None, as_polygon=False):
        """
        Union of self and `shape` object.  If no `shape` provided, then
        return union of (optional) multiple components of self
        """
        if shape is None:
            un = self.shapely[0]
        else:
            un = shape

        for s in self.geoms:
            un = un.union(s)

        if as_polygon:
            return un
        else:
            return SRegion(un)

    def intersects(self, shape):
        """
        Union of self and `shape` object
        """
        test = False
        for s in self.geoms:
            test |= s.intersects(shape)

        return test

    @property
    def region(self):
        """
        Polygon string in DS9 region format
        """
        pstr = "polygon({0})"
        if hasattr(self, "ds9_properties"):
            tail = "{0}".format(self.ds9_properties)
        else:
            tail = ""

        if hasattr(self, "label"):
            if self.label is not None:
                tail += " text={xx}".replace("xx", self.label)

        if tail:
            tail = " # " + tail

        return [
            pstr.format(",".join([f"{c:.6f}" for c in fp.flatten()])) + tail
            for fp in self.xy
        ]

    @property
    def s_region(self):
        """
        Polygon as VO s_region
        """
        pstr = self.SREGION_PREFIX + " {0}"
        polys = [
            pstr.format(" ".join([f"{c:.6f}" for c in fp.flatten()])) for fp in self.xy
        ]
        return " ".join(polys)

    def polystr(self, precision=6):
        """
        String suitable for, e.g., SQL, e.g.,

        ((x1,y1),(x2,y2),...)
        """
        np.set_printoptions(precision=precision)

        fps = []
        for xy in self.xy:
            fmt = "({0:.pf},{1:.pf})".replace("p", f"{precision:0}")
            fpstr = [fmt.format(*row) for row in xy]
            fps.append("(" + ",".join(fpstr) + ")")

        return fps

    def pad(self, scale=1.5, center="centroid", sky=True, in_place=True, **kwargs):
        """
        Expand or shrink regions

        Parameters
        ----------
        scale : float
            Scale factor, > 1 expands, < 1 contracts

        sky : bool
            Account for cos(declination)

        in_place : bool
            Update `xy` attribute in-place

        Returns
        -------
        result : `sregion.SRegion`, None
            New region object if ``in_place = True``

        """
        xy_pad = []
        if center in ["centroid"]:
            x0 = self.centroid
        else:
            x0 = [center] * self.N

        for j in range(self.N):
            if sky:
                cosd = np.cos([x0[j][1]/180*np.pi, 0])
            else:
                cosd = np.ones(2)

            xy_pad.append(
                ((self.xy[j] - x0[j]) * cosd) * scale / cosd + x0[j]
            )

        if in_place:
            self.xy = xy_pad
            result = None
        else:
            result = SRegion(xy_pad, wrap=self.is_wrapped, label=self.label)

        return result


#### PatchPolygon
# descartes no longer works with shapely>=2.0
# this is similar do descartes and taken from
# https://codereview.stackexchange.com/questions/232294/plotting-shapely-polygon-in-matplotlib
# credit: Bruno Vermeulen and Graipher at stackexchange


class PatchPolygon:
    """ """

    def __init__(self, polygon, **kwargs):
        polygon_path = self.pathify(polygon)
        self._patch = PathPatch(polygon_path, **kwargs)

    @property
    def patch(self):
        """get a Patch object"""
        return self._patch

    @staticmethod
    def generate_codes(n):
        """The first command needs to be a "MOVETO" command,
        all following commands are "LINETO" commands.
        """
        return [Path.MOVETO] + [Path.LINETO] * (n - 1)

    def pathify(self, polygon):
        """Convert coordinates to path vertices. Objects produced by Shapely's
        analytic methods have the proper coordinate order, no need to sort.

        The codes will be all "LINETO" commands, except for "MOVETO"s at the
        beginning of each subpath
        """
        vertices = list(polygon.exterior.coords)
        codes = self.generate_codes(len(polygon.exterior.coords))

        for interior in polygon.interiors:
            vertices.extend(interior.coords)
            codes.extend(self.generate_codes(len(interior.coords)))

        return Path(vertices, codes)


def patch_from_polygon(polygon, **kwargs):
    """
    Generate the Path object from `PatchPolygon`

    Parameters
    ----------
    polygon : `shapely.geometry.Polygon`
        Input polygon object

    kwargs : dict
        Keywords to pass when generating the ``patch``

    Returns
    -------
    patch : `from matplotlib.patches.PathPatch`
        The patch that can be added to a `matplotlib` figure

    """
    obj = PatchPolygon(polygon, **kwargs)
    return obj._patch
