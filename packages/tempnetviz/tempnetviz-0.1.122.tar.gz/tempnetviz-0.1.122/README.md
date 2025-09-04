# TempNetViz

**TempNetViz** is an interactive GUI designed for exploring, analyzing, and visualizing **temporal graphs** i.e. graphs that evolve over time. This readme provides the essential information for the usage of TempNetViz, for more details see the [documentation](https://cnelias.github.io/TempNetVizDocs.github.io/).

## Installation & usage

You can install TempNetViz with pip using:

```bash
pip install tempnetviz
```

To start the GUI:

```bash
python -m tempnetviz.main_gui
```

## Quickstart

Your data should be stored in a single folder as **.csv files**, where each file represents the graph at a specific time point.

Steps to get started:

1. Click **Open** in the GUI to select the folder containing your `.csv` files.
2. Use the **Sub-graph selector** to choose one or multiple layers to visualize or analyze.
3. Adjust the **metrics** to explore structural properties of your data.
   You can apply a **graph cut** (edge pruning) for better readability on large graphs.
4. Switch between **Graph**, **Histogram**, and **Animation** views to gain different insights.

You can apply aesthetic changes (e.g. edge/nodes widths, colors...) to the results via the **Settings** button.

<img src="https://github.com/KelschLAB/TemporalGraphViz/raw/main/quickstart_numbered.png" alt="Quickstart" width="100%"/>

## Main Functionalities
Here we provide a short description of the main functionalities of the GUI. For more information, see the [documentation](https://cnelias.github.io/TempNetVizDocs.github.io/)

### Structure Visualization

Visualize temporal graphs as a 3D stack to see how connections evolve over time. You can compute various metrics to quantify node importance — important nodes will appear larger.
In this example, we also applied a colormap (via the settings) to make the results more explicit.

<img src="https://github.com/KelschLAB/TemporalGraphViz/raw/main/3D_view.png" alt="Graph Structure" width="60%"/>

### Metrics Distribution

Visualize how metrics evolve over time using histograms. By default, the different time steps are stacked on top of each other for easier comparison.
In this example, deep blue corresponds to early times and deep red to the last datapoints.

<img src="https://github.com/KelschLAB/TemporalGraphViz/raw/main/histo_view.png" alt="Metrics Distribution" width="70%"/>

### Graph Animation

Animate the temporal evolution of your graph to better understand dynamics.

<img src="https://github.com/KelschLAB/TemporalGraphViz/raw/main/graph_animation.gif" alt="Graph Animation" width="100%"/>

### Temporal Layout

You can also display the results as a temporal layout. In this example, the color and thickness of node a shows its strength value. 

<img src="https://github.com/KelschLAB/TemporalGraphViz/raw/main/temporal_layout.png" alt="Temporal Layout" width="100%"/>

## License

This project is licensed under the MIT License.
