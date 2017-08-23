from tkinter import *
from tkinter import ttk
import test

root = None
mainframe = None

target_db = None
current_db = None

socket = None

def _create_gui():
    global root
    global mainframe

    root = Tk()
    root.title("Feet to Meters")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    _create_widgets()

def _create_widgets():
    global target_db
    target_db = DoubleVar()

    global current_db
    current_db = StringVar()

    ttk.Label(mainframe, text="Decibel Target").grid(column=0, row=1, sticky=W)
    target_db_entry = ttk.Entry(mainframe, width=7, textvariable=target_db).grid(column=1, row=1, sticky=(W, E))

    ttk.Label(mainframe, text="Current dB is ").grid(column=0, row=2, sticky=E)
    ttk.Label(mainframe, textvariable=current_db).grid(column=1, row=2, sticky=(W, E))

    ttk.Button(mainframe, text="Set Params", command=_set_params).grid(column=3, row=3, sticky=W)

def _set_params(*args):
    try:
        value = float(target_db.get())
        test.configure_db(value, socket)
    except ValueError:
        pass

def _update_fields():
    pass
    #print('{:.1f}'.format(test.get_last_db()))
    #root.after(200, _update_fields)
    #current_db.set('{:.1f}'.format(test.get_last_db()))

def start(_socket):
    global socket
    socket = _socket

    _create_gui()

    _update_fields()

    root.bind('<Return>', _set_params)
    root.mainloop()