import numpy as np
import pandas as pd
import geopandas as gpd

# import seaborn as sns
# import matplotlib as mpl
# from matplotlib import pyplot as plt
from shapely import LineString, Polygon, Point, normalize


def get_edges(gdf):
    out = []
    out_v = np.array([])
    for i in range(3):
        g = gdf.boundary.apply(
            lambda p: normalize(LineString(np.array(p.coords.xy).T[[i, i + 1]]))
        ).values
        g1 = gdf.boundary.apply(
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


def find_set(gdf_sjoin, lmax):
    if np.sum(gdf_sjoin.length > lmax):
        pool = gdf_sjoin[gdf_sjoin.length > lmax].sort_values(by="length")
        selected_edges = [pool.head(1)["id_edge"].values[0]]
        selected_triangles = gdf_sjoin[gdf_sjoin["id_edge"].isin(selected_edges)][
            "id_tri"
        ].to_list()
        forbidden_edges = gdf_sjoin[gdf_sjoin["id_tri"].isin(selected_triangles)][
            "id_edge"
        ].to_list()
        for k, elem in pool.iterrows():
            if elem["id_edge"] not in forbidden_edges:
                selected_edges += [elem["id_edge"]]
                selected_triangles = gdf_sjoin[
                    gdf_sjoin["id_edge"].isin(selected_edges)
                ]["id_tri"].to_list()
                forbidden_edges = gdf_sjoin[
                    gdf_sjoin["id_tri"].isin(selected_triangles)
                ]["id_edge"].to_list()
        df_out = gdf_sjoin[gdf_sjoin["id_edge"].isin(selected_edges)]
        return df_out.sort_values(by=["id_tri", "id_seg"])
    else:
        return gdf_sjoin[gdf_sjoin.length > lmax]


def get_new_geom(gdf_sjoin, gdf_out):
    crs = gdf_sjoin.crs
    gdf_sjoin = gdf_sjoin.copy()
    gdf_out = gdf_out.copy()
    gdf_keep = gdf_sjoin[~gdf_sjoin["id_tri"].isin(gdf_out["id_tri"])]
    gdf1 = (
        gdf_sjoin[
            (
                (gdf_sjoin["id_tri"].isin(gdf_out["id_tri"]))
                & (~gdf_sjoin["id_edge"].isin(gdf_out["id_edge"]))
            )
        ]
        .sort_values(by=["id_tri", "id_seg"])
        .groupby("id_tri")
        .first()
        .reset_index()
    )
    gdf2 = (
        gdf_sjoin[
            (
                (gdf_sjoin["id_tri"].isin(gdf_out["id_tri"]))
                & (~gdf_sjoin["id_edge"].isin(gdf_out["id_edge"]))
            )
        ]
        .sort_values(by=["id_tri", "id_seg"])
        .groupby("id_tri")
        .last()
        .reset_index()
    )
    gdf1.set_crs(gdf_sjoin.crs, inplace=True)
    gdf2.set_crs(gdf_sjoin.crs, inplace=True)
    gdf_ext = gdf1.intersection(gdf2)  # third vertex
    p1 = gdf_out.intersection(gdf1, align=False)
    p2 = gdf_out.intersection(gdf2, align=False)
    pnew1 = gdf_out["geometry"].apply(
        lambda p: normalize(
            LineString(
                [
                    np.array(p.coords.xy).T[0],
                    np.array(p.coords.xy).T[0]
                    + 0.5 * (np.array(p.coords.xy).T[1] - np.array(p.coords.xy).T[0]),
                ]
            )
        )
    )
    pnew2 = gdf_out["geometry"].apply(
        lambda p: normalize(
            LineString(
                [
                    np.array(p.coords.xy).T[1],
                    np.array(p.coords.xy).T[0]
                    + 0.5 * (np.array(p.coords.xy).T[1] - np.array(p.coords.xy).T[0]),
                ]
            )
        )
    )
    pcoords_new = np.stack(
        gdf_out["geometry"]
        .apply(
            lambda p: np.array(p.coords.xy).T[0]
            + 0.5 * (np.array(p.coords.xy).T[1] - np.array(p.coords.xy).T[0])
        )
        .values
    )
    pcoords_old = gdf_ext.get_coordinates().values
    gdf_new = gpd.GeoDataFrame(
        geometry=[LineString((old, new)) for old, new in zip(pcoords_old, pcoords_new)],
        crs=crs,
    )
    g1 = gpd.GeoDataFrame(geometry=pnew1, crs=crs)
    g2 = gpd.GeoDataFrame(geometry=pnew2, crs=crs)
    gdf_tmp = pd.concat(
        [
            g1,
            g2,
            gdf_new,
            gdf_keep[["geometry"]],
            gdf1[["geometry"]],
            gdf2[["geometry"]],
        ]
    )
    gdf_fin = gpd.GeoDataFrame(
        geometry=gdf_tmp["geometry"].drop_duplicates().polygonize(), crs=crs
    )
    return gdf_fin


def split_max_length(gdf, max_length):
    gdf_start = gdf.copy()
    crs = gdf_start.crs
    gdf_s = get_edges(gdf_start)
    gdf_out = find_set(gdf_s, max_length)
    keep = True
    len_old = len(gdf_start)
    count = 0
    keep = len(gdf_out)
    while keep:
        gdf_f = get_new_geom(gdf_s, gdf_out)
        gdf_s = get_edges(gdf_f)
        gdf_out = find_set(gdf_s, max_length)
        keep = len(gdf_out)
        len_old = len(gdf_f)
        count += 1
        # print(count, keep)
    return gdf_f


def get_angle(gdf, i):
    # Not really numerically stable due to intersection
    gdf_edges = gdf.copy().sort_values(by=["id_tri", "id_seg"]).reset_index()
    va = (
        gdf_edges[gdf_edges["id_seg"] == 2]["geometry"]
        .intersection(gdf_edges[gdf_edges["id_seg"] == 3]["geometry"], align=False)
        .get_coordinates()
        .values
    )
    vb = (
        gdf_edges[gdf_edges["id_seg"] == 1]["geometry"]
        .intersection(gdf_edges[gdf_edges["id_seg"] == 3]["geometry"], align=False)
        .get_coordinates()
        .values
    )
    vc = (
        gdf_edges[gdf_edges["id_seg"] == 1]["geometry"]
        .intersection(gdf_edges[gdf_edges["id_seg"] == 2]["geometry"], align=False)
        .get_coordinates()
        .values
    )
    if i == 1:
        v1 = vb - va
        v2 = vc - va
    elif i == 2:
        v1 = va - vb
        v2 = vc - vb
    elif i == 3:
        v1 = va - vc
        v2 = vb - vc
    v1 /= np.sqrt(np.array([[elem @ elem, elem @ elem] for elem in v1]))
    v2 /= np.sqrt(np.array([[elem @ elem, elem @ elem] for elem in v2]))
    return [180.0 / np.pi * np.arccos(a @ b) for a, b in zip(v1, v2)]


def get_circumcenters(gdf):
    gdf_edges = gdf.copy().sort_values(by=["id_tri", "id_seg"]).reset_index()
    v0 = (
        gdf_edges[gdf_edges["id_seg"] == 2]["geometry"]
        .intersection(gdf_edges[gdf_edges["id_seg"] == 3]["geometry"], align=False)
        .get_coordinates()
        .values
    )
    v1 = (
        gdf_edges[gdf_edges["id_seg"] == 1]["geometry"]
        .intersection(gdf_edges[gdf_edges["id_seg"] == 3]["geometry"], align=False)
        .get_coordinates()
        .values
    )
    v2 = (
        gdf_edges[gdf_edges["id_seg"] == 1]["geometry"]
        .intersection(gdf_edges[gdf_edges["id_seg"] == 2]["geometry"], align=False)
        .get_coordinates()
        .values
    )
    b = v1 - v0
    c = v2 - v0
    b2 = b.T[0] ** 2 + b.T[1] ** 2
    c2 = c.T[0] ** 2 + c.T[1] ** 2
    d2 = 2 * (b.T[0] * c.T[1] - b.T[1] * c.T[0])
    ux = (c.T[1] * b2 - b.T[1] * c2) / d2
    uy = (b.T[0] * c2 - c.T[0] * b2) / d2
    cv = (np.array([ux, uy]).T + v0).T
    gdf_cc = gpd.GeoDataFrame(
        {"id_tri": gdf_edges[gdf_edges["id_seg"] == 1]["id_tri"]},
        geometry=gpd.points_from_xy(cv[0], cv[1]),
        crs=gdf_edges.crs,
    )
    return gdf_cc


def get_bad_angles(gdf, min_angle, max_area: float = None):
    gdf_edges = gdf.copy().sort_values(by="id_tri")
    gdf_tmp = gdf_edges.dissolve("id_tri").reset_index().sort_values(by="id_tri")
    gdf_new = gpd.GeoDataFrame(
        {"id_tri": gdf_tmp["id_tri"]},
        geometry=gdf_tmp["geometry"].polygonize(),
        crs=gdf_tmp.crs,
    ).sort_values(by="id_tri")
    gdf_new["a0"] = get_angle(gdf_edges, 1)
    gdf_new["a1"] = get_angle(gdf_edges, 2)
    gdf_new["a2"] = get_angle(gdf_edges, 3)
    gdf_new["amin"] = np.min(
        [np.abs(gdf_new["a0"]), np.abs(gdf_new["a1"]), np.abs(gdf_new["a2"])], axis=0
    )
    s0 = gdf_new["amin"] < min_angle
    if max_area is None:
        return s0
    else:
        geom_tmp = [
            gdf_tmp[gdf_tmp["id_tri"] == elem].polygonize()[0]
            for elem in gdf_tmp["id_tri"]
        ]
        area = gpd.GeoDataFrame(geometry=geom_tmp, crs=gdf_tmp.crs).area.values
        s1 = area > max_area
        return np.logical_or(s0, s1)


def find_set_new(gdf_sjoin):
    if np.sum(gdf_sjoin["x"] > 0):
        pool = gdf_sjoin[gdf_sjoin["x"] > 0].sort_values(by="length")
        selected_edges = [pool.head(1)["id_edge"].values[0]]
        selected_triangles = gdf_sjoin[gdf_sjoin["id_edge"].isin(selected_edges)][
            "id_tri"
        ].to_list()
        forbidden_edges = gdf_sjoin[gdf_sjoin["id_tri"].isin(selected_triangles)][
            "id_edge"
        ].to_list()
        for k, elem in pool.iterrows():
            if elem["id_edge"] not in forbidden_edges:
                selected_edges += [elem["id_edge"]]
                selected_triangles = gdf_sjoin[
                    gdf_sjoin["id_edge"].isin(selected_edges)
                ]["id_tri"].to_list()
                forbidden_edges = gdf_sjoin[
                    gdf_sjoin["id_tri"].isin(selected_triangles)
                ]["id_edge"].to_list()
        df_out = gdf_sjoin[gdf_sjoin["id_edge"].isin(selected_edges)]
        return df_out.sort_values(by=["id_tri", "id_seg"])
    else:
        return gdf_sjoin[gdf_sjoin["x"] > 0]


def get_edges_to_split(gdf, mask):
    # TODO: assicurati che ci sia un solo lato per ciascun triangolo
    gdf_edges = gdf.copy().sort_values(by="id_tri")
    # crs = gdf_edges.crs
    cv = get_circumcenters(gdf_edges)
    p3 = gdf_edges[gdf_edges["id_seg"] == 1]["geometry"].intersection(
        gdf_edges[gdf_edges["id_seg"] == 2]["geometry"], align=False
    )
    p2 = gdf_edges[gdf_edges["id_seg"] == 1]["geometry"].intersection(
        gdf_edges[gdf_edges["id_seg"] == 3]["geometry"], align=False
    )
    p1 = gdf_edges[gdf_edges["id_seg"] == 2]["geometry"].intersection(
        gdf_edges[gdf_edges["id_seg"] == 3]["geometry"], align=False
    )
    v = gdf_edges[gdf_edges["id_seg"] == 1]["id_tri"]
    # g1 = gpd.GeoDataFrame({'id_tri': v, 'p': [1] * len(v)}, geometry=p1, crs=crs)
    # g2 = gpd.GeoDataFrame({'id_tri': v, 'p': [2] * len(v)}, geometry=p2, crs=crs)
    # g3 = gpd.GeoDataFrame({'id_tri': v, 'p': [3] * len(v)}, geometry=p3, crs=crs)
    # cv['p'] = [0]*len(v)
    x0a = gpd.GeoSeries(
        [
            LineString([a, b])
            for a, b in zip(
                cv["geometry"].get_coordinates().values, p1.get_coordinates().values
            )
        ]
    )
    x1a = gpd.GeoSeries(
        [
            LineString([a, b])
            for a, b in zip(p2.get_coordinates().values, p3.get_coordinates().values)
        ]
    )

    x0b = gpd.GeoSeries(
        [
            LineString([a, b])
            for a, b in zip(
                cv["geometry"].get_coordinates().values, p2.get_coordinates().values
            )
        ]
    )
    x1b = gpd.GeoSeries(
        [
            LineString([a, b])
            for a, b in zip(p1.get_coordinates().values, p3.get_coordinates().values)
        ]
    )

    x0c = gpd.GeoSeries(
        [
            LineString([a, b])
            for a, b in zip(
                cv["geometry"].get_coordinates().values, p3.get_coordinates().values
            )
        ]
    )
    x1c = gpd.GeoSeries(
        [
            LineString([a, b])
            for a, b in zip(p2.get_coordinates().values, p1.get_coordinates().values)
        ]
    )
    xa = x0a.intersects(x1a)
    xb = x0b.intersects(x1b)
    xc = x0c.intersects(x1c)
    gdf1 = gdf_edges[gdf_edges["id_seg"] == 1].copy()
    gdf1["bad"] = mask.astype(int).values
    gdf1["split"] = xa.astype(int).values

    gdf2 = gdf_edges[gdf_edges["id_seg"] == 2].copy()
    gdf2["bad"] = mask.astype(int).values
    gdf2["split"] = xb.astype(int).values

    gdf3 = gdf_edges[gdf_edges["id_seg"] == 3].copy()
    gdf3["bad"] = mask.astype(int).values
    gdf3["split"] = xc.astype(int).values

    gdf1["x"] = gdf1["split"] * gdf1["bad"]
    gdf2["x"] = gdf2["split"] * gdf2["bad"]
    gdf3["x"] = gdf3["split"] * gdf3["bad"]
    return pd.concat([gdf1, gdf2, gdf3])


def split_initial(gdf, min_angle):
    gdf_start = gdf.copy()
    crs = gdf_start.crs
    gdf_s = get_edges(gdf_start)
    mask = get_bad_angles(gdf_s, min_angle)
    keep = np.sum(mask)

    len_old = len(gdf_start)
    count = 0
    while keep:
        gdf_out_tmp = get_edges_to_split(gdf_s, mask)
        gdf_out = gdf_out_tmp[gdf_out_tmp["x"] > 0]
        gdf_f = get_new_geom(gdf_s, gdf_out)
        gdf_s = get_edges(gdf_f)
        mask = get_bad_angles(gdf_s, min_angle)
        keep = np.sum(mask)
        len_old = len(gdf_f)
        count += 1
        # print(count, keep)
        return gdf_f


def insert_cc(gdf, area_max, mask_start):
    gdf = gdf.copy()
    crs = gdf.crs
    gdf_cc = get_circumcenters(gdf).reset_index()
    gdf_tmp = gdf.dissolve(by="id_tri").reset_index().sort_values(by="id_tri")
    geom_new = gpd.GeoDataFrame(
        geometry=[
            gdf_tmp[gdf_tmp["id_tri"] == elem].polygonize().values[0]
            for elem in gdf_tmp["id_tri"]
        ],
        crs=crs,
    )

    m0 = gdf_cc.within(geom_new).values
    m1 = (geom_new.area > area_max).values
    m2 = np.logical_or(m1, mask_start)
    mask = np.logical_and(m0, m2)
    gdf_to_keep = geom_new[~mask]
    gdf_to_drop = geom_new[mask]
    gdf_pt = gdf_cc[mask]["geometry"].apply(lambda p: np.array(p.coords.xy))
    geom_out = gdf_to_keep["geometry"].to_list()
    if np.sum(mask):
        pval = gdf_cc[mask]["geometry"].apply(lambda p: np.array(p.coords.xy))
        for k in range(len(gdf_to_drop)):
            p0 = gdf_pt.iloc[k].reshape(-1)
            vl = np.array(gdf_to_drop.iloc[k]["geometry"].boundary.coords.xy).T[:-1]
            geom = [
                normalize(Polygon([vl[0], vl[1], p0, vl[0]])),
                normalize(Polygon([vl[1], vl[2], p0, vl[1]])),
                normalize(Polygon([vl[2], vl[0], p0, vl[2]])),
            ]
            geom_out += geom
            # print(geom)
        gdf_out = gpd.GeoDataFrame(geometry=geom_out, crs=crs)
        gdf_out["id_tri"] = np.arange(len(gdf_out)).astype(int)
        return gdf_out, pval
    else:
        return geom_new, 0


def get_edges_to_swap(gdf_edges):
    v1 = get_angle(gdf_edges, 1)
    v2 = get_angle(gdf_edges, 2)
    v3 = get_angle(gdf_edges, 3)
    g1 = gdf_edges[gdf_edges["id_seg"] == 1].copy()
    g2 = gdf_edges[gdf_edges["id_seg"] == 2].copy()
    g3 = gdf_edges[gdf_edges["id_seg"] == 3].copy()
    g1["angle"] = v1
    g2["angle"] = v2
    g3["angle"] = v3

    gf = pd.concat([g1, g2, g3])
    gfa = gf.groupby("id_edge")["angle"].sum().reset_index()
    gfa["to_swap"] = gfa["angle"] > 180
    return gfa[gfa["to_swap"]]["id_edge"].to_list()


def swap_edges(gdf_int, edge_list):
    # assegna nuovo id triangolo a tutti gli edge che rimangono
    #
    gdf = gdf_int.copy()
    crs = gdf.crs
    gdf_rel = gdf[
        gdf["id_edge"].isin(edge_list)
    ].copy()  # rimuovi e sostituisci con nuovi vertici
    gdf_rel_full = gdf[gdf["id_tri"].isin(gdf_rel["id_tri"])].copy()
    gdf_keep = gdf[~gdf["id_tri"].isin(gdf_rel["id_tri"])].copy()  # mantieni
    gdf_tmp = gdf[gdf["id_edge"].isin(edge_list)][["id_tri", "id_edge"]]
    gdf_union = (
        gdf[gdf["id_tri"].isin(gdf[gdf["id_edge"].isin(edge_list)]["id_tri"])]
        .dissolve("id_tri")
        .reset_index()[["id_tri", "geometry"]]
    )
    gdf_merge = (
        pd.merge(gdf_union, gdf_tmp, on="id_tri").dissolve("id_edge").reset_index()
    )
    out = [gpd.GeoDataFrame(geometry=gdf_keep.polygonize(), crs=crs)]
    for edge in edge_list:
        vall = np.array(
            gdf_merge[gdf_merge["id_edge"] == edge]
            .polygonize()
            .union_all()
            .boundary.coords.xy
        ).T[:-1]
        vold = np.array(
            gdf_rel[gdf_rel["id_edge"] == edge][["geometry"]]
            .drop_duplicates()["geometry"]
            .iloc[0]
            .coords.xy
        )
        vnew = np.array([elem for elem in vall if elem not in vold])
        coords_tri_1 = Polygon(
            np.concat([np.array([vold.T[0]]), vnew, np.array([vold.T[0]])])
        )
        coords_tri_2 = Polygon(
            np.concat([np.array([vold.T[1]]), vnew, np.array([vold.T[1]])])
        )
        gdf_new = gpd.GeoDataFrame(geometry=[coords_tri_1, coords_tri_2], crs=crs)
        out.append(gdf_new)
    return pd.concat(out)


def refine(gdf, min_angle, max_area: float = None):
    gdf_start = gdf.copy()
    gdf_edges = get_edges(gdf_start).reset_index().sort_values(by="id_tri")
    mask = get_bad_angles(gdf_edges, min_angle)
    print(np.sum(mask))
    flag = np.sum(mask).astype(int)
    flag += (np.max(gdf_start.area) > max_area).astype(int)
    flag = bool(flag)
    niter = 0
    while flag and niter < 40:
        mask = get_bad_angles(gdf_edges, min_angle, max_area)
        gdf_edges_new = get_edges_to_split(gdf_edges, mask)
        gdf_s = find_set_new(gdf_edges_new)
        if len(gdf_s):
            gdf_out = get_new_geom(gdf_edges_new, gdf_s)
            gdf_edges = (
                get_edges(gdf_out).reset_index().sort_values(by="id_tri")
            )  # swap after this and recreate edges
            edges_to_swap = get_edges_to_swap(gdf_edges)
            gdf_swapped_poly = swap_edges(gdf_edges, edges_to_swap)
            gdf_edges = (
                get_edges(gdf_swapped_poly).reset_index().sort_values(by="id_tri")
            )
            try:
                mask = get_bad_angles(gdf_edges, min_angle, max_area)
            except ValueError as err:
                print(err)
                return gdf_edges
            print(np.sum(mask))
            # flag = np.sum(mask).astype(bool)
            flag = np.sum(mask).astype(int)
            flag += (np.max(gdf_start.area) > max_area).astype(int)
            flag = bool(flag)
            if not flag:
                print("DONE")
            niter += 1
            # gdf_edges_new = get_edges_to_split(gdf_edges, mask)
        else:
            print(f"ELSE")
            mask = get_bad_angles(gdf_edges_new, min_angle)
            flag = np.sum(mask).astype(int)
            flag += (np.max(gdf_start.area) > max_area).astype(int)
            flag = bool(flag)
            if not flag:
                print("DONE")
                cols = gdf_edges.columns
                gdf_edges = gdf_edges_new  # [cols]
            else:
                gdf_new_p, x = insert_cc(gdf_edges_new, max_area, mask)
                gdf_edges = (
                    get_edges(gdf_new_p).reset_index().sort_values(by="id_tri")
                )  # swap after this and recreate edges
                edges_to_swap = get_edges_to_swap(gdf_edges)
                gdf_swapped_poly = swap_edges(gdf_edges, edges_to_swap)
                gdf_edges = (
                    get_edges(gdf_swapped_poly).reset_index().sort_values(by="id_tri")
                )  # swap after this and recreate edges
                mask = get_bad_angles(gdf_edges, min_angle, max_area)
                gdf_edges = get_edges_to_split(gdf_edges, mask)
            niter += 1
    return gdf_edges


"""
Idea di base:
- cerca tutti triangoli indesiderati (angolo troppo piccolo, area troppo grande etc)
- cerca circocentri di questi triangoli e crea 3 nuovi triangoli (sostituisci ciascun vertice con circocentro)
- se un segmento dei nuovi triangoli interseca un segmento del triangolo originale, splitta in due
"""
