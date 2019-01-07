import tkinter as tk
import time


win=tk.Tk()
win.geometry('300x300')
win.title('Using tkinter')
message = 'Test Label'
x = 0
Label = tk.Label(win, text = message, font = ('Comic Sans MS', 30), bg = 'Green', fg = 'blue')
Label.pack(pady=100, padx=40)

pin = 15

def Update():
    Label['text'] = message
    
while True:
    x += 1
    message = x
    print(x)
    Update()
    win.update()
    time.sleep(0.5)
