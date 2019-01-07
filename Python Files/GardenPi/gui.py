import tkinter as tk
from tkinter import *
import time
import RPi.GPIO as GPIO
import os

win=tk.Tk()
win.title('Garden Pi Status')

# gravel beds section
label_gravelBeds = tk.Label(win, text='Gravel Beds', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=0,column=0, columnspan=2)
label_bed1 = tk.Label(win, text='Bed 1', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=1,column=0)
label_bed2 = tk.Label(win, text='Bed 2', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=2,column=0)
label_bed3 = tk.Label(win, text='Bed 3', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=3,column=0)
label_bed4 = tk.Label(win, text='Bed 4', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=4,column=0)
label_bed1_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=1,column=1) 
label_bed2_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=2,column=1)
label_bed3_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=3,column=1)
label_bed4_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=4,column=1)

# dissolved oxygen sensor section
filePath = (os.path.abspath(os.path.dirname(__file__)) + '/DOlevel.txt')
DOlevel = open(filePath, 'r')
label_gravelBeds = tk.Label(win, text='Dissolved Oxygen', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=5,column=0, columnspan=2)
label_DOlevel = tk.Label(win, text='Level', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=6,column=0)
label_DOvalve = tk.Label(win, text='Sprinklers', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=7,column=0)
label_DOlevel_status = tk.Label(win, text='{} mg/L'.format(DOlevel.read()), relief = SUNKEN, width=15, font = ('Helvetica', 20)).grid(row=6,column=1) 
label_DOvalve_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=7,column=1)

# dissolved oxygen sensor section
filePath = (os.path.abspath(os.path.dirname(__file__)) + '/DOlevel.txt')
DOlevel = open(filePath, 'r')
label_waterLevel = tk.Label(win, text='Water Level', relief = RAISED, width=30, font = ('Helvetica', 24)).grid(row=8,column=0, columnspan=2)
label_fillValve = tk.Label(win, text='Filling', relief = RIDGE, width=15, font = ('Helvetica', 20)).grid(row=9,column=0)
label_fillValve_status = tk.Label(win, text='OFF', relief = SUNKEN, width=15, bg='red', font = ('Helvetica', 20)).grid(row=9,column=1)


#def UpdateGUI():

#while True:
#    UpdateGUI()
#    win.update()
#    time.sleep(15)
    
