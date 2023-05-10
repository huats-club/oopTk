# Anatomy of a GUI main.py code
# letting GUI be the main show actor

import tkinter as tk
import multiprocessing
import time

# An example of a long, blocking operation to be threaded inside GUI
def decrement(start_num, pipe_out):
    while start_num > 0:
        start_num = start_num -1
        #print(start_num)
        pipe_out.send(start_num)
        time.sleep(0.5) #seconds
    pipe_out.send(0)

# Window class inherits from "tk.Frame" class
# this is means Window class has all the functionality of tk.Frame
# i.e. owns the public/protected methods of tk.Frame, behaves like it
# and can own extra behaviors on top of it/augment the existing methods (by override the methods)
class Window(tk.Frame):
    def __init__(self, root):
        self.root = root

        # Add label greeting
        self.label = tk.Label(text="Hello")
        self.label.pack()

        # Add button
        self.button = tk.Button(text="Click me", command=self.do_countdown)
        self.button.pack()

        # Add label to show count down numbers
        self.countdown_var = tk.StringVar()
        self.countdown_label = tk.Label(textvariable=self.countdown_var)
        self.countdown_label.pack()

        # Declare variable upfront to prevent confusion
        # self-discipline
        self.countdown_thread = None

    # Prepare the countdown mechanism
    def do_countdown(self):
        # Create a pipe, first "gui_pipe" to be kept as attribute to receive data
        # second pipe "process_pipe" to be passed as object to long running function in process
        # to pass data to the "gui_pipe"
        self.gui_pipe, process_pipe = multiprocessing.Pipe()
        self.countdown_thread = multiprocessing.Process(target=decrement, args=(10, process_pipe,))
        self.countdown_thread.start()

        # Using Tkinter's own timer event to update the screen
        # every 100 ms
        self.parent.after(100, self.update)

    # Poll for incoming numbers from the decrement thread
    # and update the GUI
    def update(self):
        if self.gui_pipe.poll(1):
            num = self.gui_pipe.recv()
            if num == 0:
                # Handle the threading clean up, but joining and ending the thread lifetime
                self.countdown_thread.join()

                # UIUX, show user that process has ended
                self.countdown_var.set("End!")
                self.root.after(1000, self.clear_countdown_label)
            else: 
                # Received a valid number that is positive
                # and set to the GUI lavel to view
                self.countdown_var.set(f"{num}")

                # Calling this method again, after 100ms
                # to update the next number received from the pipe
                self.root.after(100, self.update)

    # Remove the last number in the countdown label
    # after countdown has completed
    # by replacing with a space
    def clear_countdown_label(self):
        self.countdown_var.set("")
        # We don't need to call this method again using the tkinter events
        # Because it has ended and no need to show anymore changes

    # Clean up actions to be done when "X" is clicked on the application
    def on_close(self):
        if self.countdown_thread != None and self.countdown_thread.is_alive():
            # You may encounter EOFError if you don't handle the exception
            # where you read a pipe that is closed forcefully in your above update() calls
            # Not handling here to prevent code complexity due to error handling
            self.countdown_thread.kill() 

        # Destroy the tkinter object
        self.root.destroy()

if __name__ == "__main__":
    # Creating the Tk object to "contain" all of our widgets
    root = tk.Tk()

    # Creating "Window" class, which will be embedded inside "root" Tk object
    # This can be seen as (1) "Window" class embedded in the GUI areas of "root" 
    # (2) Root is its parent
    # Comment out this object creation to see that there is no Window class in "root"
    # Note: The mainApp reference may not be useful already in OOP, as there is no need to do mainApp.getData()
    # As inside the methods, you can already invoke the methods, as seen in button example embedded in GUI
    # where methods of Window class are invokved internally with "self." keywords
    mainApp = Window(root)

    # This is one example of using the object returned
    # to invoke a method from  outside
    root.protocol("WM_DELETE_WINDOW", mainApp.on_close)

    # Let "root" Tk object's thread continue until program ends
    root.mainloop()

    ## WARNING: No code here can be executed here until 
    ## tkinter window closes
    ## As GUI thread is the main dominant thread running
    ## dictated by mainloop() call

