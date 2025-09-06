import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import Polygon
from matplotlib import pyplot as plt


def split_initial(gdf_bounds: gpd.GeoDataFrame):
    x0 = gdf_bounds.boundary.iloc[0].coords.xy[0]
    y0 = gdf_bounds.boundary.iloc[0].coords.xy[1]
    x0a = np.array(x0[:-1])
    x0b = x0a + (np.array(x0[1:]) - x0a) / 2.0

    y0a = np.array(y0[:-1])
    y0b = y0a + (np.array(y0[1:]) - y0a) / 2.0

    xnew = []
    ynew = []
    for k in range(len(x0a)):
        xnew.append(x0a[k])
        xnew.append(x0b[k])
        ynew.append(y0a[k])
        ynew.append(y0b[k])
    xnew.append(x0a[0])
    ynew.append(y0a[0])

    xnew = np.array(xnew)
    ynew = np.array(ynew)

    gdf_bounds_new = gpd.GeoDataFrame(
        geometry=[Polygon(np.array([xnew, ynew]).T)], crs=gdf_bounds.crs
    )

    return gdf_bounds_new


def get_initial_triangulation(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf_cdt_geom = gdf.constrained_delaunay_triangles().explode()

    gdf_out = (
        gpd.GeoDataFrame(geometry=gdf_cdt_geom, crs=gdf.crs)
        .reset_index()
        .drop(columns=["index"])
    )
    return gdf_out


def filter_triangles(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    pass


def get_coordinates_initial(gdf: gpd.GeoDataFrame):
    gdf_cdt = gdf.copy()
    for i, coord in enumerate(["x", "y"]):
        for j in range(3):
            gdf_cdt[f"{coord}_{j}"] = [
                gdf_cdt["geometry"].boundary.iloc[k].coords.xy[i][j]
                for k in range(len(gdf_cdt))
            ]
    return gdf_cdt


def calculate_variables(
    gdf: gpd.GeoDataFrame, angle_min: float = 0, area_max: float = 0
) -> gpd.GeoDataFrame:
    gdf_cdt = gdf.copy()
    v0 = np.array([gdf_cdt["x_0"].values, gdf_cdt["y_0"].values]).T
    v1 = np.array([gdf_cdt["x_1"].values, gdf_cdt["y_1"].values]).T - v0
    v2 = np.array([gdf_cdt["x_2"].values, gdf_cdt["y_2"].values]).T - v0
    v1n = (v1.T / np.sqrt(np.sum(v1 * v1, axis=1))).T
    v2n = (v2.T / np.sqrt(np.sum(v2 * v2, axis=1))).T
    theta1 = 180.0 / np.pi * np.arccos(np.sum(v1n * v2n, axis=1))
    v0a = np.array([gdf_cdt["x_1"].values, gdf_cdt["y_1"].values]).T
    v1a = np.array([gdf_cdt["x_0"].values, gdf_cdt["y_0"].values]).T - v0a
    v2a = np.array([gdf_cdt["x_2"].values, gdf_cdt["y_2"].values]).T - v0a

    v1an = (v1a.T / np.sqrt(np.sum(v1a * v1a, axis=1))).T
    v2an = (v2a.T / np.sqrt(np.sum(v2a * v2a, axis=1))).T

    theta2 = 180.0 / np.pi * np.arccos(np.sum(v1an * v2an, axis=1))

    d1 = 2 * (v1.T[0] * v2.T[1] - v1.T[1] * v2.T[0])

    ux = (v2.T[1] * np.sum(v1**2, axis=1) - v1.T[1] * np.sum(v2**2, axis=1)) / d1
    uy = (v1.T[0] * np.sum(v2**2, axis=1) - v2.T[0] * np.sum(v1**2, axis=1)) / d1
    r2 = ux**2 + uy**2
    gdf_cdt["r2"] = r2
    gdf_cdt["cx"] = ux + gdf_cdt["x_0"]
    gdf_cdt["cy"] = uy + gdf_cdt["y_0"]
    if angle_min > 0:
        gdf_cdt["angle_ok"] = (
            np.min(np.array([theta1, theta2, 180 - theta1 - theta2]), axis=0)
            > angle_min
        )
    else:
        gdf_cdt["angle_ok"] = True
    if area_max > 0:
        gdf_cdt["area_ok"] = gdf_cdt.area / area_max < 1
    else:
        gdf_cdt["area_ok"] = True
    gdf_cdt["ok"] = gdf_cdt["area_ok"] * gdf_cdt["angle_ok"]
    return gdf_cdt


def refine_step(
    gdf: gpd.GeoDataFrame, angle_min: float = 0, area_max: float = 0
) -> gpd.GeoDataFrame:
    gdf_cdt = gdf.copy()
    gdf_cdt["index_old"] = gdf_cdt.index
    gdf_cdt[~gdf_cdt["ok"]]
    center_group = gdf_cdt[~gdf_cdt["ok"]].sort_values(by="r2", ascending=False)
    gdf_cnt_group = gpd.GeoDataFrame(
        center_group,
        geometry=gpd.points_from_xy(center_group["cx"], center_group["cy"]),
        crs=gdf.crs,
    ).sort_values(by="r2")
    gdf_cnt_group["idn"] = range(len(gdf_cnt_group))
    gdf_cnt_group.set_index("idn", inplace=True)
    gdf_cdt["id_tmp"] = range(len(gdf_cdt))
    gdf_join = (
        gdf_cdt[
            [
                "geometry",
                "id_tmp",
                "index_old",
                "x_0",
                "x_1",
                "x_2",
                "y_0",
                "y_1",
                "y_2",
            ]
        ]
        .sjoin(gdf_cnt_group[["geometry", "r2", "cx", "cy"]])
        .sort_values(by=["id_tmp", "r2"])
    )
    gdf_join["id_mix"] = range(len(gdf_join))
    gdf_greatest = gdf_join.set_index("id_mix").groupby("id_tmp").head(1)
    id_to_drop = gdf_greatest["index_old"].values
    gdf_list = []
    for i in range(3):
        gdf_tmp = gdf_greatest.copy()
        gdf_tmp[f"x_{i}"] = gdf_tmp["cx"]
        gdf_tmp[f"y_{i}"] = gdf_tmp["cy"]
        gdf_list += [gdf_tmp]
    gdf_tmp = pd.concat(gdf_list)
    geom_new = []
    for elem in gdf_tmp[["x_0", "y_0", "x_1", "y_1", "x_2", "y_2"]].values:
        geom_new.append(
            Polygon(((elem[0], elem[1]), (elem[2], elem[3]), (elem[4], elem[5])))
        )
    gdf_tmp["geometry"] = geom_new

    gdf_tmp = calculate_variables(gdf_tmp, angle_min=angle_min, area_max=area_max)
    gdf_out = pd.concat([gdf_cdt[~gdf_cdt.index.isin(id_to_drop)], gdf_tmp])

    gdf_out = gdf_out.reset_index().drop(columns="index")
    return gdf_out


def segment_circle_intersection(
    x0, y0, x1, y1, r2: float = 1, cx: float = 0, cy: float = 0
):

    p0 = np.array([(x0 - cx) / np.sqrt(r2), (y0 - cy) / np.sqrt(r2)])
    p1 = np.array([(x1 - cx) / np.sqrt(r2), (y1 - cy) / np.sqrt(r2)])
    d = p1 - p0

    a = np.dot(d, d)
    b = 2 * np.dot(p0, d)
    c = np.dot(p0, p0) - 1

    disc = b**2 - 4 * a * c
    if disc < 0:
        return False  # no real intersection

    sqrt_disc = np.sqrt(disc)
    t1 = (-b - sqrt_disc) / (2 * a)
    t2 = (-b + sqrt_disc) / (2 * a)

    return np.sum((t1 >= 0) & (t1 <= 1) | (t2 >= 0) & (t2 <= 1))


def refine_step_ruppert(
    gdf: gpd.GeoDataFrame, angle_min: float = 0, area_max: float = 0
) -> gpd.GeoDataFrame:
    gdf_cdt = gdf.copy()
    gdf_cdt["index_old"] = gdf_cdt.index
    gdf_wrong = gdf_cdt[~gdf_cdt["ok"]].sort_values(by="r2", ascending=False)
    gdf_ok = gdf_cdt[gdf_cdt["ok"]].sort_values(by="r2", ascending=False)

    gdf_cnt_group = gpd.GeoDataFrame(
        gdf_wrong,
        geometry=gpd.points_from_xy(gdf_wrong["cx"], gdf_wrong["cy"]),
        crs=gdf.crs,
    )

    filter_add_center = gdf_wrong["geometry"].contains(gdf_cnt_group["geometry"])
    filter_split_triangle = (1 - filter_add_center).astype(bool)
    gdf_add_center = gdf_wrong[filter_add_center]
    gdf_list = []
    for i in range(3):
        gdf_tmp = gdf_add_center.copy()
        gdf_tmp[f"x_{i}"] = gdf_tmp["cx"]
        gdf_tmp[f"y_{i}"] = gdf_tmp["cy"]
        gdf_list += [gdf_tmp]
    gdf_tmp = pd.concat(gdf_list)
    geom_new = []
    for elem in gdf_tmp[["x_0", "y_0", "x_1", "y_1", "x_2", "y_2"]].values:
        geom_new.append(
            Polygon(((elem[0], elem[1]), (elem[2], elem[3]), (elem[4], elem[5])))
        )
    gdf_tmp["geometry"] = geom_new

    gdf_split_triangle = gdf_wrong[filter_split_triangle].copy()

    split_01 = np.array(
        [
            segment_circle_intersection(
                elem["x_0"],
                elem["y_0"],
                elem["x_1"],
                elem["y_1"],
                elem["r2"],
                elem["cx"],
                elem["cy"],
            )
            for k, elem in gdf_split_triangle.iterrows()
        ]
    )

    split_02 = np.array(
        [
            segment_circle_intersection(
                elem["x_0"],
                elem["y_0"],
                elem["x_2"],
                elem["y_2"],
                elem["r2"],
                elem["cx"],
                elem["cy"],
            )
            for k, elem in gdf_split_triangle.iterrows()
        ]
    )

    split_12 = np.array(
        [
            segment_circle_intersection(
                elem["x_1"],
                elem["y_1"],
                elem["x_2"],
                elem["y_2"],
                elem["r2"],
                elem["cx"],
                elem["cy"],
            )
            for k, elem in gdf_split_triangle.iterrows()
        ]
    )

    print("MIN:", np.min(split_01 + split_02 + split_12))

    gdf_split_triangle["split_01"] = split_01
    gdf_split_triangle["split_02"] = split_02
    gdf_split_triangle["split_12"] = split_12

    gdf_split_filt = gdf_split_triangle[
        gdf_split_triangle["split_01"]
        + gdf_split_triangle["split_02"]
        + gdf_split_triangle["split_12"]
        == 0
    ].copy()

    gdf_split_filt1 = gdf_split_triangle[
        gdf_split_triangle["split_01"]
        + gdf_split_triangle["split_02"]
        + gdf_split_triangle["split_12"]
        > 0
    ].copy()

    gdf_split_filt["l01"] = (gdf_split_filt["x_1"] - gdf_split_filt["x_0"]) ** 2 + (
        gdf_split_filt["y_1"] - gdf_split_filt["y_0"]
    ) ** 2
    gdf_split_filt["l02"] = (gdf_split_filt["x_2"] - gdf_split_filt["x_0"]) ** 2 + (
        gdf_split_filt["y_2"] - gdf_split_filt["y_0"]
    ) ** 2
    gdf_split_filt["l12"] = (gdf_split_filt["x_2"] - gdf_split_filt["x_1"]) ** 2 + (
        gdf_split_filt["y_2"] - gdf_split_filt["y_1"]
    ) ** 2

    gdf_split_filt[
        (
            (gdf_split_filt["l12"] > gdf_split_filt["l02"])
            & (gdf_split_filt["l12"] > gdf_split_filt["l01"])
        )
    ]["split_12"] = 1
    gdf_split_filt[
        (
            (gdf_split_filt["l02"] > gdf_split_filt["l12"])
            & (gdf_split_filt["l02"] > gdf_split_filt["l01"])
        )
    ]["split_02"] = 1
    gdf_split_filt[
        (
            (gdf_split_filt["l01"] > gdf_split_filt["l02"])
            & (gdf_split_filt["l01"] > gdf_split_filt["l12"])
        )
    ]["split_01"] = 1
    gdf_split_triangle = pd.concat([gdf_split_filt, gdf_split_filt1])

    gdf1a = gdf_split_triangle[gdf_split_triangle["split_01"].astype(bool)].copy()
    gdf1b = gdf_split_triangle[gdf_split_triangle["split_01"].astype(bool)].copy()
    gdf1res = gdf_split_triangle[~gdf_split_triangle["split_01"].astype(bool)].copy()

    gdf1a["x_1"] = gdf1a["x_0"] + (gdf1a["x_1"] - gdf1a["x_0"]) / 2
    gdf1a["y_1"] = gdf1a["y_0"] + (gdf1a["y_1"] - gdf1a["y_0"]) / 2
    gdf1b["x_0"] = gdf1b["x_0"] + (gdf1b["x_1"] - gdf1b["x_0"]) / 2
    gdf1b["y_0"] = gdf1b["y_0"] + (gdf1b["y_1"] - gdf1b["y_0"]) / 2

    gdf1 = pd.concat([gdf1a, gdf1b, gdf1res])

    gdf2a = gdf1[gdf1["split_02"].astype(bool)].copy()
    gdf2b = gdf1[gdf1["split_02"].astype(bool)].copy()
    gdf2res = gdf1[~gdf1["split_02"].astype(bool)].copy()

    gdf2a["x_2"] = gdf2a["x_0"] + (gdf2a["x_2"] - gdf2a["x_0"]) / 2
    gdf2a["y_2"] = gdf2a["y_0"] + (gdf2a["y_2"] - gdf2a["y_0"]) / 2
    gdf2b["x_0"] = gdf2b["x_0"] + (gdf2a["x_2"] - gdf2b["x_0"]) / 2
    gdf2b["y_0"] = gdf2b["y_0"] + (gdf2a["y_2"] - gdf2b["y_0"]) / 2

    gdf2 = pd.concat([gdf2a, gdf2b, gdf2res])

    gdf3a = gdf2[gdf2["split_12"].astype(bool)].copy()
    gdf3b = gdf2[gdf2["split_12"].astype(bool)].copy()
    gdf3res = gdf2[~gdf2["split_12"].astype(bool)].copy()

    gdf3a["x_2"] = gdf3a["x_1"] + (gdf3a["x_2"] - gdf3a["x_1"]) / 2
    gdf3a["y_2"] = gdf3a["y_1"] + (gdf3a["y_2"] - gdf3a["y_1"]) / 2
    gdf3b["x_1"] = gdf3b["x_1"] + (gdf3a["x_2"] - gdf3b["x_1"]) / 2
    gdf3b["y_1"] = gdf3b["y_1"] + (gdf3a["y_2"] - gdf3b["y_1"]) / 2

    gdf_angle_fin = pd.concat([gdf3a, gdf3b, gdf3res]).drop(
        columns=["split_01", "split_02", "split_12"]
    )
    geom_new = []

    for elem in gdf_angle_fin[["x_0", "y_0", "x_1", "y_1", "x_2", "y_2"]].values:
        geom_new.append(
            Polygon(((elem[0], elem[1]), (elem[2], elem[3]), (elem[4], elem[5])))
        )
    gdf_angle_fin["geometry"] = geom_new

    gdf_tmp = calculate_variables(gdf_tmp, angle_min=angle_min, area_max=area_max)
    gdf_angle_fin = calculate_variables(
        gdf_angle_fin, angle_min=angle_min, area_max=area_max
    )
    gdf_out = pd.concat([gdf_ok, gdf_tmp, gdf_angle_fin])

    gdf_out = gdf_out.reset_index().drop(columns="index")
    fig, ax = plt.subplots()
    gdf_out.boundary.plot(ax=ax, lw=1, color="lightgray", alpha=0.7)
    fig.savefig("/home/stippe/Downloads/mesh.webp")

    fig, ax = plt.subplots()
    gdf_out.plot("area_ok", ax=ax)
    fig.savefig("/home/stippe/Downloads/mesh_full.webp")

    print("Area:", np.max(gdf_out.area) / area_max)

    return gdf_out
