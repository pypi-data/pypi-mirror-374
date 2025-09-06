import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import LineString, normalize


def get_edges(gdf):
    out = []
    out_v = np.array([])
    for i in range(3):
        g = gdf.boundary.apply(
            lambda p: normalize(LineString(np.array(p.coords.xy).T[[i, i + 1]]))
        ).values
        gdf_out = gpd.GeoDataFrame(
            {"id_seg": [i + 1] * len(g), "id_tri": np.arange(len(g)).astype(int)},
            geometry=g,
            crs=gdf.crs,
        )
        out.append(gdf_out)
        out_v = np.concat([out_v, g])
    gdf_edges = pd.concat(out)
    vert_unique = np.unique(
        np.stack(gdf_edges["geometry"].apply(lambda p: np.array(p.coords.xy).T).values),
        axis=0,
    )
    gdf_unique = gpd.GeoDataFrame(
        {"id_edge": np.arange(len(vert_unique))},
        geometry=[LineString(elem) for elem in vert_unique],
        crs=gdf.crs,
    )
    gdf_unique["length"] = gdf_unique["geometry"].length
    gdf_sjoin = (
        gdf_unique.sjoin(
            pd.concat(out, ignore_index=True), how="inner", predicate="within"
        )
        .sort_values(by=["length", "id_edge", "id_tri", "id_seg"])
        .drop(columns=["index_right"])
    )
    return gdf_sjoin[["id_edge", "id_seg", "id_tri", "length", "geometry"]]


def cross_prod(u, v):
    return u[0] * v[1] - u[1] * v[0]


def calculate_triangle_area(x: np.array) -> float:
    u = x[1] - x[0]
    v = x[2] - x[0]
    return np.abs(cross_prod(u, v)) / 2.0


def calculate_triangle_smaller_angle(x: np.array) -> float:
    out = []
    for ind in [0, 1, 2]:
        indx = [0, 1, 2]
        indx.remove(ind)
        v0 = x[ind].astype(float)
        v1 = x[indx[0]].astype(float)
        v2 = x[indx[1]].astype(float)
        x1 = v1 - v0
        x2 = v2 - v0
        x1 /= np.sqrt(np.sum(x1**2))
        x2 /= np.sqrt(np.sum(x2**2))
        out.append(np.arccos(x1 @ x2))
    return 180.0 / np.pi * np.min(np.abs(out))


def get_triangle_circumcenter(x: np.array) -> np.array:
    v0 = x[0]
    v1 = x[1]
    v2 = x[2]
    b = v1 - v0
    c = v2 - v0
    b2 = np.sum(b**2)
    c2 = np.sum(c**2)
    d2 = 2 * (b[0] * c[1] - b[1] * c[0])
    ux = (c[1] * b2 - b[1] * c2) / d2
    uy = (b[0] * c2 - c[0] * b2) / d2
    cv = np.array([ux, uy]) + v0
    return cv


def point_inside_triangle(p, x):
    """

    :param p: coordinates of the point
    :param x: coordinates of the vertices of the triangle
    :return: True if the point is interior to the triangle, False otherwise
    """
    p0 = p - x[0]
    y = x - x[0]
    denom = cross_prod(y[1], y[2])
    a = (cross_prod(p0, y[2]) - cross_prod(y[0], y[2])) / denom
    b = (cross_prod(y[1], p0) - cross_prod(y[1], y[0])) / denom
    cond = (a > 0) and (b > 0) and (a + b < 1)
    return cond


def segments_are_intercepting(
    x1: np.array, x2: np.array, x3: np.array, x4: np.array
) -> bool:
    """
    Determines if the segment p and q are intercepting
    :param x1: np.array 2d array containing p0
    :param x2: np.array 2d array containing p1
    :param x3: np.array 2d array containing q0
    :param x4: np.array 2d array containing q1
    :return: bool
    True if the segments have a common point, False otherwise
    """
    denom = cross_prod(x1 - x2, x3 - x4)
    tnum = cross_prod(x1 - x3, x3 - x4)
    unum = -cross_prod(x1 - x2, x1 - x3)
    t = tnum / denom
    u = unum / denom
    cond = t > 0 and t < 1 and u > 0 and u < 1
    return cond
