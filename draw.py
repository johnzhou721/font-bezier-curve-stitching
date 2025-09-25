# PATCHED -- to correct text color handling caused by Tkinter handling Dark mode
# paper is always white so canvas background white still makes sense; however the
# text didn't have explicit color setting before.

# dictionary of points over here
points = # first line from output fill here

# put instructions here and replace the []
instructions = # second line from output fill here


import tkinter as tk
from canvasvg import saveall

points = {value: key for key, value in points.items()}
        
class StringArtHelpers:
    def zoom_in(self, event):
        canvas = self.canvas
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        factor = 1.1
        canvas.scale("all", x, y, factor, factor)

    def zoom_out(self, event):
        canvas = self.canvas
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        factor = 0.9
        canvas.scale("all", x, y, factor, factor)
    
    def __init__(self, root):
        self.root = root
        self.root.title("String Art")

        # Create a canvas widget
        self.canvas = tk.Canvas(self.root, width=3000, height=1200, bg='white')
        self.canvas.pack()
        canvas = self.canvas
        canvas.focus_set()
        #canvas.bind("<MouseWheel>", self.do_zoom) # WINDOWS ONLY
        canvas.bind('<ButtonPress-1>', lambda event: canvas.scan_mark(event.x, event.y))
        canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))
        canvas.bind("<Return>", self.zoom_in)
        canvas.bind("<BackSpace>", self.zoom_out)


    def transform(self, x, y):
        """Transform coordinates from FontForge into coordinates for Tkinter drawing"""
        return 1.5*x+50, 1000-1.5*y

    def draw_line(self, a, b, color='magenta'):
        x1, y1 = points[a]
        x2, y2 = points[b]
        # Draw the line on the canvas
        x1prime, y1prime = self.transform(x1, y1)
        x2prime, y2prime = self.transform(x2, y2)
        self.canvas.create_line(x1prime, y1prime, x2prime, y2prime, fill=color, width=0.05)

    def draw_point(self, pt, label="", size=10):
        xprime, yprime = self.transform(pt[0], pt[1])
        # x1, y1 = (xprime - 1), (yprime - 1)
        # x2, y2 = (xprime + 1), (yprime + 1)
        # self.canvas.create_oval(x1, y1, x2, y2, fill='yellow')
        self.canvas.create_text(xprime, yprime-1, text=label, font=("Verdana", size), fill="black")


if __name__ == "__main__":

    choice = int(input("1 to generate svg for printing dots, or 0 to do visualize >"))

    root = tk.Tk()

    helper = StringArtHelpers(root)
    if not choice:
        for instruction in instructions:
            if instruction != 'New':
                helper.draw_line(instruction[0], instruction[1])
    
    for key, value in points.items():
        if choice:
            helper.draw_point(value, label=key, size=3)
        else:
            helper.draw_point(value, label=key)
    
    if choice:
        saveall("output.svg", helper.canvas)
    else:
        root.mainloop()

