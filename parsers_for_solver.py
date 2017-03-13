'''
File name: parsers_for_solver.py
Author: Michal Adamkiewicz
Date: 2014 - 2015

Implements the specific parsers needed by the ODE solver
'''

from parsers import treeParser

def initial_value(st):
    a=st.split(',')
    return list(map(lambda x: x.travel()(0,[]) , map(ODETree,a)))
    # return list(map(float, a))


class ParametricODETree(treeParser):
    "Customizable upon class creation number and list variable parser"

    time_var=['t']
    state_var=['x','y']

    def singles_handle(self,st):

        #TODO: parse numbers better + maybe complex numbers
        if(st.lower() in self.constants):
            self.function=self.constants[st.lower()]

        #Auto multyplication potencial?

        elif(st in self.time_var):
            self.function=st

        elif(st[:-3] in self.state_var):
            self.function=st

        else:
            self.function=float(st)


    def travel(self):

        if(type(self.function)==type(1.0)):
            def actual_function(*args):
                return self.function

        elif(type(self.function)==type(' ')):

            if(self.function in self.time_var):
                def actual_function(*args):
                    return args[self.time_var.index(self.function)]


            elif(self.function[:-3] in self.state_var):

                def actual_function(*args):
                    return args[ self.state_var.index(self.function[:-3]) +len(self.time_var) ][int(self.function[2:-1])]
                    # return state[int(self.function[2:-1])]#

        else:
            function_list=list(map(lambda x: x.travel(), self.leaves))
            def actual_function(*args):
                return self.function(* [x(*args) for x in function_list] )

        return actual_function