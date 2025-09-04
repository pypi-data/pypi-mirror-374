# TempGraphViz

**TempGraphViz** is an interactive GUI designed for exploring, analyzing, and visualizing **temporal graphs** — graphs that evolve over time.

## Installation & usage

You can install TempGraphViz with pip using:

pip install tempgraphviz

To start the GUI:

python -m tempgraphviz.main_gui

## Quickstart

Your data should be stored in a single folder as **.csv files**, where each file represents the graph at a specific time point.

Steps to get started:

1. Click **Open** in the GUI to select the folder containing your `.csv` files.
2. Use the **Sub-graph selector** to choose one or multiple layers to visualize or analyze.
3. Adjust the **layout** and **metrics** to explore structural properties.
4. Optionally, apply a **graph cut** for better readability on large graphs.
5. Switch between **Graph**, **Histogram**, and **Animation** views to gain different insights.

![Quickstart](https://github.com/KelschLAB/TemporalGraphViz/raw/main/quickstart_numbered.png)

## Main Functionalities

### Structure Visualization

Visualize temporal graphs as a 3D stack to see how connections evolve over time. You can compute various metrics to quantify node importance — important nodes will appear larger.

![Graph Structure](https://github.com/KelschLAB/TemporalGraphViz/raw/main/3D_view.png)

### Metrics Distribution

Visualize how metrics evolve over time using histograms.

![Metrics Distribution](https://github.com/KelschLAB/TemporalGraphViz/raw/main/histo_view.png)

### Temporal Layout

You can also display the results as a temporal layout.

![Temporal Layout](https://github.com/KelschLAB/TemporalGraphViz/raw/main/temporal_layout.png)


### Graph Animation

Animate the temporal evolution of your graph to better understand dynamics.

![Graph Animation](https://github.com/KelschLAB/TemporalGraphViz/raw/main/graph_animation.gif)

## License

This project is licensed under the MIT License.
