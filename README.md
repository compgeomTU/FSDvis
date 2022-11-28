# Graph By Curve Free Space Diagram
## Traversal Distance Python Library Visualizer

### Installation
Download zip package and dependencies from GitHub.

### Dependencies
* [NumPy](numpy.org) is used to calculate dimensions of free space diagrams.
* Free space diagrams are stored using [Shapleys](shapely.readthedocs.io)
Polygon and Multipolygon classes.
* The GUI of the free space diagram is built using [matplotlib](matplotlib.org).

### Command Line
To run the program, run a command line execution in the package with format:
```
python3 main.py <graph filename: str> <curve filename: str>
```

**Flags:**
* `-e` type: *int* | specifies the Epsilon value for the free space diagram.

* `-f` type: *str* | saves plot as a type of file.

* `-l` type: *str* logged computation of Traversal Distance and free space
diagram as a .log file.

### Sample Inputs
Sample graph and curve files can be copied and pasted into the command line.

1. samples/A samples/B
2. samples/H samples/G
3. samples/P samples/Q
4. samples/arc_de_triomphe samples/vehicle_path

### Example
This image shows the Arc de Triomphe is Paris, France. It is surrounded by
twelve intersecting roads and one pedestrian tunnel.
**arc_de_triomphe.jpg:**
![Image](/docs/arc_de_triomphe.jpg?raw=true)

Given a roadmap, we can build the road network surrounding the monument
and a path for any given vehicle.
```
python3 main.py samples/arc_de_triomphe samples/vehicle_path -f docs/arc_de_triomphe_.png
```
**arc_de_triomphe_freespace.png:**
![Image](/docs/arc_de_triomphe_graph.png?raw=true)

In this plot, the road network is defined as a graph (colored black) and the
vehicle path is defined as a curve (colored dashed gray). By computing the
Traversal Distance of the graph and curve, we can visualize the free space
diagram is 3D space.  
```
python3 main.py samples/arc_de_triomphe samples/vehicle_path -e 5.0 -f docs/arc_de_triomphe_graphpng
```
**arc_de_triomphe.png:**
![Image](/docs/arc_de_triomphe_freespace.png?raw=true)

The free space is shown where epsilon equals five. To Save the data generated
by the Traversal Distance and free space diagram, we can create a log as the
program runs.  
```
python3 main.py samples/arc_de_triomphe samples/vehicle_path -e 5.0 -l docs/arc_de_triomphe_log.log
```
**arc_de_triomphe.log:**
![Image](/docs/arc_de_triomphe_log.png?raw=true)

#### Author
* **Will Rodman**     | wrodman@tulane.edu

#### Contributors
* **Dr. Carola Wenk** | cwenk@tulane.edu             | https://www.cs.tulane.edu/~carola/
* **Erfan Hosseini**  | shosseinisereshgi@tulane.edu | https://erfanhosseini.com
* **Emily Powers**    | epowers3@tulane.edu
* **Rena Repenning**  |                              | http://renarepenning.com

#### Version History
**1.0.** 11-31-2022

#### Lisence
MIT License • Copyright (c) 2022 Computational Geometry @ Tulane
