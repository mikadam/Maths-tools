'''
File name: ODE_Solvers.py
Author: Michal Adamkiewicz
Date: 2014

Contains UI for ODE solver
'''

import math


import matplotlib
import tkinter as Tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk

from tkinter.filedialog import asksaveasfile

from multiprocessing import Process, Pipe, Array, Value

from parsers_for_solver import initial_value
from parsers_for_solver import ParametricODETree

matplotlib.use('TkAgg')

from numpy import array, zeros
import numpy

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ODE_Tk import d1_Euler, non_dif_graph, d2_Euler, d2_Euler_shared


def d1_Euler_wrapper(clear=True):
    
    global value_array
    global main_pipe
    global p
    # global triple
    # triple=False

    t_init=float(p_start.get())
    t_max=float(p_end.get())

    step_size=float(p_step.get())
    skip_size=int(p_skip.get())

    func_x=p_func_x.get()
    init_x=p_init_x.get()
    func_y=p_func_y.get()
    init_y=p_init_y.get()

    cancel.grid()
    prog['maximum']=int((t_max-t_init)//(step_size*skip_size))+2
    prog.grid()
    # prog.start(interval=None)
    prog.update()



    tree=ParametricODETree(func_x)
    function_x=tree.travel()

    tree=ParametricODETree(func_y)
    function_y=tree.travel()

    if clear:
        a.clear()

    # main_pipe,child_pipe = Pipe()

    if(init_x.strip()==''):

        # p=Process(target=non_dif_graph,args=(child_pipe,function,t_init,t_max,step_size,skip_size))
        init_x=None
    else:
        init_x=initial_value(init_x)

        
    if(init_y.strip()==''):
        init_y=None
    else:

        init_y=initial_value(init_y)
        

    global a_t,a_x,a_y, count
    a_t=Array('d', zeros(int((t_max-t_init)//(step_size*skip_size))+2))
    a_x=Array('d', zeros(int((t_max-t_init)//(step_size*skip_size))+2))
    a_y=Array('d', zeros(int((t_max-t_init)//(step_size*skip_size))+2))

    count=Value('i', 0)

    p=Process(target=d2_Euler_shared,args=(count,a_t,a_x,a_y,function_x,function_y,init_x,init_y,t_init,t_max,step_size,skip_size))



    p.daemon=True
    p.start()

    root.after(500,check_proc)

def check_proc():

    # if not main_pipe.poll():
    if p.is_alive():
        # print(count.value)
        prog['value']=count.value
        root.after(500,check_proc)

    else:

        global value_array
        value_array=[]
        value_array.append(numpy.frombuffer(a_t.get_obj()))
        value_array.append(numpy.frombuffer(a_x.get_obj()))
        value_array.append(numpy.frombuffer(a_y.get_obj()))

        # print()
        # for line in array([value_array[0],value_array[1],value_array[2]]).T:
        #     print(line)
        # print()

        if(plot_type.get()==0):
            a.plot(value_array[1],value_array[2])
        elif(plot_type.get()==1):
            a.plot(value_array[0],value_array[1])
            a.plot(value_array[0],value_array[2])

        canvas.show()
        prog.stop()
        prog.grid_remove()

        #MOD
        cancel.grid_remove()

def save():
    try:
        value_array
    except NameError:
        messagebox.showerror("Can't save",'The function values have not been calculated yet!')
        return
    try:
        with asksaveasfile(defaultextension='.csv',initialfile='data_file') as f:
            for point in array([value_array[0],value_array[1],value_array[2]]).T:
                f.write(str(point[0])+','+str(point[1])+','+str(point[2])+'\n')
    except AttributeError:
        pass

def end_calc():
    global p
    p.terminate()

    prog.stop()
    prog.grid_remove()


root = Tk.Tk()
root.title("ODE Calc")

f = Figure(figsize=(6,5), dpi=100)
a = f.add_subplot(1,1,1)

canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()


Tk.Label(root,text=' ').grid(row=0,column=0,columnspan=6)

Tk.Label(root,text='Start:').grid(row=1,column=0,columnspan=1)
p_start=Tk.Entry(root,width=3)
p_start.grid(row=1,column=1,columnspan=1,sticky='ew')

Tk.Label(root,text='Step:').grid(row=1,column=2,columnspan=1)
p_step=Tk.Entry(root,width=6)
p_step.grid(row=1,column=3,columnspan=1,sticky='ew')

Tk.Label(root,text='Functions:').grid(row=1,column=4,columnspan=1)
p_func_x=Tk.Entry(root,width=25)
p_func_x.grid(row=1,column=5,columnspan=1,sticky='ew')
p_func_y=Tk.Entry(root,width=25)
p_func_y.grid(row=1,column=6,columnspan=1,sticky='ew')

Tk.Label(root,text='End:').grid(row=2,column=0,columnspan=1)
p_end=Tk.Entry(root,width=3)
p_end.grid(row=2,column=1,columnspan=1,sticky='ew')

Tk.Label(root,text='Skip').grid(row=2,column=2,columnspan=1)
p_skip=Tk.Entry(root,width=4)
p_skip.grid(row=2,column=3,columnspan=1,sticky='ew')

Tk.Label(root,text='Initial:').grid(row=2,column=4,columnspan=1)
p_init_x=Tk.Entry(root,width=30)
p_init_x.grid(row=2,column=5,columnspan=1,sticky='ew')
p_init_y=Tk.Entry(root,width=30)
p_init_y.grid(row=2,column=6,columnspan=1,sticky='ew')


calc=Tk.Button(root,text='Replace',command=d1_Euler_wrapper)
calc.grid(row=3,column=0,columnspan=2,sticky='ew')

calc=Tk.Button(root,text='Add',command=lambda:d1_Euler_wrapper(False))
calc.grid(row=3,column=2,columnspan=2,sticky='ew')

save=Tk.Button(root,text='Save Newest',command=save)
save.grid(row=3,column=4,columnspan=1,sticky='ew')

prog=ttk.Progressbar(root,mode='determinate')
prog.grid(row=3,column=5,columnspan=1,sticky='ew')
prog.grid_remove()

#MOD
cancel=Tk.Button(root,text='Cancel',command=end_calc)
cancel.grid(row=3,column=6,columnspan=1,sticky='ew')
cancel.grid_remove()
#end mod

plot_type = Tk.IntVar()

Tk.Radiobutton(root, text="Parametric", variable=plot_type, value=0).grid(row=1,column=7,columnspan=1,sticky='ew')
Tk.Radiobutton(root, text="Two Graph", variable=plot_type, value=1).grid(row=2,column=7,columnspan=1,sticky='ew')

canvas.get_tk_widget().grid(row=4,column=0,columnspan=8,sticky='ewns')

p_func_x.insert(0,'t')
p_init_x.insert(0,'')

p_func_y.insert(0,'-50*y[0]*(1-2/(sqrt(9+y[0]^2)))')
p_init_y.insert(0,'2,0')
p_step.insert(0,'0.001')
p_skip.insert(0,'100')
p_start.insert(0,'0')
p_end.insert(0,'10')

root.grid_columnconfigure(1,weight=1)
root.grid_columnconfigure(3,weight=1)
root.grid_columnconfigure(5,weight=2)
root.grid_rowconfigure(4,weight=1)



while 1:
    try:
        root.mainloop()
        exit()
    except UnicodeDecodeError:
        pass

    #Old unsafe parsers

    # function_str=''.join(filter(lambda x: x in "1234567890xy[]+-*/().", func))

    # function_str=string_sanitize(func)
    # def function(x, y):
    #     d = eval(function_str)
    #     return d


