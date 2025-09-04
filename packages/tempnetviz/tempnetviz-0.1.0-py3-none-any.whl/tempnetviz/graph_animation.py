import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import igraph as ig
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
import numpy as np
import matplotlib as mpl
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphAnimator:
    def __init__(self, graphs, layout, styles, parent_frame = None, interframe_time = 200):
        self.graphs = graphs
        self.layout = layout
        self.styles = styles # store all the layout information, node sizes, edges width etc...
        self.is_playing = False
        self.animation = None
        self.interframe = interframe_time
        self.current_frame = 0
        if parent_frame is None:
            self.root = tk.Tk()
            self.root.resizable(width=True, height=True)
            self.root.title("Multilayer graph analysis")
            self.parent_frame = tk.Frame(self.root)
            self.root.mainloop()

        else:
            self.parent_frame = parent_frame
        self.setup_ui()
        self.play_animation()
    
    def get_fig(self):
        return self.fig, self.ax
        
    def setup_ui(self):
        """Set up the matplotlib figure and widgets"""
        # make figure
        plt.ioff()
        # px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        self.fig = Figure(dpi = 100)
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)   
            
        # Animation frame 
        self.anim_frame = tk.Frame(self.parent_frame)
        self.anim_frame.place(relx= 0.0, rely = 0.0, relwidth=1, relheight=0.90)
        
        # make canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.anim_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # control frame to put widgets in
        self.control_frame = tk.Frame(self.parent_frame)
        self.control_frame.place(relx= 0.1, rely = 0.92, relwidth=0.7, relheight=0.10)

        # Create slider
        slider_label = tk.Label(self.control_frame, text="Frame:")
        slider_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.slider = tk.Scale(self.control_frame, from_=0, to=len(self.graphs)-1, 
            orient=tk.HORIZONTAL,length=400, command=self.update_slider)
        self.slider.bind('<ButtonPress-1>', self.stop_animation_on_slider_click)
        self.slider.bind('<B1-Motion>', self.stop_animation_on_slider_click)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Create buttons
        self.button_frame = tk.Frame(self.parent_frame)
        self.button_frame.place(relx= 0.8, rely = 0.92, relwidth=0.2, relheight=0.10)
        self.play_button = tk.Button(self.button_frame, text=" Play ", command=self.play_animation)
        self.play_button.pack(side=tk.LEFT, padx=10)
        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_animation)
        self.pause_button.pack(side=tk.LEFT, padx=10)
        
        self.precompute_plots()
        
        self.img_obj = self.ax.imshow(self.frame_images[0])
        self.update_plot(0)
        self.play_animation
        self.canvas.draw()
        
    def precompute_plots(self):
        plt.ioff()
        self.frame_images = []
        # temp label that shows progress of pre-computation
        self.precompute_label = ttk.Label(self.anim_frame, text=f" Rendering frames (0 from {len(self.graphs)-1}) ", font = 'Helvetica 20 bold')
        self.precompute_label.place(relx=0.3, rely=0.17, relwidth=0.44, relheight=0.28)
        for idx, g in enumerate(self.graphs):
            self.precompute_label.config(text = f" Rendering frames ({idx} from {len(self.graphs)-1}) ")
            self.parent_frame.update_idletasks()
            fig_tmp, ax_tmp = plt.subplots()
            ig.plot(g, target=ax_tmp, layout = self.layout.coords, **self.styles[idx])
            ax_tmp.axis('off')
            fig_tmp.canvas.draw()
            buf = fig_tmp.canvas.buffer_rgba()  # memoryview
            img = np.asarray(buf)  # Convert to NumPy array (H x W x 4)
            self.frame_images.append(img)
            self.parent_frame.update()
            plt.close(fig_tmp)
            
        self.precompute_label.destroy()
        self.parent_frame.update()
            
    def stop_animation_on_slider_click(self, event):
        """Stop the animation when the slider is clicked"""
        if self.is_playing and self.animation and getattr(self.animation, "event_source", None):
            self.animation.event_source.stop()
        self.is_playing = False
           
    def update_plot(self, frame_idx):
        """Update the plot with the graph at the given frame index"""
        self.img_obj.set_data(self.frame_images[frame_idx])
        self.canvas.draw()
        self.slider.set(frame_idx)
        self.current_frame = frame_idx
    
    def update_slider(self, val):
        """Handle slider changes"""
        if not self.is_playing:
            frame_idx = int(float(val))
            self.update_plot(frame_idx)
    
    def play_animation(self):
        """Start animation playback"""
        if self.is_playing: return
        self.is_playing = True

        def animate(frame):
            if not self.is_playing: 
                return []
            self.update_plot(frame)
            return [self.img_obj]

        self.animation = FuncAnimation(
            self.fig, animate, frames=len(self.frame_images),
            interval=self.interframe, blit=True, repeat=True
        )
        self.canvas.draw()
    
    def pause_animation(self):
        """Pause animation playback"""
        if self.is_playing and self.animation and getattr(self.animation, "event_source", None):
            self.animation.event_source.stop()
            self.is_playing = False
    

 