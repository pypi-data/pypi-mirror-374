import logging
import numpy as np
import geopandas as gpd
from shapely import Polygon

from delaunay_refine.utils import (
    calculate_triangle_area,
    calculate_triangle_smaller_angle,
    get_triangle_circumcenter,
    point_inside_triangle,
    segments_are_intercepting,
)


class Triangulation:
    """
    This method contains all the informations about the triangulation,
    as well as the method to perform it
    """
    def __init__(self):
        self.x = np.array([])  # List of coordinates
        self.n_initial = 0  # We can't touch the initial points.
        self.edges = None
        self.triangles = (
            None  # triplets of edges or triplets of vertices? For now edges
        )
        self.is_center = None
        # (vertices from edges are easier to recover)

        #  Triangulation parameters
        self.min_angle = None
        self.max_area = None
        self.min_area = None

    def set_points(self, points: np.array) -> None:
        """
        Assigns the coordinates of the initial triangulation
        :param points: np.array containing the coordinates pairs of each point
        :return: None
        """
        self.x = points

    def set_edges(self, edges_list: list) -> None:
        """
        Assigns the pairs of points of each edge.
        Points are represented as their index 0,1,...,len(self.x)-1
        :param edges_list:
        :return: None
        """
        self.edges = edges_list
        self.is_center = [0] * len(self.edges)

    def set_min_angle(self, min_angle: float) -> None:
        """
        Sets the minimum desired angle which should be returned in the refinement
        :param min_angle: the minimum angle, expressed in degrees
        :return: None
        """
        self.min_angle = min_angle

    def set_max_area(self, max_area: float) -> None:
        """
        Sets the maximum desired area which should be returned in the refinement
        :param max_area: the maximum area, expressed in the same units of the coordinates (squared)
        :return: None
        """
        self.max_area = max_area

    def _set_triangles_from_edges(self, triangle_edges) -> None:
        self.triangles = triangle_edges

    def get_triangle_coordinates(self) -> np.array:
        """
        Returns the coordinates of the triangulation points
        :return: np.array
        """
        #  We only need two edges for each triangle
        pts_id = [
            sorted(list(set(self.edges[elem[0]]).union(set(self.edges[elem[1]]))))
            for elem in self.triangles
        ]
        return np.stack([[self.x[pt] for pt in elem] for elem in pts_id])

    def get_edge(self, i: int):
        """
        Returns the i-th edge
        :param i: int
        :return: np.array
        """
        return np.stack((self.x[self.edges[i][0]], self.x[self.edges[i][1]]))

    def to_gdf(self, crs=None):
        """
        Consverts the triangulation into a geodataframe, where each trianle
        is converted into a shapely Polygon
        :param crs: Optional crs for the resulting geodataframe
        :return: geopandas.GeoDataFrame
        """
        out = []
        for tri in self.triangles:
            pts_list = list(
                set(list(np.array([self.edges[elem] for elem in tri]).reshape(-1)))
            )
            geom = Polygon([self.x[elem] for elem in pts_list])
            out += [geom]
        res = gpd.GeoDataFrame(geometry=out, crs=crs)
        return res

    def _get_bad_triangles(self):
        #  The first step is to determine which are the bad triangles
        #  (angle too small or area too large)
        coords = self.get_triangle_coordinates()
        area = np.array([calculate_triangle_area(elem) for elem in coords])
        min_angle = np.array(
            [calculate_triangle_smaller_angle(elem) for elem in coords]
        )
        out = np.logical_or(area > self.max_area, min_angle < self.min_angle)
        if self.min_area is None:
            return out
        return np.logical_and(out, area > self.min_area)

    def _get_circumcenters(self):
        #  For each bad triangle we must determine the circumcenter
        return np.array(
            [
                get_triangle_circumcenter(elem)
                for elem in self.get_triangle_coordinates()
            ]
        )

    @staticmethod
    def _circumcenter_is_inside(cc_arr: np.array, pts: np.array) -> np.array:
        #  The second step is to determine if the circumcenter is inside the triangle or not
        return np.array(
            [point_inside_triangle(p, pts[i]) for i, p in enumerate(cc_arr)]
        )

    def _count_edges_occurrences(self):
        #  If an edge appears only once, it is external, otherwise it is internal
        edges, occ = np.unique(np.array(self.triangles).reshape(-1), return_counts=True)
        return dict(zip(edges, occ))

    def _create_new_vertex_from_split(self, edge_num):

        coords = np.mean([self.x[pt] for pt in self.edges[edge_num]], axis=0)
        return coords

    def _add_new_vertex(self, coords):
        # print(np.shape(self.x))
        # print(coords)
        try:
            self.x = np.concat([self.x, [coords]])
            return len(self.x) - 1
        except ValueError as err:
            print(f"Error {err}")
            print(np.shape(self.x))
            print(np.shape(coords))
            raise err

    def _created_split_edge(self, edge_index, vertex_index):
        vert = self.edges[edge_index]
        return [int(vert[0]), vertex_index], [int(vert[1]), vertex_index]

    def _edge_is_encroached(self, cc_arr: np.array, id_tri: int):
        tri_pts = np.unique(
            np.array([self.edges[elem] for elem in np.array(self.triangles)[id_tri]])
        )
        for id_edge in range(3):
            edge_pts = self.edges[np.array(self.triangles)[id_tri][id_edge]]
            pt0 = self.x[list(set(tri_pts).difference(set(edge_pts)))[0]]
            pt1 = self.x[edge_pts[0]]
            pt2 = self.x[edge_pts[1]]
            v = segments_are_intercepting(cc_arr[id_tri], pt0, pt1, pt2)

            if v:
                edge_num = int(np.array(self.triangles)[id_tri][id_edge])

                return {
                    "edge": edge_num,
                    "opposite_point": int(
                        list(set(tri_pts).difference(set(edge_pts)))[0]
                    ),
                }
        return {"edge": None, "opposite_point": None}

    def _swap_edge(self, edge):
        tri = [elem for elem in self.triangles if edge in elem]
        if len(tri) == 2:
            tri_other = [elem for elem in self.triangles if edge not in elem]
            tri0 = tri[0]
            tri1 = tri[1]
            tri0_other = [elem for elem in tri0 if elem != edge]
            tri1_other = [elem for elem in tri1 if elem != edge]

            if (
                set(self.edges[tri0_other[0]]).intersection(
                    set(self.edges[tri1_other[0]])
                )
                != set()
            ):
                out1 = tuple(sorted([tri0_other[0], tri1_other[0], edge]))
                out2 = tuple(sorted([tri0_other[1], tri1_other[1], edge]))
            else:
                out1 = tuple(sorted([tri0_other[0], tri1_other[1], edge]))
                out2 = tuple(sorted([tri0_other[1], tri1_other[0], edge]))
            v0 = np.array([self.edges[elem] for elem in tri0_other]).reshape(-1)
            v1 = np.array([self.edges[elem] for elem in tri1_other]).reshape(-1)

            x0, c0 = np.unique(v0, return_counts=True)
            z0 = int(x0[np.argmax(c0)])

            x1, c1 = np.unique(v1, return_counts=True)
            z1 = int(x1[np.argmax(c1)])

            output = sorted([z0, z1]), tri_other + [out1, out2]

            return output
            #  Given an edge, if the sum of
            #  the angles opposite to the edge is greater than pi,
            #  We must swap it
            #  (create two new triangles from the two triangles containing the vertex)
        return []

    def _create_missing_edge_from_split(self, tri,
                                        edge_num,
                                        new_vertex_index):
        res_edges = [self.edges[edge] for edge in tri if edge != edge_num]
        logging.debug(
            f"""Building last edge in {tri} from intersection
             of edges {res_edges} and vertex {new_vertex_index}"""
        )
        intersection_pt = list(set(res_edges[0]).intersection(set(res_edges[1])))[0]
        new_edge = [int(intersection_pt), new_vertex_index]
        logging.debug("New edge has boundary points %s", new_edge)
        return new_edge

    def _add_edge(self, edge_coords, is_center: int = 0):
        logging.debug("Old len: %s", len(self.edges))
        self.edges = np.concat([self.edges, [edge_coords]])
        self.is_center += [is_center]
        logging.debug("New len: %s", len(self.edges))
        return len(self.edges) - 1

    def _split_triangle(
        self, tri, edge_num, new_edge_index, p_index, q_index
    ):
        logging.debug(tri)
        logging.debug(f" Splitting edge {edge_num} in {tri}")
        res_edges = [edge for edge in tri if edge != edge_num]
        # 1. isolate edges different from edge_num
        # 2. for each edge
        tri_out = []
        for edge in res_edges:
            logging.debug("Building new triangle containing %s", edge)
            logging.debug(self.edges[edge])
            logging.debug(self.edges[p_index])
            logging.debug(self.edges[q_index])
            intersects_p = len(
                list(set(self.edges[edge]).intersection(self.edges[p_index]))
            )
            intersects_q = len(
                list(set(self.edges[edge]).intersection(self.edges[q_index]))
            )
            if intersects_p:
                tri_out += [tuple(sorted((edge, p_index, new_edge_index)))]
            elif intersects_q:
                tri_out += [tuple(sorted((edge, q_index, new_edge_index)))]
            else:
                raise ValueError(f"No common point found in {tri}")
        return tri_out
        # logging.debug(np.unique(tri_pts, return_counts=True))

    def _add_triangle(self, tri):
        logging.debug("Old tri len %s", len(self.triangles))
        self.triangles += [tri]
        logging.debug("New tri len %s", len(self.triangles))

    def _edge_must_be_swapped(self, edge_num):
        triangles_edges = [tri for tri in self.triangles if edge_num in tri]
        if len(triangles_edges) == 2:
            # print(triangles_edges)
            v1 = [edge for edge in triangles_edges[0] if edge != edge_num]
            v2 = [edge for edge in triangles_edges[1] if edge != edge_num]

            x11 = self.edges[v1[0]]
            x12 = self.edges[v1[1]]
            comm_pt_1 = set(x11).intersection(set(x12))
            u11 = list(set(x11).difference(comm_pt_1))[0]
            u12 = list(set(x12).difference(comm_pt_1))[0]
            y11 = self.x[u11] - self.x[list(comm_pt_1)[0]]
            y12 = self.x[u12] - self.x[list(comm_pt_1)[0]]
            y11 /= np.sqrt(np.sum(y11**2))
            y12 /= np.sqrt(np.sum(y12**2))
            angle1 = np.arccos(np.dot(y11, y12))

            x21 = self.edges[v2[0]]
            x22 = self.edges[v2[1]]
            comm_pt_2 = set(x21).intersection(set(x22))
            u21 = list(set(x21).difference(comm_pt_2))[0]
            u22 = list(set(x22).difference(comm_pt_2))[0]
            y21 = self.x[u21] - self.x[list(comm_pt_2)[0]]
            y22 = self.x[u22] - self.x[list(comm_pt_2)[0]]
            y21 /= np.sqrt(np.sum(y21**2))
            y22 /= np.sqrt(np.sum(y22**2))
            angle2 = np.arccos(np.dot(y21, y22))
            return angle1 + angle2 > np.pi
        return False

    def _build_new_edges(self, triangles, nold):
        xnew = list(range(nold, len(self.x)))
        pts = [[self.edges[edge] for edge in tri] for tri in triangles]
        v0 = [int(list(set(pt[1]).intersection(set(pt[2])))[0]) for pt in pts]
        v1 = [int(list(set(pt[0]).intersection(set(pt[2])))[0]) for pt in pts]
        v2 = [int(list(set(pt[0]).intersection(set(pt[1])))[0]) for pt in pts]
        new_edges_0 = [[p, v] for p, v in zip(xnew, v0)]
        new_edges_1 = [[p, v] for p, v in zip(xnew, v1)]
        new_edges_2 = [[p, v] for p, v in zip(xnew, v2)]
        return np.concat([new_edges_0, new_edges_1, new_edges_2])

    def _build_new_triangles(self, triangles):
        mstart = len(self.edges)
        idx_0 = range(mstart, mstart + len(triangles))
        idx_1 = range(mstart + len(triangles), mstart + 2 * len(triangles))
        idx_2 = range(mstart + 2 * len(triangles), mstart + 3 * len(triangles))
        tri0 = [(x[0], y, z) for x, y, z in zip(triangles, idx_1, idx_2)]
        tri1 = [(x[1], y, z) for x, y, z in zip(triangles, idx_0, idx_2)]
        tri2 = [(x[2], y, z) for x, y, z in zip(triangles, idx_0, idx_1)]
        return np.concat([tri0, tri1, tri2])

    def _reorder_triangles(self, by_area: bool = False):
        if by_area:
            crd = self.get_triangle_coordinates()
            tri_ord = np.argsort([calculate_triangle_area(elem) for elem in crd])[::-1]
        else:
            crd = self.get_triangle_coordinates()
            cc = self._get_circumcenters()
            tri_ord = np.argsort(
                [np.sum((elem[0] - cc[k]) ** 2) for k, elem in enumerate(crd)]
            )[::-1]
        tri_new = [self.triangles[k] for k in tri_ord]
        return tri_new

    def _create_new_tri(self, tri_to_split, nold):
        return [
            tuple(sorted((tri_to_split[0], nold + 1, nold + 2))),
            tuple(sorted((tri_to_split[1], nold, nold + 2))),
            tuple(sorted((tri_to_split[2], nold, nold + 1))),
        ]

    def _swap_edges(self):
        cont = True
        while cont:
            for edge in range(len(self.edges) + 1):
                if edge == len(self.edges):
                    cont = False
                else:
                    if self._edge_must_be_swapped(edge):
                        # print(f"Swap edge")
                        edge_out, triangles_out = self._swap_edge(edge)
                        self.edges[edge] = edge_out
                        self.is_center[edge] = 0
                        self.triangles = triangles_out
                        break

    def refine(
        self,
        min_angle: float,
        max_area: float,
        max_iter: int = 1000,
        min_area: float | None = None,
    ):
        """
        Performs Delaunay refinement according to Ruppert's algorithm
        :param min_angle: float, smallest desired angle.
        :param max_area: float, largest desired area
        :param max_iter: int, maximum number of iterations
        :param min_area: float, minimum area, below this value there won't be splitting
        :return: None
        """
        self.set_min_angle(min_angle)
        self.set_max_area(max_area)
        self.min_area = min_area
        for _ in range(max_iter):
            self.triangles = self._reorder_triangles()
            bad_tri = self._get_bad_triangles()
            if not np.any(bad_tri):
                break
            coords = self.get_triangle_coordinates()
            cc = self._get_circumcenters()

            is_inside = self._circumcenter_is_inside(cc_arr=cc, pts=coords)

            if np.any(np.invert(is_inside[bad_tri])):
                self._split_edge_of_encroached_triangle(bad_tri, cc, is_inside)
            else:
                self._insert_cc(bad_tri)
                # break
            self._swap_edges()


    def _insert_cc(self, bad_tri):
        tri_to_split = [t for k, t in enumerate(self.triangles) if bad_tri[k]][0]

        for edge in tri_to_split:
            self.is_center[edge] = 0

        tri_old = [t for k, t in enumerate(self.triangles) if t != tri_to_split]

        vall = [self.edges[elem] for elem in tri_to_split]
        nnew = len(self.x)
        cc = self._get_circumcenters()
        cc_coords = np.array(cc)[bad_tri][0]

        v0 = int(list(set(vall[1]).intersection(set(vall[2])))[0])
        v1 = int(list(set(vall[0]).intersection(set(vall[2])))[0])
        v2 = int(list(set(vall[0]).intersection(set(vall[1])))[0])

        new_edges = [[v0, nnew], [v1, nnew], [v2, nnew]]

        nedge_old = len(self.edges)

        new_tris = [
            (tri_to_split[0], nedge_old + 1, nedge_old + 2),
            (tri_to_split[1], nedge_old + 0, nedge_old + 2),
            (tri_to_split[2], nedge_old + 0, nedge_old + 1),
        ]

        self.x = np.concat([self.x, [cc_coords]])

        for edge in new_edges:
            self._add_edge(edge, is_center=1)
        # self.edges = np.concat([self.edges, new_edges])

        self.triangles = tri_old + new_tris

        self.triangles = self._reorder_triangles()

        return tri_to_split

    def _split_edge_of_encroached_triangle(self, bad_tri, cc, is_inside):
        id_tri = np.argwhere(np.array(np.logical_and(bad_tri, np.invert(is_inside))))[
            0
        ][0]
        logging.debug("SPLIT")
        dict_data = self._edge_is_encroached(cc, id_tri)
        logging.debug(dict_data)
        edge_num = dict_data["edge"]
        if edge_num is not None:
            self.is_center[edge_num] = 0
            logging.debug("splitting edge %s", edge_num)
            new_vertex_coords = self._create_new_vertex_from_split(edge_num)
            logging.debug("Creating new vertex with coordinates %s", new_vertex_coords)
            new_vertex_index = self._add_new_vertex(new_vertex_coords)
            logging.debug("New vertex added with index %s", new_vertex_index)
            logging.debug("Creating new edges by splitting %s", edge_num)
            p, q = self._created_split_edge(edge_num, new_vertex_index)
            p_index = self._add_edge(p, is_center=0)
            logging.debug("p has index %s", p_index)
            q_index = self._add_edge(q, is_center=0)
            logging.debug("q has index %s", q_index)
            logging.debug(f"Edges {p} and {q} created")
            triangles_to_split = [tri for tri in self.triangles if edge_num in tri]
            logging.debug("Edge found in triangles %s", triangles_to_split)
            for tri in triangles_to_split:
                new_edge = self._create_missing_edge_from_split(
                    tri, edge_num, new_vertex_index
                )
                new_edge_index = self._add_edge(new_edge, is_center=0)
                new_tirangles = self._split_triangle(
                    tri, edge_num, new_edge_index, p_index, q_index
                )
                logging.debug("Created %s", new_tirangles)
                for new_tri in new_tirangles:
                    self._add_triangle(new_tri)
            self.triangles = [
                tri for tri in self.triangles if tri not in triangles_to_split
            ]


    def _dissolve_centers(self, candidates, p, bad_tri, cc, is_inside):
        id_tri = np.argwhere(np.array(np.logical_and(bad_tri, np.invert(is_inside))))[
            0
        ][0]
        print(self.triangles[id_tri])
        print(cc[id_tri])
        dst = np.sum((self.x[p[0]] - self.x[p[1]]) ** 2)
        print(dst)
        is_closer = [
            elem
            for elem in np.array(candidates).reshape(-1)
            if np.sum((self.x[self.edges[elem]] - cc[id_tri]) ** 2) < dst
        ]
        print(is_closer)
        return is_closer


def _build_pairs(x):
    xn = sorted([int(elem) for elem in x])
    return [[xn[0], xn[1]], [xn[0], xn[2]], [xn[1], xn[2]]]


def triangulation_from_gdf(gdf: gpd.GeoDataFrame):
    """
    Builds a Triangulation object from a geopandas GeoDataFrame
    :param gdf:
    :return: Triangulation
    """
    crs = gdf.crs
    gdf_bds = gdf.boundary.reset_index().drop(columns="index")
    pts = gdf.boundary.get_coordinates().drop_duplicates().values
    gdf_pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(pts.T[0], pts.T[1]), crs=crs)
    df_tmp = gdf_bds.sjoin(gdf_pts).reset_index()[["index", "index_right"]]
    pts_pairs = [
        _build_pairs(df_tmp[df_tmp["index"] == k].values.T[1])
        for k in df_tmp["index"].drop_duplicates()
    ]
    edges = np.unique(
        [elem[0] for elem in pts_pairs]
        + [elem[1] for elem in pts_pairs]
        + [elem[2] for elem in pts_pairs],
        axis=0,
    )
    v0 = [elem[0] for elem in pts_pairs]
    v1 = [elem[1] for elem in pts_pairs]
    v2 = [elem[2] for elem in pts_pairs]
    tmp = ["-".join([str(x) for x in elem]) for elem in edges]
    v0s = ["-".join([str(x) for x in elem]) for elem in v0]
    v1s = ["-".join([str(x) for x in elem]) for elem in v1]
    v2s = ["-".join([str(x) for x in elem]) for elem in v2]
    u0 = [tmp.index(elem) for elem in v0s]
    u1 = [tmp.index(elem) for elem in v1s]
    u2 = [tmp.index(elem) for elem in v2s]
    # return dict(points=pts, edges=edges, triangles=list(zip(u0, u1, u2)))
    tri = Triangulation()
    tri.set_points(pts)
    tri.set_edges(edges)
    tri._set_triangles_from_edges(list(zip(u0, u1, u2)))
    return tri
