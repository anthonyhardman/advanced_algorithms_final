# Final Project Part 2: Report and Implementation


## Background
Delaunay triangulation and Voronoi diagrams are fundamental constructs in computational geometry, each offering unique properties and applications. Delaunay triangulation for a set of points in a plane involves creating triangles such that no point is inside the circumcircle of any triangle. This triangulation maximizes the minimum angle of all the angles of the triangles in the triangulation, helping avoid skinny triangles. The Voronoi diagram, a dual of the Delaunay triangulation, partitions a plane into regions based on distance to a set of specified points. Each region contains all the points closer to a specific site than to any other.

The significance of Delaunay triangulation lies in its properties, which lend themselves to various applications, such as mesh generation, pathfinding algorithms, and spatial analysis. Voronoi diagrams, on the other hand, are widely used in fields such as meteorology, aviation, and urban planning for proximity-based problem-solving.

## Objective
The primary objective of this project is to develop an efficient algorithm to generate Delaunay triangulation from a given set of points in a two-dimensional space. Leveraging the divide-and-conquer method, the algorithm aims to efficiently triangulate a large number of points by recursively dividing the problem into smaller, manageable sub-problems and then merging the solutions. The resulting triangulation will form the foundation for constructing a Voronoi diagram. This approach is chosen for its effectiveness in handling large datasets and its capacity to achieve a balance between computational complexity and performance.

## Real World Application
The use of Delaunay triangulation in conjunction with Voronoi diagrams can be particularly beneficial in dynamic environments where safety and efficiency are paramount. This system's application can extend to various types of autonomous vehicles, including ground robots, drones, and even underwater exploration vehicles, where path optimization and obstacle avoidance are critical for successful navigation and mission accomplishment.


## Problem Statement for Delaunay Triangulation

**Input Specification**:
- The input to the algorithm is a list of 2D sites, each defined as a `Site` object. These sites represent distinct points in a two-dimensional plane.
- It is preferable to have a set of points where collinear sites are minimal to avoid complications in the triangulation process.

**Output Specification**:
- The output is the complete set of edges that form the Delaunay triangulation of the given sites.
- Each edge in the triangulation is represented as a `QuadEdge` in the QuadEdge data structure, efficiently encoding the connectivity and relationships between the triangulation's vertices.
- Specific emphasis is given to identifying the leftmost and rightmost edges of the convex hull, integral to the merging process in the divide-and-conquer approach.
- All edges are tracked and managed using a dictionary or a similar data structure for efficient access and manipulation.

**Performance Requirement**:
- The algorithm aims to achieve a time complexity of $O(n \log n)$, aligning with the performance benchmarks established in the foundational paper on this topic: "Primitives for the Manipulation of General Subdivisions and the Computation of Voronoi Diagrams" by Leonidas Guibas and Jorge Stolfi.

**Additional Notes**:
- **Complete Triangulation**: The Delaunay triangulation algorithm will produce a comprehensive mesh of triangles, represented by the interconnected QuadEdges, encompassing the entire set of input sites.
- **Collinear Points Handling**: The algorithm should account for the presence of collinear points or outline any limitations arising from such scenarios.
- **Data Structure Utilization**: The employment of an efficient data structure, like a dictionary, for edge tracking is crucial to meeting the desired computational performance and forms a core component of the algorithm's design.

**Pseudo code**:
```
FUNCTION __triangulate(sites: List of Site) RETURNS Tuple of (QuadEdge, QuadEdge)
    IF length of sites is 2 THEN
        Create an edge a between sites[0] and sites[1]
        RETURN (a, a.sym)

    ELSE IF length of sites is 3 THEN
        Create edge a between sites[0] and sites[1]
        Create edge b between sites[1] and sites[2]
        Splice a.sym and b

        IF ccw(sites[0], sites[1], sites[2]) THEN
            Connect b and a
            RETURN (a, b.sym)

        ELSE IF ccw(sites[0], sites[2], sites[1]) THEN
            Connect b and a
            RETURN (c.sym, c)

        ELSE
            RETURN (a, b.sym)

    ELSE
        Divide the sites into two halves
        (ldo, ldi) = __triangulate(left half of sites)
        (rdi, rdo) = __triangulate(right half of sites)

        Merge the two halves:
        WHILE true DO
            Adjust ldi and rdi to find the lower common tangent
            IF left_of(rdi.origin, ldi) THEN
                Move ldi to its left neighbor
            ELSE IF right_of(ldi.origin, rdi) THEN
                Move rdi to its right neighbor
            ELSE
                break

        Connect rdi.sym and ldi to create base edge base1

        Adjust ldo and rdo if they are the same as ldi and rdi origins respectively

        WHILE true DO
            Find candidate edges lcand and rcand

            Remove edges violating Delaunay condition around lcand
            WHILE valid(lcand) and in_circle(base1.dest, base1.origin, lcand.dest, lcand.onext.dest) DO
                Delete lcand
                Update lcand to next edge

            Remove edges violating Delaunay condition around rcand
            WHILE valid(rcand) and in_circle(base1.dest, base1.origin, rcand.dest, rcand.oprev.dest) DO
                Delete rcand
                Update rcand to previous edge

            IF no valid lcand or rcand THEN
                break

            Connect edges to restore Delaunay condition
            IF not valid(lcand) OR (valid(rcand) AND in_circle(lcand.dest, lcand.origin, rcand.origin, rcand.dest)) THEN
                Connect rcand and base1.sym
            ELSE
                Connect base1.sym and lcand.sym

        RETURN (ldo, rdo)
END FUNCTION
```
**Runtime Analysis:**
1. **Divide-and-Conquer Approach**:
   - **Divide Step**: The algorithm recursively divides the set of points into smaller subsets. This division is a simple operation, usually taking linear time, $O(n) $, where $n $ is the number of points.
   - **Conquer Step**: For very small subsets (like 2 or 3 points), the algorithm directly computes the triangulation in constant time, $O(1) $.

2. **Merge Step**:
   - **Lower Common Tangent**: Finding the lower common tangent involves iterating over the edges of the two subproblem hulls. This step can take up to linear time in the size of the subproblem, $O(n)$, in the worst case.
   - **Edge Flipping**: Restoring the Delaunay condition by edge flipping is typically sub-linear per merge step but can approach linear time, $O(n) $, in the worst case for each level of recursion.

3. **Recursive Structure**:
   - The depth of recursion is $O(\log n) $ because the problem size is halved at each level.
   - If each merge operation is $O(n) $ in the worst case, the total work done at each level of recursion is $O(n) $.

4. **Overall Complexity**:
   - The total time complexity is the product of the work done per level of recursion and the number of levels. Since the depth of the recursion is $O(\log n) $ and the work per level is $O(n) $, the overall complexity is $O(n \log n) $.
   - This $O(n \log n) $ complexity is consistent with the performance achieved in the foundational paper by Guibas and Stolfi.

### Problem Statement for Voronoi Diagram Generation

**Objective**:
- Develop an algorithm to generate a Voronoi diagram from the Delaunay triangulation of a set of 2D points.

**Input Specification**:
- The input to the Voronoi diagram generation algorithm is the complete list of edges resulting from the Delaunay triangulation process.
   - These edges are represented as `QuadEdge` objects, encompassing the entire Delaunay triangulation.
   - The input list of edges includes all connections and relationships established during the triangulation process.

**Output Specification**:
- The output of the algorithm is a list of Voronoi edges.
   - Each Voronoi edge is defined by its origin and destination points, representing the boundaries between adjacent Voronoi cells.
   - The origin and destination of each Voronoi edge are the circumcenters of adjacent triangles in the Delaunay triangulation.

**Performance Requirement**:
- The target complexity for generating the Voronoi diagram is to align with the complexity of the Delaunay triangulation process, specifically $ O(n \log n) $.
   - This ensures that the Voronoi diagram generation does not add significant computational overhead beyond the Delaunay triangulation.

**Additional Considerations**:
- **Efficient Conversion**: The algorithm should effectively utilize the Delaunay triangulation output, converting triangulation edges to Voronoi edges in an optimized manner.
- **Handling Special Cases**: Special cases, such as dealing with edges at the boundary of the triangulation, should be appropriately managed to ensure a complete and accurate Voronoi diagram.
- **Seamless Integration**: The transition from Delaunay triangulation to Voronoi diagram generation should be smooth and integrated, leveraging the existing relationships and data structures from the triangulation process.

**Pseudo Code**
```
FUNCTION voronoi() RETURNS List of VoronoiEdges
    Initialize triangles as the result of find_triangles()

    Initialize a dictionary triangle_to_circumcenter
    FOR each triangle in triangles DO
        Calculate the circumcenter for the triangle
        Map the triangle to its circumcenter in triangle_to_circumcenter

    Initialize a dictionary edge_to_triangles
    FOR each triangle in triangles DO
        FOR each pair of sites (site1, site2) in the triangle DO
            Create an edge_key as a frozenset of (site1, site2)
            Append the triangle to edge_to_triangles[edge_key]

    Initialize an empty set voronoi_edges
    FOR each pair of adjacent triangles in edge_to_triangles.values() DO
        IF there are exactly 2 adjacent triangles THEN
            Get the two triangles t1 and t2
            Find their circumcenters cc1 and cc2 from triangle_to_circumcenter
            Create a VoronoiEdge between cc1 and cc2
            Add the VoronoiEdge to voronoi_edges

    Convert voronoi_edges to a list

    RETURN list of VoronoiEdges
END FUNCTION
```
The runtime analysis of the Voronoi diagram generation algorithm, which is based on the Delaunay triangulation output, can be structured as follows:

### Runtime Analysis of Voronoi Diagram Generation Algorithm

1. **Input Processing**:
   - The input to the Voronoi algorithm is the output of the Delaunay triangulation, which is a set of edges (QuadEdges) and their connectivity.
   - The time complexity of processing this input is $O(1)$ since it's merely passing the already computed Delaunay triangulation data.

2. **Circumcenter Calculation**:
   - For each triangle in the Delaunay triangulation, the algorithm calculates its circumcenter.
   - The circumcenter calculation for a single triangle is a constant-time operation, $O(1)$.
   - If there are $T$ triangles in the triangulation, this step has a complexity of $O(T)$. Typically, $T$ is proportional to the number of sites $n$, so this step is $O(n)$.

3. **Edge Mapping to Triangles**:
   - The algorithm iterates over each triangle and identifies the edges that form the triangle.
   - Since each triangle has 3 edges, and the number of triangles is roughly proportional to the number of sites $n$, this step also operates in $O(n)$ time.

4. **Voronoi Edge Construction**:
   - For each edge shared by two triangles, the algorithm constructs a Voronoi edge between their circumcenters.
   - This operation is done for each pair of adjacent triangles, and since each triangle shares edges with its neighbors, this step is also $O(n)$.

5. **Overall Complexity**:
   - The most time-consuming steps of the Voronoi diagram generation are linear with respect to the number of sites $n$, resulting in an overall complexity of $O(n)$.
   - Since the Voronoi diagram generation relies on the output of the Delaunay triangulation, its overall complexity remains dominated by the Delaunay triangulation process. Therefore, the combined complexity of generating both Delaunay triangulation and Voronoi diagram is $O(n \log n)$, where the logarithmic factor comes from the Delaunay triangulation.

<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/x-mathjax-config">
    MathJax.Hub.Config({ tex2jax: {inlineMath: [['$', '$']]}, messageStyle: "none" });
</script>
