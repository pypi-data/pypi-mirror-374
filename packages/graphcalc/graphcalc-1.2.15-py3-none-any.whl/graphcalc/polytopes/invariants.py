
from typing import Union, List
import networkx as nx
import graphcalc as gc
from graphcalc.core import SimpleGraph

__all__ = [
    'p_vector',
    'p_gons',
    'fullerene',
    'simple_graph',
    'polytope_graph',
    'simple_polytope_graph',
    'polytope_graph_with_p6_zero',
    'simple_polytope_graph_with_p6_zero',
    'polytope_graph_with_p6_greater_than_zero',
    'simple_polytope_graph_with_p6_greater_than_zero',
]

def p_vector(G_nx: Union[nx.Graph, SimpleGraph]) -> List[int]:
    r"""
    Compute the p-vector of a planar graph.

    The p-vector of a graph is a list where the i-th entry represents the count of i-sided faces
    (e.g., triangles, quadrilaterals, pentagons) in a planar embedding of the graph. The function
    assumes the input graph is planar and connected.

    Parameters
    ----------
    G_nx : networkx.Graph or graphcalc.SimpleGraph
        A planar graph for which the p-vector is computed.

    Returns
    -------
    list of int
        The p-vector, where the value at index `k-3` corresponds to the number of k-sided faces in the graph.

    Notes
    -----
    - This function first checks the planarity of the input graph using NetworkX's `check_planarity`.
    - If the graph is not planar, a `ValueError` is raised.

    Examples
    --------
    Compute the p-vector of a simple planar graph:

    >>> import graphcalc as gc
    >>> G = gc.cycle_graph(6)  # Hexagon
    >>> gc.p_vector(G)
    [0, 0, 0, 1]

    Compute the p-vector of a graph with multiple face sizes:

    >>> G = gc.SimpleGraph()
    >>> G.add_edges_from([
    ...     (0, 1), (1, 2), (2, 3), (3, 0),  # Quadrilateral face
    ...     (0, 4), (4, 1),  # Two triangular faces
    ...     (1, 5), (5, 2)
    ... ])
    >>> gc.p_vector(G)
    [2, 1, 0, 1]
    """
    # Ensure the graph is labeled with consecutive integers
    G_nx = nx.convert_node_labels_to_integers(G_nx)
    graph = nx.to_numpy_array(G_nx, dtype=int)


    # Dictionary to store the count of faces by their number of sides
    num_i_sides = {}

    # Check if the graph is planar and obtain its planar embedding
    is_planar, embedding_nx = nx.check_planarity(G_nx)
    if not is_planar:
        raise ValueError("The input graph is not planar.")

    # Initialize vertex elements list
    vert_elms = list(range(1, len(graph[0]) + 1))

    # Initialize edge elements and relations
    edge_elms = []
    edge_dict = {}
    relations = []

    # Construct edges and their relationships
    for vert in vert_elms:
        vert_mat_index = vert - 1
        neighbors = [j + 1 for j in range(len(graph[0])) if graph[vert_mat_index][j] == 1]

        for buddy in neighbors:
            if vert < buddy:
                new_edge = edge_elms[-1] + 1 if edge_elms else vert_elms[-1] + 1
                edge_elms.append(new_edge)
                edge_dict[new_edge] = [vert, buddy]
                relations.extend([[vert, new_edge], [buddy, new_edge]])

    # Initialize face elements and relations
    face_elms = []
    face_dict = {}

    # Construct faces using planar embedding
    for edge, (v1, v2) in edge_dict.items():
        for face_vertices in [embedding_nx.traverse_face(v=v1-1, w=v2-1), embedding_nx.traverse_face(v=v2-1, w=v1-1)]:
            face_vertices = list(face_vertices)
            if not any(sorted(face_vertices) == sorted(existing) for existing in face_dict.values()):
                new_face = face_elms[-1] + 1 if face_elms else edge_elms[-1] + 1
                face_elms.append(new_face)
                face_dict[new_face] = face_vertices
                relations.append([edge, new_face])

    # Count faces by size
    for face_vertices in face_dict.values():
        num_i_sides[len(face_vertices)] = num_i_sides.get(len(face_vertices), 0) + 1

    # Construct p-vector
    max_face_size = max(num_i_sides.keys(), default=2)
    p_k_vec = [num_i_sides.get(j, 0) for j in range(3, max_face_size + 1)]

    return p_k_vec


def p_gons(G: Union[nx.Graph, SimpleGraph], p: int = 3) -> int:
    r"""
    Compute the number of p-sided faces in a planar graph.

    This function determines the count of faces with exactly `p` sides in a given planar graph
    by leveraging the p-vector. The graph must be planar and connected.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        A planar graph for which the count of p-sided faces is computed.
    p : int, optional
        The number of sides of the faces to count. Defaults to 3 (triangular faces).

    Returns
    -------
    int
        The number of p-sided faces in the graph. Returns 0 if no such faces exist.

    Notes
    -----
    - This function assumes the input graph is planar.
    - It internally calls the `p_vector` function to calculate the p-vector of the graph.

    Examples
    --------
    Count the number of triangular faces in a hexagonal graph:

    >>> import graphcalc as gc
    >>> G = gc.cycle_graph(6)  # Hexagon
    >>> gc.p_gons(G, p=3)
    0

    Count the number of hexagonal faces in the same graph:

    >>> gc.p_gons(G, p=6)
    1

    Count the number of pentagonal faces in a graph with multiple face types:

    >>> G = gc.SimpleGraph()
    >>> G.add_edges_from([
    ...     (0, 1), (1, 2), (2, 3), (3, 0),  # Quadrilateral face
    ...     (0, 4), (4, 1),  # Two triangular faces
    ...     (1, 5), (5, 2)
    ... ])
    >>> gc.p_gons(G, p=5)
    0
    """
    vector = p_vector(G)
    return vector[p - 3] if p - 3 < len(vector) else 0

def fullerene(G: Union[nx.Graph, SimpleGraph]) -> bool:
    """
    Determine whether a graph is a fullerene.

    A fullerene is a 3-regular, planar, simple, and connected graph
    in which every face is either a pentagon or hexagon, and exactly
    12 of the faces are pentagons.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The graph to check.

    Returns
    -------
    bool
        True if G is a fullerene, False otherwise.
    """
    # Check if 3-regular
    if not all(degree == 3 for _, degree in G.degree):
        return False

    # Check if planar
    is_planar, _ = nx.check_planarity(G)
    if not is_planar:
        return False

    # Compute p-vector: [triangles, quads, pentagons, hexagons, ...]
    vector = p_vector(G)

    # Count pentagons
    pentagons = vector[2] if len(vector) > 2 else 0
    if pentagons != 12:
        return False

    # Ensure all other nonzero faces are hexagons
    for i, count in enumerate(vector):
        face_size = i + 3
        if face_size != 5 and face_size != 6 and count > 0:
            return False

    return True

def simple_graph(G: Union[nx.Graph, SimpleGraph]) -> bool:
    r"""
    Check if a graph is simple.

    A graph is simple if:
    1. It has no self-loops.
    2. It has no multiple edges.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The input graph.

    Returns
    -------
    bool
        True if the graph is simple, False otherwise.
    """
    # Check for self-loops
    if any(G.has_edge(u, u) for u in G.nodes):
        return False

    # Check for multiple edges (only relevant for MultiGraph)
    if isinstance(G, nx.MultiGraph):
        for u, v, count in G.edges(keys=True):
            if G.number_of_edges(u, v) > 1:
                return False

    return True


def polytope_graph(G: Union[nx.Graph, SimpleGraph]) -> bool:
    """
    Determine whether a graph is the 1-skeleton of a convex 3D polyhedron.

    According to Steinitz's theorem, a graph is a polytope graph (polyhedral graph)
    if and only if it is:
    1. Simple (no loops or multi-edges),
    2. Planar,
    3. 3-connected.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The graph to check.

    Returns
    -------
    bool
        True if G is a polytope graph, False otherwise.

    Examples
    --------
    >>> G = gc.path_graph(5)
    >>> gc.polytope_graph(G)
    False
    """
    # 1. Must be simple
    if not simple_graph(G):
        return False

    # 2. Must be planar
    is_planar, _ = nx.check_planarity(G)
    if not is_planar:
        return False

    # 3. Must be 3-connected
    if not nx.is_connected(G) or nx.node_connectivity(G) < 3:
        return False

    return True

def simple_polytope_graph(G: Union[nx.Graph, SimpleGraph]) -> bool:
    r"""
    Check if a graph is the graph of a simple polyhedron.

    A graph is the graph of a polyhedron (or a polytope graph) if and only if it is:
    1. Simple: The graph has no self-loops or multiple edges.
    2. Planar: The graph can be embedded in the plane without edge crossings.
    3. 3-Connected: The graph remains connected after removing any two vertices.
    4. 3-Regular: Each vertex has degree 3.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The input graph.

    Returns
    -------
    bool
        True if the graph is a polytope graph, False otherwise.

    Examples
    --------
    >>> import graphcalc as gc
    >>> G = gc.cube_graph()  # Octahedral graph is a simple polytope graph
    >>> gc.simple_polytope_graph(G)
    True

    >>> G = gc.path_graph(5)  # Path graph is not a simple polytope graph
    >>> gc.simple_polytope_graph(G)
    False
    """
    return gc.simple_graph(G) and gc.polytope_graph(G) and gc.connected_and_cubic(G)

def polytope_graph_with_p6_zero(G: Union[nx.Graph, SimpleGraph]) -> bool:
    r"""
    Check if a graph is the graph of a polyhedron with no hexagonal faces.

    A graph is the graph of a polyhedron (or a polytope graph) if and only if it is:
    1. Simple: The graph has no self-loops or multiple edges.
    2. Planar: The graph can be embedded in the plane without edge crossings.
    3. 3-Connected: The graph remains connected after removing any two vertices.
    4. No hexagonal faces: The graph has no hexagonal faces.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The input graph.

    Returns
    -------
    bool
        True if the graph is a polytope graph, False otherwise.

    Examples
    --------
    >>> import graphcalc as gc
    >>> G = gc.cube_graph()  # Cubical graph is a polytope graph with hexagonal faces
    >>> polytope_graph_with_p6_zero(G)
    True
    """
    return gc.polytope_graph(G) and gc.p_gons(G, p=6) == 0


def simple_polytope_graph_with_p6_zero(G: Union[nx.Graph, SimpleGraph]) -> bool:
    r"""
    Check if a graph is the graph of a simple polyhedron with no hexagonal faces.

    A graph is the graph of a polyhedron (or a polytope graph) if and only if it is:
    1. Simple: The graph has no self-loops or multiple edges.
    2. Planar: The graph can be embedded in the plane without edge crossings.
    3. 3-Connected: The graph remains connected after removing any two vertices.
    4. 3-Regular: Each vertex has degree 3.
    5. No hexagonal faces: The graph has no hexagonal faces.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The input graph.

    Returns
    -------
    bool
        True if the graph is a polytope graph, False otherwise.

    Examples
    --------
    >>> import graphcalc as gc
    >>> G = gc.cube_graph()  # Cubical graph is a simple polytope graph with hexagonal faces
    >>> gc.simple_polytope_graph_with_p6_zero(G)
    True
    """
    return gc.simple_polytope_graph(G) and gc.p_gons(G, p=6) == 0

def polytope_graph_with_p6_greater_than_zero(G: Union[nx.Graph, SimpleGraph]) -> bool:
    r"""
    Check if a graph is the graph of a polyhedron with at least one hexagonal face.

    A graph is the graph of a polyhedron (or a polytope graph) if and only if it is:
    1. Simple: The graph has no self-loops or multiple edges.
    2. Planar: The graph can be embedded in the plane without edge crossings.
    3. 3-Connected: The graph remains connected after removing any two vertices.
    4. At least one hexagonal face: The graph has at least one hexagonal face.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The input graph.

    Returns
    -------
    bool
        True if the graph is a polytope graph, False otherwise.

    Examples
    --------
    >>> import graphcalc as gc
    >>> G = gc.cube_graph()  # Cubical graph is a polytope graph with hexagonal faces
    >>> gc.polytope_graph_with_p6_greater_than_zero(G)
    False
    """
    return gc.polytope_graph(G) and gc.p_gons(G, p=6) > 0

def simple_polytope_graph_with_p6_greater_than_zero(G: Union[nx.Graph, SimpleGraph]) -> bool:
    r"""
    Check if a graph is the graph of a simple polyhedron with at least one hexagonal face.

    A graph is the graph of a polyhedron (or a polytope graph) if and only if it is:
    1. Simple: The graph has no self-loops or multiple edges.
    2. Planar: The graph can be embedded in the plane without edge crossings.
    3. 3-Connected: The graph remains connected after removing any two vertices.
    4. 3-Regular: Each vertex has degree 3.
    5. At least one hexagonal face: The graph has at least one hexagonal face.

    Parameters
    ----------
    G : networkx.Graph or graphcalc.SimpleGraph
        The input graph.

    Returns
    -------
    bool
        True if the graph is a polytope graph, False otherwise.

    Examples
    --------
    >>> import graphcalc as gc
    >>> G = gc.cube_graph()  # Cubical graph is a simple polytope graph with hexagonal faces
    >>> gc.simple_polytope_graph_with_p6_greater_than_zero(G)
    False
    """
    return gc.simple_polytope_graph(G) and gc.p_gons(G, p=6) > 0
