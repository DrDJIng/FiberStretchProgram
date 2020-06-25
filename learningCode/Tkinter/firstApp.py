from tkinter import * # Imports tkinter, defaults to Tk
from tkinter import ttk # Imports new widgets. Call functions as ttk.function()

# Define calculation function for use later in script.
def calculate(*args):
    try:
        value = float(feet.get())
        meters.set((0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass

root = Tk() # Create the root Window
root.title("Feet to Meters") # Set title of the window
mainframe = ttk.Frame(root, padding = "3 3 12 12") # Create the main frame widget, and attach it to the root window.
mainframe.grid(column = 0, row = 0, sticky = (N, W, E, S)) # Makes an empty space, sticky tells us where the anchors are.
root.columnconfigure(0, weight = 1) # Configure column 0
root.rowconfigure(0, weight = 1) # Configure row 0

feet = StringVar() # Initiatlise variable
meters = StringVar() # Initiatlise variable
feet_entry = ttk.Entry(mainframe, width = 7, textvariable = feet) # Create editable widget
feet_entry.grid(column = 2, row = 1, sticky = (W, E)) # Puts widget in column 2, first row.
ttk.Label(mainframe, textvariable = meters).grid(column = 2, row = 2, sticky = (W, E)) # Creates a label for meters, puts it below feet label.
ttk.Button(mainframe, text = "Calculate", command = calculate).grid(column = 3, row = 3, sticky = W) # Makes a button, puts it in bottom right.

ttk.Label(mainframe, text = 'feet').grid(column = 3, row = 1, sticky = W) # Make and place label
ttk.Label(mainframe, text = 'is equivalent to').grid(column = 1, row = 2, sticky = E) # Make and place label
ttk.Label(mainframe, text = 'meters').grid(column = 3, row = 2, sticky = W) # Make and place label

for child in mainframe.winfo_children(): child.grid_configure(padx = 5, pady = 5) # For every child of mainframe, pad with 5 pixels
feet_entry.focus() # Set focus on open to the editable text field
root.bind('<Return>', calculate) # Make it so pressing "Enter" calculates the conversion.

root.mainloop() # Tell Tk to enter its event loop, which runs everything.
