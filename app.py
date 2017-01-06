from tkinter import *
from tkinter import filedialog
import PIL.Image as Image
import PIL.ImageTk as ImageTk

class CanvasImage:

    FILETYPES = (('PNG', '*.png'),\
                 ('JPEG', '*.jpg'))
    MAX_WIDTH = 800
    MAX_HEIGHT = 600
    MAX_SIZE = MAX_WIDTH, MAX_HEIGHT
    PLACEHOLDER = "placeholder.png"
    SCALE = 256

    def __init__(self, canvas):
        self.canvas = canvas
        self.path = self.PLACEHOLDER
        self.image = self.get_image(self.path)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_on_canvas = self.canvas.create_image(self.MAX_WIDTH / 2, 
                                                        self.MAX_HEIGHT / 2,
                                                        image = self.tk_image)

    def get_image(self, path):
        image = Image.open(path)
        image.thumbnail(self.MAX_SIZE, Image.ANTIALIAS)
        return image

    def configure(self, image):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfigure(self.image_on_canvas, image = self.tk_image)

    def load(self):
        self.path = filedialog.askopenfilename(filetypes = self.FILETYPES)
        self.image = self.get_image(self.path)
        self.configure(self.image)

    # Returns an array of zeroes with length of SCALE
    def empty_histogram(self):
        return [0 for _ in range(self.SCALE)]

    # Probability mass function
    def pmf(self, histogram):
        total = sum(histogram)
        return [pixel / total for pixel in histogram]
    
    # Cumulative distributive function
    def cdf(self, histogram):
        pmf = self.pmf(histogram)
        for i in range(1, len(pmf)):
            pmf[i] += pmf[i - 1]
        return pmf

    def equalize(self):
        # YCbCr color space provides luminosity information
        self.image = self.image.convert("YCbCr")

        hist = self.empty_histogram()

        # Calculate histogram for image
        pixels = self.image.load()
        for i in range(self.image.size[0]):
            for j in range(self.image.size[1]):
                y, cb, cr = self.image.getpixel((i, j))
                hist[y] += 1

        cdf = self.cdf(hist) 

        # Apply equalized values to image
        for i in range(self.image.size[0]):
            for j in range (self.image.size[1]):
                y, cb, cr = self.image.getpixel((i, j))
                y = int(cdf[y] * (self.SCALE - 1))
                pixels[i, j] = (y, cb, cr)

        self.image = self.image.convert("RGB")
        self.configure(self.image)

    def save(self):
        if self.path:
            self.image.save(fp = self.path)

    def save_as(self):
        save_path = filedialog.asksaveasfilename(filetypes = self.FILETYPES)
        if save_path:
            self.image.save(fp = save_path)

window = Tk()
window.wm_title("Image processor")

canvas = Canvas(window, width = CanvasImage.MAX_WIDTH, height = CanvasImage.MAX_HEIGHT)
canvas.grid(row = 0, column = 0, columnspan = 4)

canvas_image = CanvasImage(canvas)

open_button = Button(window, text = "Open an image", command = canvas_image.load)
open_button.grid(row = 1, column = 0, sticky = "WE")

equalize_button = Button(window, text = "Equalize histogram", command = canvas_image.equalize)
equalize_button.grid(row = 1, column = 1, sticky = "WE")

save_button = Button(window, text = "Save", command = canvas_image.save)
save_button.grid(row = 1, column = 2, sticky = "WE")

save_as_button = Button(window, text = "Save as", command = canvas_image.save_as)
save_as_button.grid(row = 1, column = 3, sticky = "WE")

window.mainloop()
