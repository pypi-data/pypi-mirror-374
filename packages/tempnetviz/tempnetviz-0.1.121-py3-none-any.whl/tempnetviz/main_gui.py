import tkinter as tk
from tkinter import ttk

import webbrowser
from tkinter import filedialog
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from functools import partial
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
import os
import sys

if __name__ == "__main__" and __package__ is None:
    # Go up one level to the package root
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    __package__ = "tempnetviz"

from tempnetviz.read_graph import *
from tempnetviz.settings_window import settingsWindow
from tempnetviz.listbox_selection import MultiSelectDropdown
from tempnetviz.tooltip import ToolTip
from tempnetviz.temporal_layout import plot_temporal_layout

#To-do: 
#       - put layout button in settings? It is actually not super necessary to have it in main app.
#       - include link of doc once online in the GUI (setting/ help section)
#       - make sure that the "Run" instruction in documentation actually works

###### For future versions: 
#       - simplify the metric code in read_graph.py for better readability
#       - Add dynamic layout for animation, such that nodes are not fixed but can move closer/further to points they are similar to.
#       - Include compatibility with other formats (right now, only compatible with csv format).
#       - include minimal spanning tree, and jaccard metric (Edge metrics for visual graph analytics: a comparative study) in later version of project.
#       - add local clustering coefficient metric
#       - Include measure of topology type? i.e. homophily/clustering/degree/spatial 
#           (see Spatially embedded recurrent neural networks reveal widespread links between structural and functional neuroscience, 2023)

class App:
    def __init__(self, root):
        #setting window size
        width=1200
        height=700
        
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=True, height=True)
        root.title("Multilayer graph analysis")

        # variables that can change after interacting with the buttons
        self.dirpath = None
        self.path_to_file = None
        self.layout_style = "fr"
        self.node_metric = "none"
        self.percentage_threshold = 0.0
        self.mnn_number = None
        self.mutual = True
        self.degree = 0
        self.idx = []
        self.cluster_num = 0
        self.display_type = "plot"
        self.edge_type = "affinity"
        self.view_type = "3D"
        self.histo_type = "stacked"
        self.remove_loops = True # for the app to know if feedback loops should be plotted or not 
        self.edge_thickness_var = tk.StringVar(value = "5") # variable for changing edge type in settings window
        self.node_thickness_var = tk.StringVar(value = "20") # variable for changing edge type in settings window
        self.animation_speed_var = tk.StringVar(value = "200") # variable for changing the speed of animation
        self.show_histogram_legend = True
        self.scale_edge_width = True # variable for scaling the thickness of edge to their value
        self.between_layer_edges = True
        self.rm_index = True # if True, remove the first row and column of input file(s), considering them as indexing
        self.show_node_lb = True # variable for showing the names of the nodes in the graph
        self.show_planes = False 
        self.community_algorithm = "louvain"
        self.edge_cmap = matplotlib.colormaps.get_cmap("Greys")
        self.node_cmap = "none"
        self.num_bins = 10 # number of bins for the histograms
        self.show_colorbars = False

        self.color1 = "#E4F8FF"
        self.color2 = "#FFF7E3"
        self. color3 = "#FFE8E3"
        self.color_display_btn = "#FFD7CF"
    
        # Frames
        menu_frame = tk.Frame(root, bg = self.color1, highlightbackground="gray", highlightthickness=1)
        menu_frame.place(relx=0, rely=0, relwidth=0.22, relheight=0.2)
        
        btn_frame = tk.Frame(root, bg = self.color2, highlightbackground="gray", highlightthickness=1) #main buttons frame
        btn_frame.place(relx=0, rely=0.2, relwidth=0.22, relheight=0.65)
        
        result_display_frame = tk.Frame(root, bg = self.color3, highlightbackground="gray", highlightthickness=1) #result display frame
        result_display_frame.place(relx=0, rely=0.78, relwidth=0.22, relheight=0.22)

        self.content_frame = tk.Frame(root) # content frame, for plotting and stats
        self.content_frame.place(relx=0.22, rely=0.1, relwidth=0.78, relheight=0.8)

        # File menu/settings button
        load_label = tk.Label(menu_frame, text = "Data loading / Settings", font = 'Helvetica 12 bold', bg = self.color1)
        load_label.place(relx = 0.1, rely = 0.1, relwidth=0.8, relheight=0.35)
        load_button = tk.Button(menu_frame, text = "Open")
        load_button.place(relx=0.05, rely = 0.5, relwidth=0.43, relheight=0.35)
        load_button["command"] = self.load_button_command
        settings_button = tk.Menubutton(menu_frame, text = "Settings")
        settings_button.menu = tk.Menu(settings_button, tearoff=False)   
        settings_button["menu"]= settings_button.menu  
        settings_button.menu.add_command(label="Settings", command=self.settings_window)
        settings_button.menu.add_command(label="Reset",command = self.reset)
        link = "https://stackoverflow.com/questions/71458060/how-to-open-a-link-with-an-specific-button-tkinter" #link to docs
        settings_button.menu.add_command(label="Help", command =lambda: webbrowser.open(link))
        settings_button.place(relx=0.53,rely = 0.5, relwidth=0.43, relheight=0.35)
        
        # Folder selection Menubutton
        analysis_label = tk.Label(btn_frame, text = "Data analysis", font = 'Helvetica 12 bold', bg = self.color2)
        analysis_label.place(relx = 0.1, rely = 0.05, relwidth=0.8)
        origin, distance_between = 0.15, 0.15
        padx, pady, font = 0, 30, '5'
        graph_selector_label = tk.Label(btn_frame, text = "Sub-graph:", bg = self.color2)
        graph_selector_label.place(relx= 0.07, rely = origin, relwidth=0.25, relheight=0.08)
        
        # Graph file(s) selection menu
        self.graph_selector = MultiSelectDropdown(btn_frame, [], 
            button_text="Select graph file(s)", apply_callback=self.get_checked)
        self.graph_selector.button.place(relx=0.34, rely=origin, relwidth=0.57, relheight=0.08)
        self.path_variable_list = [] # storing the menu options here
        self.path_label_list = []
        self.active_path_list = [] # storing selected paths here

        # layout selection
        layout_label = tk.Label(btn_frame, text = "Layout: ", bg = self.color2)
        layout_label.place(relx=0.12, rely = origin+distance_between, relheight=0.06)
        layout_list = ["circle", "drl", "fr", "kk", "large", "random", "tree"]
        self.plot_selector=ttk.Combobox(btn_frame, values = layout_list, state = "readonly")
        self.plot_selector.place(relx=0.35, rely = origin+distance_between, relheight=0.06)
        self.plot_selector.set("Graph layout")
        self.plot_selector.bind('<<ComboboxSelected>>', self.plot_changed)
        self.plot_selector_tooltip = ToolTip(self.plot_selector, "Click here to change the spatial organization\n of the nodes within the graph.", 700)

        # metric selection for nodes
        metric_label = tk.Label(btn_frame, text = "Metric: ", bg = self.color2)
        metric_label.place(relx=0.12, rely = origin+2*distance_between, relheight=0.06)
        metric_values = ["none", "strength", "betweenness", "closeness", "eigenvector centrality", "page rank", "hub score", "authority score", "rich-club", "k-core"]
        self.node_metric_selector=ttk.Combobox(btn_frame, values = metric_values, state = "readonly")
        self.node_metric_selector.place(relx=0.35, rely = origin+2*distance_between, relheight=0.06)
        self.node_metric_selector.set("Node metric")
        self.node_metric_selector.bind('<<ComboboxSelected>>', self.node_changed)
        self.node_metric_selector_tp = ToolTip(self.node_metric_selector, "The node metrics are different measurements of the importance\n of the nodes within the graph", 700)

        # Graph-cut type selection
        graphcut_label = tk.Label(btn_frame, text = "Graph cut: ", bg = self.color2)
        graphcut_label.place(relx=0.05, rely = origin+3*distance_between, relheight=0.06)
        graphcut_values = ["none", "threshold", "mutual nearest neighbors", "nearest neighbors"]
        self.graphcut_selector=ttk.Combobox(btn_frame, values = graphcut_values, state = "readonly")
        self.graphcut_selector.place(relx=0.35, rely = origin+3*distance_between, relheight=0.06)
        self.graphcut_selector.set("Graph-cut type")
        self.graphcut_selector.bind('<<ComboboxSelected>>', self.graphcut_param_window)
        self.graphcut_tooltip = ToolTip(self.graphcut_selector, "Click here to prune the edges of the graph(s). Threshold will remove weak edges,\nwhile nearest neighbors based cut only keeps edges between nodes that are functionaly close.", 700)
        
        # Button to open clustering window
        self.cluster_button = tk.Button(btn_frame)
        self.cluster_button["text"] = "cluster nodes"
        self.cluster_button.place(relx=0.2, rely = origin+4*distance_between, relwidth= 0.6, relheight=0.1)
        self.cluster_button["command"] = self.cluster_button_command
        self.cluster_button_tooltip = ToolTip(self.cluster_button, "Click here to detect communities in the graph(s).\n Nodes that are similar will be colored the same", 700)

        # Display type buttons (plot, stats, animation)
        tk.Label(result_display_frame, text="Display type", font = 'Helvetica 12 bold', bg =  self.color3).place(relx = 0.1, rely = 0.1, relwidth=0.8, relheight=0.2)
        self.plot_btn = tk.Button(result_display_frame, text='Multi-layer')
        self.plot_btn.place(relx = 0.1, rely = 0.4, relwidth=0.38, relheight=0.2)
        self.plot_btn["command"] = self.plot_clicked
        self.stats_btn = tk.Button(result_display_frame, text='Histogram')
        self.stats_btn.place(relx = 0.5, rely = 0.4, relwidth=0.39, relheight=0.2)
        self.stats_btn["command"] = self.stats_clicked
        self.anim_btn = tk.Button(result_display_frame, text='Animation')
        self.anim_btn.place(relx = 0.1, rely = 0.65, relwidth=0.39, relheight=0.2)
        self.anim_btn["command"] = self.animation_clicked
        self.tl_btn = tk.Button(result_display_frame, text='Temp. layout')
        self.tl_btn.place(relx = 0.5, rely = 0.65, relwidth=0.39, relheight=0.2)
        self.tl_btn["command"] = self.templayout_clicked
        self.plot_btn.config(bg="#d1d1d1")
        self.stats_btn.config(bg="#f0f0f0")
        self.anim_btn.config(bg="#f0f0f0")
        self.tl_btn.config(bg="#f0f0f0")
        
        # Starting instructions label
        txt = "------------------------------------- QUICKSTART --------------------------------------------\n\n"
        txt += "1. Select the directory/folder where your files are stored with the  'Open'  button.\n"
        txt += "\n2. Then, select the graph file(s) with the 'sub-graph' drop-down menu to start plotting.\n"
        txt += "      You can select files by dragging the mouse, or by holding ctrl and clicking.\n\n"
        txt += "3. Change the representation with the layout and metric buttons. If you are working with \n"
        txt += "      large graphs, apply a graph cut to remove weak edges and improve visibility.\n\n"
        txt += "4. You can switch the result display with the 'multi-layer', 'statistics',\n 'animation' and 'Temp. layout' buttons"
        self.label = tk.Label(self.content_frame, font = 'Helvetica 13 bold', 
                              text = txt)
        self.label.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.5)
        
    # functions for folder selection
    def load_button_command(self):
        """ Selects the directory/folder path where graph layers are contained, and updates the list of selectable graph layer """
        self.dirpath = filedialog.askdirectory(title="Select the directory/folder which contains the graph file(s)")
        self.path_variable_list = []
        self.path_label_list = []
        if len(self.dirpath) == 0:
            return
        path_list = [p for p in os.listdir(self.dirpath) if p.endswith(".csv")]
        self.path_list = path_list
        self.graph_selector.choices = self.path_list
        self.graph_selector.refresh_listbox()
                
    # function for graph selection and display
    def get_checked(self):
        """ Updates list of paths when graph layer selector is clicked """
        lst = [self.graph_selector.listbox.get(i) for i in self.graph_selector.listbox.curselection()]
        self.active_path_list = lst
        self.path_to_file = [self.dirpath + "/" + self.active_path_list[i] for i in range(len(self.active_path_list))]   
        self.automatic_threshold([self.path_to_file[0]])
        if self.display_type == "plot":
            self.plot_in_frame()
        elif self.display_type == "stats":
            self.stats_in_frame()
        elif self.display_type == "animation":
            self.animation_in_frame()

    def reset(self):
        """
        Resets every user-selected options aside from the path/graph selected and the type of graph edges.
        """
        def reset_clicked(self, win):
            self.plot_selector.set("Graph layout")
            self.node_metric_selector.set("Node metric")
            self.graphcut_selector.set("Graph-cut type")
            self.node_metric = None
            self.idx = []
            self.percentage_threshold = 0.0
            self.mnn_number = None
            self.mutual = True
            if self.display_type == "plot":
                self.plot_in_frame()
            elif self.display_type == "stats":
                self.stats_in_frame()
            elif self.display_type == "animation":
                self.animation_in_frame()
            win.destroy()
            
        popup = tk.Toplevel(root)
        popup.wm_title("Reset plot parameters?")
        label = ttk.Label(popup, text=" Graph layout, color labels and cut threshold will be reset.\nPath and edge type (affinity/distance) will not be affected.")
        label.pack(side="top")
        B1 = ttk.Button(popup, text="Ok", command = partial(reset_clicked, self, popup))
        B1.pack(side="left", padx = 50)
        B2 = ttk.Button(popup, text="No", command = popup.destroy)
        B2.pack(side="left")
        
    def automatic_threshold(self, path):
        data = read_graph(path)[0]
        if data.shape[0] > 70:
            self.percentage_threshold = 80
        if data.shape[0] > 60:
            self.percentage_threshold = 70
        elif data.shape[0] > 50:
            self.percentage_threshold = 60
        elif data.shape[0] > 40:
            self.percentage_threshold = 50 
        elif data.shape[0] > 30:
            self.percentage_threshold = 40
        elif data.shape[0] > 20:
            self.percentage_threshold = 30
        else:
            return
        self.graphcut_selector.set("threshold")
        tk.messagebox.showinfo(self, f"An automatic threshold of {self.percentage_threshold}% was applied to improve visibility.\nTo change this, use the 'graph cut' menu to input the desired settings.")
                
    def settings_window(self):
        settingsWindow(root, self) # creates a settings window
         
    # central function for plotting the graph(s)
    def plot_in_frame(self):
        if len(self.active_path_list) == 0:
            return
        for fm in self.content_frame.winfo_children():
            fm.destroy()
            root.update()
            
        # Show temporary "Loading..." label before plotting
        self.label = ttk.Label(self.content_frame, text="Rendering graph...", font = 'Helvetica 20 bold')
        self.label.place(relx=0.3, rely=0.2, relwidth=0.8, relheight=0.4)
        self.content_frame.update()
                
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        f = Figure(figsize=(950*px,500*px))
        if len(self.path_to_file) > 1 and self.view_type == "3D":
            a = f.add_subplot(111, projection='3d')
            a.set_box_aspect((2,2,1), zoom=1.5)
        else:
            a = f.add_subplot(111)
            
        display_graph(self.path_to_file, a, percentage_threshold = self.percentage_threshold, mnn = self.mnn_number, mutual = self.mutual, \
                      avg_graph = self.view_type == "avg", affinity = self.edge_type == "affinity",  rm_fb_loops = self.remove_loops, \
                      layout = self.layout_style, node_metric = self.node_metric, rm_index = self.rm_index, \
                      idx = self.idx, cluster_num = self.cluster_num, layer_labels=self.path_to_file, deg = self.degree,
                      edge_width = int(self.edge_thickness_var.get()), node_size = int(self.node_thickness_var.get()), 
                      scale_edge_width = self.scale_edge_width, between_layer_edges = self.between_layer_edges,
                      node_labels = self.show_node_lb, show_planes = self.show_planes, edge_cmap = self.edge_cmap, 
                      node_cmap = self.node_cmap)
            
        if self.show_colorbars:
            f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=self.edge_cmap), ax=a, label="Normalized edge value", shrink = 0.3, location = 'right', pad = 0.1)
            if self.node_metric != "none" and self.node_cmap != "none":
                f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=self.node_cmap), ax=a, label="Normalized metric value", shrink = 0.3, location = 'left')
            else: # to keep layout consistent across changes of settings
                cb = f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=cm.Reds), ax=a, label="Normalized metric value", shrink = 0.3, location = 'left')
                cb.remove()
            
        f.subplots_adjust(left=0, bottom=0, right=0.948, top=1, wspace=0, hspace=0)

        canvas = FigureCanvasTkAgg(f, master=self.content_frame)
        NavigationToolbar2Tk(canvas, self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()#fill=tk.BOTH, expand=True, side="top") 
        self.label.destroy()
        
    # central function for displaying the statistics of the graph(s)
    def stats_in_frame(self):
        if len(self.active_path_list) == 0:
            return
        for fm in self.content_frame.winfo_children():
            fm.destroy()
            root.update()
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        f = Figure(figsize=(800*px,400*px), dpi = 100)
        a = f.add_subplot(111)
        display_stats(self.path_to_file, a, percentage_threshold=self.percentage_threshold, rm_index = self.rm_index,
                      affinity = self.edge_type == "affinity", mnn = self.mnn_number, mutual = self.mutual, 
                      node_metric = self.node_metric, avg_graph = self.view_type == "avg",
                      stacked = self.histo_type == "stacked", deg = self.degree, show_legend = self.show_histogram_legend, bins = self.num_bins)
        
        canvas = FigureCanvasTkAgg(f, master=self.content_frame)
        NavigationToolbar2Tk(canvas, self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()#fill=tk.BOTH, expand=True, side="top") 
       
    def animation_in_frame(self):
        if len(self.active_path_list) == 0:
            return
        for fm in self.content_frame.winfo_children():
            fm.destroy()
            root.update()

        f, a = display_animation(self.path_to_file, self.content_frame, percentage_threshold = self.percentage_threshold, mnn = self.mnn_number,
                      mutual = self.mutual, avg_graph = self.view_type == "avg", affinity = self.edge_type == "affinity",
                      rm_fb_loops = self.remove_loops, rm_index = self.rm_index, layout = self.layout_style, node_metric = self.node_metric, 
                      idx = self.idx, cluster_num = self.cluster_num, layer_labels=self.path_to_file, deg = self.degree,
                      edge_width = int(self.edge_thickness_var.get()), node_size = 2*int(self.node_thickness_var.get()), 
                      scale_edge_width = self.scale_edge_width, between_layer_edges = self.between_layer_edges, 
                      interframe = int(self.animation_speed_var.get()), node_labels = self.show_node_lb,
                      node_cmap = self.node_cmap, edge_cmap = self.edge_cmap)
        if self.show_colorbars:
            if self.scale_edge_width:
                f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=self.edge_cmap),
                           ax=a, label="Normalized edge value", shrink = 0.3,
                           location = 'right', pad = 0.1, fraction=0.05)
            if self.node_metric != "none" and self.node_cmap != "none":
                f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=self.node_cmap), ax=a,
                           label="Normalized metric value", shrink = 0.3,
                           fraction=0.05, location = 'left')
            else: # to keep layout consistent across changes of settings
                cb = f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=cm.Reds),
                                ax=a, label="Normalized metric value", shrink = 0.3,
                                fraction=0.05, location = 'left')
                cb.remove()
            
    def templayout_in_frame(self):
        if len(self.active_path_list) == 0:
            return
        for fm in self.content_frame.winfo_children():
            fm.destroy()
            root.update()
            
        # Show temporary "Loading..." label before plotting
        self.label = ttk.Label(self.content_frame, text="Rendering graph...", font = 'Helvetica 20 bold')
        self.label.place(relx=0.3, rely=0.2, relwidth=0.8, relheight=0.4)
        self.content_frame.update()
                
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        f = Figure(figsize=(950*px,500*px))
        a = f.add_subplot(111)

        plot_temporal_layout(self.path_to_file, a, percentage_threshold = self.percentage_threshold, mnn = self.mnn_number, mutual = self.mutual, \
                      avg_graph = self.view_type == "avg", affinity = self.edge_type == "affinity",  rm_fb_loops = self.remove_loops, \
                      layout = self.layout_style, node_metric = self.node_metric, rm_index = self.rm_index, \
                      idx = self.idx, cluster_num = self.cluster_num, layer_labels=self.path_to_file, deg = self.degree,
                      edge_width = int(self.edge_thickness_var.get()), node_size = int(self.node_thickness_var.get()), 
                      scale_edge_width = self.scale_edge_width, between_layer_edges = self.between_layer_edges,
                      node_labels = self.show_node_lb, show_planes = self.show_planes, edge_cmap = self.edge_cmap, 
                      node_cmap = self.node_cmap)
        if self.show_colorbars:
            f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=self.edge_cmap), ax=a, label="Normalized edge value", shrink = 0.3, location = 'right', pad = 0.1)
            if self.node_metric != "none" and self.node_cmap != "none":
                f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=self.node_cmap), ax=a, label="Normalized metric value", shrink = 0.3, location = 'left')
            else: # to keep layout consistent across changes of settings
                cb = f.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap=cm.Reds), ax=a, label="Normalized metric value", shrink = 0.3, location = 'left')
                cb.remove()
            
        f.subplots_adjust(left=0, bottom=0, right=0.948, top=1, wspace=0, hspace=0)

        canvas = FigureCanvasTkAgg(f, master=self.content_frame)
        NavigationToolbar2Tk(canvas, self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()#fill=tk.BOTH, expand=True, side="top") 
        self.label.destroy()
    
    def graphcut_param_window(self, event):
        """
        Prompt for selecting the parameter for graph cut, i.e. removal of edges.
        
        If 'threshold' is selected, a percentage has to be given as an input. This 
            percentage is scaled w.r.t to the strongest edge in the graph. Any edge with 
            a value below the input threshold (in % of strongest edge) will be removed.
        If 'mutual nearest neighbors' is selected, only the edges between nodes that are
            mutual nearest neighbors are preserved. The input value specifies the neighboring
            'degree', e.g. 1 means only 1st neighbors are preserved, 2 means 
            up to the 2nd nearest neighbors, 3 means up to the 3rd nearest neighbor etc.
        """
        if self.graphcut_selector.get() == "none":
            self.idx = [] # resets results of clustering as they will not be relevant after graph cut anymore
            self.percentage_threshold = 0.0
            self.mnn_number = None
            if self.display_type == "plot":
                self.plot_in_frame()
            elif self.display_type == "stats":
                self.stats_in_frame()
            elif self.display_type == "animation":
                self.animation_in_frame()
            return
        
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Enter Parameter Value")
        
        # center window
        self.new_window.geometry("200x100")
        self.new_window.update_idletasks()
        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_w = root.winfo_width()
        root_h = root.winfo_height()
        win_w = self.new_window.winfo_width()
        win_h = self.new_window.winfo_height()
        x = root_x + (root_w // 2 - win_w // 2)
        y = root_y + (root_h // 2 - win_h // 2)
        self.new_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        tk.Label(self.new_window, text="Enter " + self.graphcut_selector.get()).grid(row=0,column=0, padx = 15)
        self.graphcut_entry = tk.Entry(self.new_window)
        self.graphcut_entry.grid(row=1,column=0, padx = 15)
        if self.graphcut_selector.get() == "threshold":
            self.graphcut_entry.insert(0, str(self.percentage_threshold))
            tk.Label(self.new_window, text="%").grid(row=1,column=1)
        elif self.graphcut_selector.get() == "mutual nearest neighbors" or self.graphcut_selector.get() == "nearest neighbors":
            mnn = str(self.mnn_number) if self.mnn_number is not None else ""
            self.graphcut_entry.insert(0, mnn)
        tk.Button(self.new_window, text="Cut!", command=self.graph_cut_changed).grid(row=2,column=0, padx = 15)
        # tk.Label(self.new_window, text="Enter " + self.graphcut_selector.get()).grid(row=0,column=, padx = 70)
        self.graphcut_entry.bind("<Return>", lambda event: self.graph_cut_changed())

    def graph_cut_changed(self):
        self.idx = [] # resets results of clustering as they will not be relevant after graph cut anymore
        if self.graphcut_selector.get() == "threshold":
            self.mnn_number = None
            self.percentage_threshold = float(self.graphcut_entry.get())
        elif self.graphcut_selector.get() == "mutual nearest neighbors":
            self.percentage_threshold = 0.0
            self.mnn_number = int(self.graphcut_entry.get())
            self.mutual = True
        elif self.graphcut_selector.get() == "nearest neighbors":
            self.percentage_threshold = 0.0
            self.mnn_number = int(self.graphcut_entry.get())
            self.mutual = False
        self.node_metric = self.node_metric_selector.get()
        self.new_window.destroy()
        self.refresh_plot()
       
    def refresh_plot(self):
        if self.display_type == "plot":
            self.plot_in_frame()
        elif self.display_type == "stats":
            self.stats_in_frame()
        elif self.display_type == "animation":
            self.animation_in_frame()
        elif self.display_type == "temporal layout":
            self.templayout_in_frame()
            
    def plot_clicked(self):
        self.display_type = "plot"
        self.plot_in_frame()
        self.plot_btn.config(bg="#d1d1d1")
        self.stats_btn.config(bg="#f0f0f0")
        self.anim_btn.config(bg="#f0f0f0")
        self.tl_btn.config(bg="#f0f0f0")

    def stats_clicked(self):
        self.display_type = "stats"
        self.stats_in_frame()
        self.plot_btn.config(bg="#f0f0f0")
        self.stats_btn.config(bg="#d1d1d1")
        self.anim_btn.config(bg="#f0f0f0")
        self.tl_btn.config(bg="#f0f0f0")

    def animation_clicked(self):
        self.display_type = "animation"
        self.animation_in_frame()
        self.plot_btn.config(bg="#f0f0f0")
        self.stats_btn.config(bg="#f0f0f0")
        self.anim_btn.config(bg="#d1d1d1")
        self.tl_btn.config(bg="#f0f0f0")

    def templayout_clicked(self):
        self.display_type = "temporal layout"
        self.templayout_in_frame()
        self.plot_btn.config(bg="#f0f0f0")
        self.stats_btn.config(bg="#f0f0f0")
        self.anim_btn.config(bg="#f0f0f0")
        self.tl_btn.config(bg="#d1d1d1")

    # layout type changed
    def plot_changed(self, event):
        self.layout_style = self.plot_selector.get()
        self.refresh_plot()

    def rich_club_window(self):
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Degree value for rich-club")
        self.new_window.grab_set()

        self.new_window.geometry("200x100")
        self.new_window.update_idletasks()
        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_w = root.winfo_width()
        root_h = root.winfo_height()
        win_w = self.new_window.winfo_width()
        win_h = self.new_window.winfo_height()
        x = root_x + (root_w // 2 - win_w // 2)
        y = root_y + (root_h // 2 - win_h // 2)
        self.new_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        tk.Label(self.new_window, text="Enter degree:").pack(pady=(5, 2))
        self.rich_club_entry = tk.Entry(self.new_window)
        self.rich_club_entry.pack(pady=(2, 5))
        tk.Button(self.new_window, text="Compute rich-club!", command=self.rich_club_changed).pack(pady=(0, 3))
        self.rich_club_entry.bind("<Return>", lambda event: self.rich_club_changed())

    def k_core_window(self):
        self.new_window = tk.Toplevel(root)
        self.new_window.title("Degree value for k-core")
        
        self.new_window.geometry("200x100")
        self.new_window.update_idletasks()
        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_w = root.winfo_width()
        root_h = root.winfo_height()
        win_w = self.new_window.winfo_width()
        win_h = self.new_window.winfo_height()
        x = root_x + (root_w // 2 - win_w // 2)
        y = root_y + (root_h // 2 - win_h // 2)
        self.new_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        tk.Label(self.new_window, text="Enter degree").grid(row=0,column=0)
        self.kcore_entry = tk.Entry(self.new_window)
        self.kcore_entry.grid(row=1,column=0)
        tk.Button(self.new_window, text="Compute k-core!", command=self.rich_club_changed).grid(row=2,column=0)
        self.kcore_entry.bind("<Return>", lambda event: self.kcore_changed())

    def kcore_changed(self):
        self.degree = int(self.kcore_entry.get())
        self.new_window.destroy()
        self.refresh_plot()
    
    def rich_club_changed(self):
        self.degree = int(self.rich_club_entry.get())
        self.new_window.destroy()
        self.refresh_plot()
        
    def node_changed(self, event):
        self.node_metric = self.node_metric_selector.get()
        if self.node_metric == "rich-club":
            self.rich_club_window()
            return
            
        if self.node_metric == "k-core":
            self.k_core_window()
            return
            
        self.refresh_plot()


    def cluster_button_command(self):
        if len(self.active_path_list) == 0:
            return
        
        self.idx = community_clustering(self.path_to_file, algorithm = self.community_algorithm, mnn = self.mnn_number, 
                                        percentage_threshold=self.percentage_threshold, 
                                        mutual = self.mutual, affinity = self.edge_type == "affinity")
        self.cluster_num = max(self.idx)+1
        if self.display_type == "animation":
            self.animation_in_frame()
        else:
            self.plot_in_frame()
        

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
