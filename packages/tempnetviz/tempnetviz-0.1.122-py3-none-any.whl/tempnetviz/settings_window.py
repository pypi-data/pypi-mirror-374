import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import filedialog
from .tooltip import ToolTip
import matplotlib

class settingsWindow(tk.Toplevel):
    """
    Opens a window showing the current settings (edge type, multilayer view and stats type),
        to allow user to change them.
    """    
    def __init__(self, root, app):
        super().__init__(root)
        self.root = root
        self.app = app
        self.title("Settings")
        self.geometry("400x320")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.tabControl = ttk.Notebook(self)

        tab1 = ttk.Frame(self.tabControl)
        tab2 = ttk.Frame(self.tabControl)
        tab3 = ttk.Frame(self.tabControl)
        tab4 = ttk.Frame(self.tabControl)
        
        self.tabControl.add(tab1, text ='General')
        self.tabControl.add(tab2, text ='Graph Plot')
        self.tabControl.add(tab3, text ='Histogram')
        self.tabControl.add(tab4, text ='Animation')
        self.tabControl.pack(expand = 1, fill ="both")
        
        self.edge_type_var = tk.IntVar(value = 1) # variable for changing affinity/distance in settings window
        self.view_var = tk.IntVar(value = 1)      # variable for changing view from 3D to average in settings window
        self.histo_type_var = tk.IntVar(value = 1) # variable for side by side or stacked histogram
        self.loops_var = tk.IntVar(value = 1)     # variable for the removal of feedback loops in graph display
        self.rm_index_var = tk.IntVar(value = 1)     # variable for the removal of index row in input data file: sometimes dataframe have row and columns names 
        self.show_node_lb_var = tk.IntVar(value = 1)     # variable for the displaying the name of the nodes in the graphs

## 1st tab: generic settings
        rm_index_label = tk.Label(tab1, text="Remove index row in input: ")
        rm_index_label.grid(row = 1, column = 1)
        rm_index_button = tk.Checkbutton(tab1, text="", variable = self.rm_index_var, onvalue = 1, offvalue = 0, command = self.rm_index_button_clicked)
        if self.app.rm_index:
            rm_index_button.select()
        rm_index_button.grid(row = 1, column = 2)
        tp_index1 = ToolTip(rm_index_label, "If clicked, the first row and column of input file\nwill be considered to contain indexing information\nlike node names or node indices\nand will be removed from plotting.")
        tp_index2 = ToolTip(rm_index_button, "If clicked, the first row and column of input file\nwill be considered to contain indexing information\nlike node names or node indices\nand will be removed from plotting.")

        show_node_lb_label = tk.Label(tab1, text="Show node labels: ")
        show_node_lb_label.grid(row = 2, column = 1)
        show_node_lb_button = tk.Checkbutton(tab1, text="", variable = self.show_node_lb_var, onvalue = 1, offvalue = 0, command = self.show_node_lb_button_clicked)
        if self.app.show_node_lb:
            show_node_lb_button.select()
        show_node_lb_button.grid(row = 2, column = 2)
        tp_lb1 = ToolTip(show_node_lb_label, "Whether or not to display node labels (i.e. names).\nworks only if input data contains an index row.")
        tp_lb2 = ToolTip(show_node_lb_button, "Whether or not to display node labels (i.e. names).\nworks only if input data contains an index row.")

        edge_label = tk.Label(tab1, text="Edge type")
        edge_label.grid(row = 3, column = 1)
        dist_button = tk.Radiobutton(tab1, text="Distance", variable = self.edge_type_var, value = 2, command = self.switch_edge_type)
        dist_button.grid(row = 3, column = 2)    
        aff_button = tk.Radiobutton(tab1, text="Affinity", variable = self.edge_type_var, value = 1, command = self.switch_edge_type)
        aff_button.grid(row = 3, column = 3)
        # need to remove event listeners from radiobutton: they get triggered by hovering otherwise
        dist_button.bind('<Enter>', lambda e: None)
        dist_button.bind('<Leave>', lambda e: None)       
        aff_button.bind('<Enter>', lambda e: None)
        aff_button.bind('<Leave>', lambda e: None)
        tp_edgetype1 = ToolTip(edge_label, "Does the data in the input file represent distance between the nodes (i.e. how 'far appart' they are)\ or how affine they are (i.e. how strongly connected?).")
        tp_edgetype2 = ToolTip(dist_button, "Does the data in the input file represent distance between the nodes (i.e. how 'far appart' they are)\ or how affine they are (i.e. how strongly connected?).")
        tp_edgetype3 = ToolTip(aff_button, "Does the data in the input file represent distance between the nodes (i.e. how 'far appart' they are)\ or how affine they are (i.e. how strongly connected?).")

        community_algo_label = tk.Label(tab1, text = "Community detection algorithm: ")
        community_algo_label.grid(row = 4, column = 1)
        algo_values = ["louvain", "walktrap", "infomap", "modularity"]
        self.community_algo_selector=ttk.Combobox(tab1, values = algo_values, state = "readonly")
        self.community_algo_selector.grid(row = 4, column = 2)
        self.community_algo_selector.set(self.app.community_algorithm)
        self.community_algo_selector.bind('<<ComboboxSelected>>', self.algo_changed)
        
        fbloop_label = tk.Label(tab1, text="Remove feedback loops in plots: ")
        fbloop_label.grid(row = 5, column = 1)
        fb_loop_button = tk.Checkbutton(tab1, text="", variable = self.loops_var, onvalue = 1, offvalue = 0, command = self.loops_button_clicked)
        if self.loops_var.get() == 1:
            fb_loop_button.select()
        fb_loop_button.grid(row = 5, column = 2)
        tp_fb1 = ToolTip(fbloop_label, "Does the data contain feedback loop? I.e. self-interacting nodes?\nWhen this is clicked, feedback loops are removed.")
        tp_fb2 = ToolTip(fb_loop_button, "Does the data contain feedback loop? I.e. self-interacting nodes?\nWhen this is clicked, feedback loops are removed.")

        scale_edge_label = tk.Label(tab1, text="Scale edge width: ")
        scale_edge_label.grid(row = 6, column = 1)
        scale_edge_button = tk.Checkbutton(tab1, text="", command = self.scale_edge_clicked)
        if self.app.scale_edge_width:
            scale_edge_button.select()
        scale_edge_button.grid(row = 6, column = 2)
        tp_scale_edge1 = ToolTip(scale_edge_label, "If seleceted, the width of the edges in the graph(s)\nwill be displayed proportionally to their corresponding weight.")
        tp_scale_edge2 = ToolTip(scale_edge_button, "If seleceted, the width of the edges in the graph(s)\nwill be displayed proportionally to their corresponding weight.")

        tk.Label(tab1, text="Edge thickness:").grid(row=7, column=1)
        self.edge_thickness_var = tk.StringVar() 
        self.edge_thickness_entry = tk.Entry(tab1, textvariable=self.edge_thickness_var)
        self.edge_thickness_entry.insert(0, self.app.edge_thickness_var.get())
        self.edge_thickness_entry.bind('<Return>', lambda event: self.on_enter_pressed(event))
        self.edge_thickness_entry.grid(row=7, column=2)
        
        tk.Label(tab1, text="Node thickness:").grid(row=8, column=1)
        self.node_thickness_var = tk.StringVar() 
        self.node_thickness_entry = tk.Entry(tab1, textvariable=self.node_thickness_var)
        self.node_thickness_entry.insert(0, self.app.node_thickness_var.get())
        self.node_thickness_entry.bind('<Return>', lambda event: self.on_enter_pressed(event))
        self.node_thickness_entry.grid(row=8, column=2)
        
        node_cmaps_val = ["Greys", "Reds", "Greens", "Blues", "cool", "coolwarm", "viridis", "none"]
        node_cmap_label = tk.Label(tab1, text = "Colormap for node metrics: ")
        node_cmap_label.grid(row = 9, column = 1)
        self.node_cmap_selector=ttk.Combobox(tab1, values = node_cmaps_val, state = "readonly")
        self.node_cmap_selector.grid(row = 9, column = 2)
        if self.app.node_cmap != "none":
            self.node_cmap_selector.set(self.app.node_cmap.name)
        else:
            self.node_cmap_selector.set("none")
        self.node_cmap_selector.bind('<<ComboboxSelected>>', self.node_cmap_changed)
        
        edge_cmaps_val = ["Greys", "Reds", "Greens", "Blues", "cool", "coolwarm", "viridis"]
        edge_cmap_label = tk.Label(tab1, text = "Colormap for edge values: ")
        edge_cmap_label.grid(row = 10, column = 1)
        self.edge_cmap_selector=ttk.Combobox(tab1, values = edge_cmaps_val, state = "readonly")
        self.edge_cmap_selector.grid(row = 10, column = 2)
        self.edge_cmap_selector.set(self.app.edge_cmap.name)
        self.edge_cmap_selector.bind('<<ComboboxSelected>>', self.edge_cmap_changed)
        
        cb_label = tk.Label(tab1, text="Show colorbars: ")
        cb_label.grid(row = 11, column = 1)
        cb_button = tk.Checkbutton(tab1, text="", command = self.cb_button_clicked)
        if self.app.show_colorbars:
            cb_button.select()
        cb_button.grid(row = 11, column = 2)
        tp_cb1 = ToolTip(scale_edge_label, "If seleceted, colorbars will indicates the values associated with the colormap.")
        tp_cb2 = ToolTip(scale_edge_button, "If seleceted, colorbars will indicates the values associated with the colormap.")

        # necessary because of tkinter foul handling of radiobuttons. Values do not get set properly, events get triggered when they shouldn't...
        if self.app.edge_type == "distance":
            original_command = dist_button.cget('command')
            dist_button.config(command=lambda: None)
            dist_button.invoke()
            dist_button.config(command=original_command)
        
## Second tab: 3D plot options
        multilayer_label = tk.Label(tab2, text="Multilayer display")
        multilayer_label.grid(row = 1, column = 1)
        avg_button = tk.Radiobutton(tab2, text="Average", variable = self.view_var, value = 2, command = self.switch_view_type)
        avg_button.grid(row = 1, column = 2)
        multilayer_button = tk.Radiobutton(tab2, text="3D", variable = self.view_var, value = 1, command = self.switch_view_type)
        multilayer_button.grid(row = 1, column = 3)
        # need to remove event listeners from radiobutton: they get triggered by hovering otherwise
        avg_button.bind('<Enter>', lambda e: None)
        avg_button.bind('<Leave>', lambda e: None)       
        multilayer_button.bind('<Enter>', lambda e: None)
        multilayer_button.bind('<Leave>', lambda e: None)
        
        # necessary because of tkinter foul handling of radiobuttons. Values do not get set properly, events get triggered when they shouldn't...
        if self.app.view_type == "avg":
            original_command = avg_button.cget('command')
            avg_button.config(command=lambda: None)
            avg_button.invoke()
            avg_button.config(command=original_command)
            
        show_planes_label = tk.Label(tab2, text="Show planes: ")
        show_planes_label.grid(row = 2, column = 1)
        show_planes_button = tk.Checkbutton(tab2, text="", command = self.show_planes_button_clicked)
        if self.app.show_planes:
            show_planes_button.select()
        show_planes_button.grid(row = 2, column = 2)

## 3rd tab: histogram options
        multilayer_label = tk.Label(tab3, text="Histogram type")
        multilayer_label.grid(row = 1, column = 1)
        sbs_button = tk.Radiobutton(tab3, text="Side-by-side", variable = self.histo_type_var, value = 1, command = self.switch_histo_type)
        sbs_button.grid(row = 1, column = 2)
        stacked_button = tk.Radiobutton(tab3, text="Stacked", variable = self.histo_type_var, value = 2, command = self.switch_histo_type)
        stacked_button.grid(row = 1, column = 3)
        # need to remove event listeners from radiobutton: they get triggered by hovering otherwise
        sbs_button.bind('<Enter>', lambda e: None)
        sbs_button.bind('<Leave>', lambda e: None)       
        stacked_button.bind('<Enter>', lambda e: None)
        stacked_button.bind('<Leave>', lambda e: None)
        
        show_legend_label = tk.Label(tab3, text="Show legend: ")
        show_legend_label.grid(row = 2, column = 1)
        show_legend_button = tk.Checkbutton(tab3, text="", command = self.show_legend_clicked)
        if self.app.show_histogram_legend:
            show_legend_button.select()
        show_legend_button.grid(row = 2, column = 2)
                    
        # necessary because of tkinter foul handling of radiobuttons. Values do not get set properly, events get triggered when they shouldn't...
        if self.app.histo_type == "side-by-side":
            original_command = sbs_button.cget('command')
            sbs_button.config(command=lambda: None)
            sbs_button.invoke()
            sbs_button.config(command=original_command)
            
        tk.Label(tab3, text="Number of bins:").grid(row=3, column=1)
        self.bins_var = tk.StringVar() 
        self.bins_entry = tk.Entry(tab3, textvariable=self.bins_var)
        self.bins_entry.insert(0, self.app.num_bins)
        self.bins_entry.bind('<Return>', lambda event: self.on_enter_pressed_hist(event))
        self.bins_entry.grid(row=3, column=2)

## 4th tab: animation options   
        tk.Label(tab4, text="Time between frames (ms):").grid(row=1, column=1)
        self.animation_speed_var = tk.StringVar() 
        self.animation_speed_entry = tk.Entry(tab4, textvariable=self.animation_speed_var)
        self.animation_speed_entry.insert(0, self.app.animation_speed_var.get())
        self.animation_speed_entry.bind('<Return>', lambda event: self.on_enter_pressed(event))
        self.animation_speed_entry.grid(row=1, column=2)
        
        between_layer_label = tk.Label(tab2, text="Draw edges between layers: ")
        between_layer_label.grid(row = 8, column = 1)
        between_layer_button = tk.Checkbutton(tab2, text="", command = self.between_layer_clicked)
        if self.app.between_layer_edges:
            between_layer_button.select()
        between_layer_button.grid(row = 8, column = 2)
        
## Callbacks
    def redraw(self):
        if self.app.display_type == "plot":
            self.app.plot_in_frame()
        elif self.app.display_type == "stats":
            self.app.stats_in_frame()
        elif self.app.display_type == "animation":
            self.app.animation_in_frame()
        elif self.app.display_type == "temporal layout":
            self.app.templayout_in_frame()

    def on_enter_pressed(self, event):
        edge_thickness_value = self.edge_thickness_entry.get()  
        node_thickness_value = self.node_thickness_entry.get() 
        animation_speed_value = self.animation_speed_entry.get()
        self.app.edge_thickness_var.set(edge_thickness_value)
        self.app.node_thickness_var.set(node_thickness_value)
        self.app.animation_speed_var.set(animation_speed_value)
        self.redraw()
        
    def cb_button_clicked(self):
        self.app.show_colorbars = not self.app.show_colorbars
        self.redraw()
        
    def on_enter_pressed_hist(self, event):
        bins_value = self.bins_entry.get()  
        self.app.num_bins = int(bins_value)
        self.redraw()
        
    def switch_edge_type(self):
        if self.app.edge_type == "affinity":
            self.app.edge_type = "distance"
            self.redraw()
            return
        else:
            self.app.edge_type = "affinity"
            self.redraw()
            return
        
    def algo_changed(self, event):
        self.app.community_algorithm = self.community_algo_selector.get()
        self.app.cluster_button_command()
        
    def node_cmap_changed(self, event):
        if self.node_cmap_selector.get() != "none":    
            self.app.node_cmap = matplotlib.colormaps.get_cmap(self.node_cmap_selector.get())
        else:
            self.app.node_cmap = "none"
        self.redraw()        

    def edge_cmap_changed(self, event):
        self.app.edge_cmap = matplotlib.colormaps.get_cmap(self.edge_cmap_selector.get())
        self.redraw()    


    def switch_view_type(self):
        if self.app.view_type == "3D":
            self.app.view_type = "avg"
            self.redraw()
            return
        else:
            self.app.view_type = "3D"
            self.redraw()
            return

    def switch_histo_type(self):
        if self.app.histo_type == "stacked":
            self.app.histo_type = "side-by-side"
            self.redraw()
            return
        else:
            self.app.histo_type = "stacked"
            self.redraw()
            return
        
    def show_planes_button_clicked(self):
        self.app.show_planes = not self.app.show_planes
        self.redraw()

    def loops_button_clicked(self):
        self.app.remove_loops = not self.app.remove_loops
        self.redraw()
        
    def show_node_lb_button_clicked(self):
        self.app.show_node_lb = not self.app.show_node_lb
        self.redraw()
        
    def rm_index_button_clicked(self):
        self.app.rm_index = not self.app.rm_index
        if not self.app.rm_index: # if indexing row and column are not removed, then there is no labels to be loaded
            self.app.show_node_lb = False 
        self.redraw()

    def scale_edge_clicked(self):
        self.app.scale_edge_width = not self.app.scale_edge_width
        self.redraw()

    def show_legend_clicked(self):
        self.app.show_histogram_legend = not self.app.show_histogram_legend
        self.redraw()

    def between_layer_clicked(self):
        self.app.between_layer_edges = not self.app.between_layer_edges
        self.redraw()
        
    def on_close(self):
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    t = settingsWindow(root, None)
    root.mainloop()