print("Palima's test version is running.")

#import requirements
import tkinter as tk
import time

#add local objects dictionary
objects = {}

#Add the screen class.
class Screen:
    is_running = False

    def __init__(
            self
    ):
        root = tk.Tk()
        root.title("Palima")
        root.geometry("950x700")
        root.resizable(False, False)
        root.config(bg='black')
        objects[self] = root
    
    def write_screen(self):
        global is_running
        try:
            objects[self].update()
            is_running = True
        except:
            is_running = False
