# abstraction for gui
# 1:1 grid dimensions only
from PIL import Image, ImageTk
import time
import tkinter

class GUI:
    def __init__(self, width, height, n):
        self.N = n

        self.side_length = min(width, height)

        self.window = tkinter.Tk()

        # canvas containing stuff
        # YES THE WIDTH AND HEIGHT IS PARTIALLY IGNORED UNTIL THIS IS CENTERED

        self.canvas = tkinter.Canvas(self.window, width=self.side_length, height=self.side_length, bg="#ffffff")
        self.canvas.grid(row=0, column=0, columnspan=5)
        #self.canvas.pack()
        
        # this is the actual grid
        self.grid_images = [] 

        # NOTE: we need to keep a reference to the image, or else it will not render because it gets garbage collected
        #       wtf
        # https://web.archive.org/web/20201111190625id_/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
        self.image_for_tk = tkinter.PhotoImage()
        
        # add image to canvas
        self.canvas_image = self.canvas.create_image(0, 0, image=self.image_for_tk, anchor='nw')

        # ROW 1
        # add buttons beside scale
        self.fastprev_button = tkinter.Button(self.window, text='<<', command=lambda : self._on_click_scale_button(-10))
        self.fastprev_button.grid(row=1, column=0)

        self.prev_button = tkinter.Button(self.window, text='<', command=lambda : self._on_click_scale_button(-1))
        self.prev_button.grid(row=1, column=1)
        #self.prev_button.pack()
        

        # add scale
        self.scale = tkinter.Scale(self.window, to=0, orient=tkinter.HORIZONTAL, command=self._on_scale_update)
        self.scale.grid(row=1, column=2)
        #self.scale.pack()

        self.next_button = tkinter.Button(self.window, text='>', command=lambda : self._on_click_scale_button(+1))
        self.next_button.grid(row=1, column=3)

        self.fastnext_button = tkinter.Button(self.window, text='>>', command=lambda : self._on_click_scale_button(+10))
        self.fastnext_button.grid(row=1, column=4)

        self.explored_count = tkinter.Label(self.window)
        self.explored_count.grid(row=2, column=0, columnspan=5)
        self.set_explored_count(0)

        # from mazebot.py
        remap = {
            'Empty Space': '#FFF',
            'Wall': '#000',
            'Current Maze Path': '#F00',
            'All Tiles Explored by the Algorithm': '#0F0',
            
            'Starting Tile': '#00F',
            'Target Tile': '#F0F'
        }

        # Add legend
        # sticky='w' left-aligns text
        self.legend_title = tkinter.Label(self.window, text="\nLegend")
        self.legend_title.grid(row=3, column=0, columnspan=5)

        self.legend_color = []
        self.legend_text = []
        for idx, kv in enumerate(remap.items()):
            text, color = kv
            self.legend_color.append(tkinter.Label(self.window, text=' ' * 8, bg=color))
            self.legend_color[-1].grid(row=4 + idx, column=1, columnspan=1, sticky='w')

            self.legend_text.append(tkinter.Label(self.window, text=text))
            self.legend_text[-1].grid(row=4 + idx, column=2, columnspan=3, sticky='w')

        # HACK: bottom padding so it won't look weird
        self.bottom_padding = tkinter.Label(self.window)
        self.bottom_padding.grid(row=4 + len(self.legend_text) + 1, column=0)

    def test(self):
        i = 0

        for _ in range(1000): 
            self.next_frame()
            for x in range(self.N):
                for y in range(self.N):
                    if (x + y) % 3 == 0:
                        self.set_tile_color((x, y), (i, 0, 0))
                    elif (x + y) % 3 == 1:
                        self.set_tile_color((x, y), (0, i, 0))
                    elif (x + y) % 3 == 2:
                        self.set_tile_color((x, y), (0, 0, i))

            i = (i + 1) % 255
        
        # call this to make the window display an image at the start
        self.update_window()
    
    def next_frame(self):
        new_image = Image.new('RGBA', (self.N, self.N), (0, 0, 0))
        new_image.putalpha(255)
        self.grid_images.append(new_image)

        self.scale.configure(to=len(self.grid_images)-1)
    
    def set_tile_color(self, coords, color):
        if len(self.grid_images) > 0:
            self.grid_images[-1].putpixel(coords, color)

    def set_explored_count(self, explored_count):
        self.explored_count.configure(text=f'Explored tiles: {explored_count}')

    def _on_click_scale_button(self, factor):
        updated_scale_val = int(self.scale.get()) + factor

        if 0 <= updated_scale_val < len(self.grid_images):
            self.scale.set(updated_scale_val)
            self.update_window()

    def _on_scale_update(self, new_idx):
        self.update_window()

    def update_window(self):
        current_image_idx = self.scale.get()

        if 0 <= current_image_idx < len(self.grid_images):
            # scale grid to fit window
            # nearest neighbor scaling preserves the sharpness of pixel art
            original_image = self.grid_images[current_image_idx]
            resized_image = original_image.resize((self.side_length, self.side_length), Image.NEAREST)
            
            # update image
            self.image_for_tk = ImageTk.PhotoImage(resized_image)
            
            # replace image in the canvas
            self.canvas.itemconfig(self.canvas_image, image=self.image_for_tk)

            # redraw
            self.window.update()

    def keep_running(self):
        tkinter.mainloop()

if __name__ == '__main__':
    gui = GUI(640, 480, 10)

    gui.test()

    tkinter.mainloop()

