# Graph to Curve Free Space Diagram
## Traversal Distance Python Library

### Installation
Download package and dependencies from GitHub.

### Dependencies
- [NumPy](numpy.org) is used to calculate dimensions of free space diagrams.
- Free space diagrams are stored using [Shapleys](shapely.readthedocs.io) Polygon and Multipolygon classes.
- The GUI of the free space diagram is built using [matplotlib](matplotlib.org).

## Example
This image shows the Arc de Triomphe is Paris, France. It is surrounded by
twelve intersecting roads and one pedestrian tunnel.   
![Image](/docs/arc_de_triomphe.jpg?raw=true)
Given a roadmap, we can build the road network surrounding the monument
and a path for any given vehicle.
```
python3 main.py samples/arc_de_triomphe samples/vehicle_path -f docs/arc_de_triomphe_graph.png
```
![Image](/docs/arc_de_triomphe_graph.png?raw=true)
In this plot, the road network is defined as a graph (colored black) and the
vehicle path is defined as a curve (colored dashed gray). By computing the
Traversal Distance of the graph and curve, we can visualize the free space
diagram is 3D space.  
```
python3 main.py samples/arc_de_triomphe samples/vehicle_path -e 5.0 -f docs/arc_de_triomphe_freespace.png
```
![Image](/docs/arc_de_triomphe_freespace.png?raw=true)

The the free space is shown where epsilon equals five.

## Author
- **Will Rodman** wrodman@tulane.edu

### Version History
- **0.1.** 12-31-2022

### Lisence
MIT License • Copyright (c) 2022 Computational Geometry @ Tulane
