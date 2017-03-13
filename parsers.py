'''
File name: parsers.py
Author: Michal Adamkiewicz
Date: 2014 - 2015

Classes for parsing algebraic expressions safely and doing some basic symbolic manipulations
e.g. finding derivatives, doing substitutions
'''

import math

class treeParser:
    "Customizable upon class creation number_variable only parser"

    operators=[{'+': lambda x, y: x+y,'-': lambda x, y: x-y},
                {'*': lambda x, y: x*y,'/': lambda x, y: x/y},
                {'^': lambda x, y: x**y}]

    functions={'sin':math.sin,
                'cos':math.cos,
                'tan':math.tan,
                'asin':math.asin,
                'acos':math.acos,
                'atan':math.atan,
                'sqrt':math.sqrt,
                'abs':math.fabs,
                'floor':math.floor,
                'ln': (lambda x: math.log(x,math.e))}
    constants={'pi': math.pi, 'e': math.e}
    variables=['x','y']

    def __init__(self,st):

        st=st.strip()
        if(st[0]=='-'):
            st='0'+st

        found_match=self.operator_handle(st)
        if(found_match == 1): return

        #if passed has additional parenthesis
        if(st[0]=='(' and st[-1]==')'):
            inside_tree=self.__class__(st[1:-1])
            self.function=inside_tree.function
            self.leaves=inside_tree.leaves
            return


        found_match=self.function_handle(st)
        if(found_match == 1): return

        self.leaves=[]
        self.singles_handle(st)

    def operator_handle(self,st):
        for level in self.operators:
            for op, func in level.items():
                braket_level=0
                for char in reversed(range(len(st))):

                    if(st[char]==')'): braket_level+=1
                    elif(st[char]=='('): braket_level-=1
                    elif(st[char]==op and braket_level==0): 
                        self.function=func
                        self.leaves=[]
                        self.leaves.append(self.__class__(st[:char]))
                        self.leaves.append(self.__class__(st[char-len(st)+1:]))
                        return 1

    def function_handle(self,st):
        for fu,func in self.functions.items():
            if(st[:len(fu)] == fu):
                self.function=func
                #todo multi argument
                # self.leaves=[self.__class__(st[len(fu)+1:-1])]
                #working below
                #self.leaves=list(map(self.__class__,st[len(fu)+1:-1].split(',')))
                self.leaves=[self.__class__(st[len(fu)+1:-1])]
                return 1


    def singles_handle(self,st):
        #TODO: parse numbers better
        if(st in self.constants):
            self.function=self.constants[st]

        #Auto multyplication potencial?
        elif(st in self.variables):
            self.function=st

        else:
            self.function=float(st)


    def travel(self):

        if(type(self.function)==type(1.0)):
            def actual_function(*args):
                return self.function

        elif(self.function in self.variables):
            def actual_function(*args):
                return args[self.variables.index(self.function)]

        else:
            def actual_function(*args):
                return self.function(* map(lambda x: x.travel()(*args), self.leaves) )

        return actual_function

class MultiListTree(treeParser):
    'Customizable upon running parser'

    def singles_handle(self,st):

        #TODO: complex numbers
        if(st.lower() in self.constants):
            self.function=self.constants[st.lower()]
            return #Added later might be needed in other versions

        try:
            self.function=float(st)
        except ValueError:
            self.function=st


    def travel(self):

        if(type(self.function)==type(1.0) or type(self.function)==type(1)):
            def actual_function(**kargs):
                return self.function

        elif(type(self.function)==type(' ')):


            if('[' in self.function and ']' in self.function):
                var_name=self.function.split('[')[0]
                var_index=int(self.function.split('[',1)[1][:-1])
                def actual_function(**kargs):
                    return kargs[var_name][var_index]

            else:
                def actual_function(**kargs):
                    return kargs[self.function]

        else:
            function_list=list(map(lambda x: x.travel(), self.leaves))
            def actual_function(**kargs):
                return self.function(* [x(**kargs) for x in function_list] )

        return actual_function

class CalcTree(MultiListTree):

    def is_no_addition(self):

        if(self.function in self.functions.values()):
            return True

        if(type(self.function)==type(float(1)) or type(self.function)==type(" ")):
            return True


        if(not self.leaves[0].is_no_addition()):
            return False

        if(not self.leaves[1].is_no_addition()):
            return False

        if(self.function in self.operators[1].values()):
            return True

        if(self.function in self.operators[2].values()):
            return True


        return False

    def __str__(self):


        if(self.function==math.e):
            return 'e'
        elif(self.function==math.pi):
            return 'pi'

        try:
            if(int(self.function)==self.function):
                return str(int(self.function))
        except:
            pass


        for key,funct in self.functions.items():
            if(funct==self.function):
                return key+'('+str(self.leaves[0])+')'

        if(self.function==self.operators[0]['+']):
            return str(self.leaves[0])+'+'+str(self.leaves[1])
        if(self.function==self.operators[0]['-']):
            return str(self.leaves[0])+'-'+str(self.leaves[1])


        if(self.function==self.operators[1]['*']):

            if(self.leaves[0].is_no_addition()):

                if(self.leaves[1].is_no_addition()):
                    return str(self.leaves[0])+'*'+str(self.leaves[1])
                return str(self.leaves[0])+'*('+str(self.leaves[1])+')'

            if(self.leaves[1].is_no_addition()):
                return '('+str(self.leaves[0])+')*'+str(self.leaves[1])

            return '('+str(self.leaves[0])+')*('+str(self.leaves[1])+')'


        if(self.function==self.operators[1]['/']):
            if(self.leaves[0].is_no_addition()):
                if(type(self.leaves[1].function)==type(float(1)) or type(self.leaves[1].function)==type(" ")):
                    return str(self.leaves[0])+'/'+str(self.leaves[1])
                return str(self.leaves[0])+'/('+str(self.leaves[1])+')'

            if(type(self.leaves[1].function)==type(float(1)) or type(self.leaves[1].function)==type(" ")):
                return '('+str(self.leaves[0])+')/'+str(self.leaves[1])

            return '('+str(self.leaves[0])+')/('+str(self.leaves[1])+')'

        if(self.function==self.operators[2]['^']):

            if(type(self.leaves[0].function)==type(float(1)) or type(self.leaves[0].function)==type(" ")):
                if(type(self.leaves[1].function)==type(float(1)) or type(self.leaves[1].function)==type(" ")):
                    return str(self.leaves[0])+'^'+str(self.leaves[1])
                return str(self.leaves[0])+'^('+str(self.leaves[1])+')'

            if(type(self.leaves[1].function)==type(float(1)) or type(self.leaves[1].function)==type(" ")):
                    return '('+str(self.leaves[0])+')^'+str(self.leaves[1])

            return '('+str(self.leaves[0])+')^('+str(self.leaves[1])+')'


        return str(self.function)

    def new_tree(self,func,leves):

        new_instance=self.__class__('1')
        new_instance.leaves=leves
        if(type(func)==type(int(1))):
            new_instance.function=float(func)
        elif(type(func)==type(float(1))):
            new_instance.function=func
        elif(func=='+'):
            new_instance.function=self.operators[0]['+']

        elif(func=='-'):
            new_instance.function=self.operators[0]['-']

        elif(func=='*'):
            new_instance.function=self.operators[1]['*']
        elif(func=='/'):
            new_instance.function=self.operators[1]['/']
        elif(func=='^'):
            new_instance.function=self.operators[2]['^']

        elif(func in self.functions.keys()):
            new_instance.function=self.functions[func]
        else:
            new_instance.function=func
        return new_instance

    def diffrenciate(self,with_respect):


        if(type(self.function)==type(float(1))):
            return self.new_tree(0.0,[])

        elif(self.function==with_respect):
            return self.new_tree(1.0,[])

        elif(type(self.function)==type(' ')):
            return self.new_tree(0.0,[])

        elif(self.function==self.operators[0]['+']):
            return self.new_tree('+',[self.leaves[0].diffrenciate(with_respect),self.leaves[1].diffrenciate(with_respect)])

        elif(self.function==self.operators[0]['-']):
            return self.new_tree('-',[self.leaves[0].diffrenciate(with_respect),self.leaves[1].diffrenciate(with_respect)])

        elif(self.function==self.operators[1]['*']):

            b1=self.new_tree('*',[self.leaves[0].diffrenciate(with_respect),self.leaves[1]])
            b2=self.new_tree('*',[self.leaves[0],self.leaves[1].diffrenciate(with_respect)])
            return self.new_tree('+',[b1,b2])

        elif(self.function==self.operators[1]['/']):

            b1=self.new_tree('*',[self.leaves[0].diffrenciate(with_respect),self.leaves[1]])
            b2=self.new_tree('*',[self.leaves[0],self.leaves[1].diffrenciate(with_respect)])
            up_b=self.new_tree('-',[b1,b2])
            down_b=self.new_tree('^',[self.leaves[1],self.new_tree(2,[])])
            return self.new_tree('/',[up_b,down_b]) 

        elif(self.function==self.functions['sin']):
            return self.new_tree('*',[self.leaves[0].diffrenciate(with_respect),self.new_tree('cos',[self.leaves[0]])])

        elif(self.function==self.functions['cos']):
            to_negative=self.new_tree('*',[self.leaves[0].diffrenciate(with_respect),self.new_tree('sin',[self.leaves[0]])])
            return self.new_tree('-',[self.new_tree(0,[]),to_negative])

        elif(self.function==self.functions['tan']):
            b1=self.new_tree('^',[self.new_tree('tan',[self.leaves[0]]),self.new_tree(2,[])])
            return self.new_tree('*',[self.new_tree('+',[self.new_tree(1,[]),b1]),self.leaves[0].diffrenciate(with_respect)])

        elif(self.function==self.functions['ln']):
            return self.new_tree('/',[self.leaves[0].diffrenciate(with_respect),self.leaves[0]])

        elif(self.function==self.operators[2]['^']):
            if(type(self.leaves[1].function)==type(float(1))):
                without_chain=self.new_tree('*',[self.leaves[1],self.new_tree('^',[self.leaves[0], self.new_tree(self.leaves[1].function-1,[]) ])])
                return self.new_tree('*',[self.leaves[0].diffrenciate(with_respect),without_chain])

            #TODO Implement other rules

        print('Sorry the function you wish to differentiate is not implemented in this version')
        raise AttributeError

    def integrate(self,with_respect):

        if(type(self.function)==type(float(1))):
            return self.new_tree('*',[self.new_tree(self.function,[]),self.new_tree(with_respect,[])])

        elif(self.function==with_respect):
            return self.new_tree('^',[self.new_tree(with_respect,[]),self.new_tree(1,[])]).integrate(with_respect)

        elif(type(self.function)==type(' ')):
            return self.new_tree('*',[self.new_tree(self.function,[]),self.new_tree(with_respect,[])])

        elif(self.function==self.operators[0]['+']):
            return self.new_tree('+',[self.leaves[0].integrate(with_respect),self.leaves[1].integrate(with_respect)])

        elif(self.function==self.operators[0]['-']):
            return self.new_tree('-',[self.leaves[0].integrate(with_respect),self.leaves[1].integrate(with_respect)])



        elif(self.function==self.operators[1]['*']):
            if(type(self.leaves[0].function)==type(float(1))):
                return self.new_tree('*',[self.leaves[0],self.leaves[1].integrate(with_respect)])

        elif(self.function==self.operators[1]['*']):
            if(type(self.leaves[1].function)==type(float(1))):
                return self.new_tree('*',[self.leaves[1],self.leaves[0].integrate(with_respect)])

        elif(self.function==self.operators[1]['/']):
            if(type(self.leaves[1].function)==type(float(1))):
                return self.new_tree('/',[self.leaves[0].integrate(with_respect),self.leaves[1],])



        elif(self.function==self.operators[2]['^']):
            if(type(self.leaves[1].function)==type(float(1)) and self.leaves[0].function==with_respect):
                if(self.leaves[1].function==-1):
                    return self.new_tree('ln',[with_respect])
            return self.new_tree('/',[self.new_tree('^',[self.leaves[0], self.new_tree(self.leaves[1].function+1,[]) ]),self.new_tree(self.leaves[1].function+1,[])])

        print('Sorry the function you wish to integrate is not implemented in this version')
        raise AttributeError

    def simplify_basic(self):

        try:
            self.leaves[0].simplify_basic()
            self.leaves[1].simplify_basic()
        except (AttributeError, IndexError):
            pass




        try:
            if(self.function==self.operators[0]['+'] and self.leaves[0].function==0):#0+x=x
                self.function=self.leaves[1].function
                self.leaves=self.leaves[1].leaves
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[0]['+'] and self.leaves[1].function==0):#x+0=x
                self.function=self.leaves[0].function
                self.leaves=self.leaves[0].leaves
        except (AttributeError, IndexError):
            pass


        try:
            if(self.function==self.operators[0]['-'] and self.leaves[1].function==0):#x-0=x
                self.function=self.leaves[0].function
                self.leaves=self.leaves[0].leaves
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[1]['*'] and self.leaves[0].function==1):#1*x=x
                self.function=self.leaves[1].function
                self.leaves=self.leaves[1].leaves
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[1]['*'] and self.leaves[1].function==1):#x*1=x
                self.function=self.leaves[0].function
                self.leaves=self.leaves[0].leaves
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[1]['*'] and self.leaves[0].function==0):#0*x=0
                self.function=0
                self.leaves=[]
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[1]['*'] and self.leaves[1].function==0):#x*0=0
                self.function=0
                self.leaves=[]
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[1]['/'] and self.leaves[1].function==1):#x/1=1
                self.function=self.leaves[0].function
                self.leaves=self.leaves[0].leaves
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[2]['^'] and self.leaves[1].function==1):#x^1=x
                self.function=self.leaves[0].function
                self.leaves=self.leaves[0].leaves
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[0]['+'] and type(self.leaves[0].function)==type(float(1)) and type(self.leaves[1].function)==type(float(1))):
                self.function=self.leaves[0].function+self.leaves[1].function
                self.leaves=[]
        except (AttributeError, IndexError):
            pass

        try:
            if(self.function==self.operators[1]['*'] and type(self.leaves[0].function)==type(float(1)) and type(self.leaves[1].function)==type(float(1))):
                self.function=self.leaves[0].function*self.leaves[1].function
                self.leaves=[]
        except (AttributeError, IndexError):
            pass

    def substitute(self,var_sub,tree_sub):

        if(self.function==var_sub):
            return tree_sub
        elif(type(self.function)==type(float(1))):
            return self
        elif(type(self.function)==type(' ')):
            return self

        temp=self.new_tree("+",list(map(lambda x:x.substitute(var_sub,tree_sub), self.leaves)))
        temp.function=self.function
        return temp

if __name__ == '__main__':


    test2=' 5+5*(sin(3.14)-5*3)'
    test3='5+5*((sin(3.14)-5)*100)'
    test4='(x+1)*(y+2)'
    test5='(2+y[0]+y[1])*(x+y[0])'
    test='-50*y[0]*(1-2/((9+y[0]^2)^(0.5)))'
    test2='x^2+2'
    test='t*x[0]+y[1]*y[0]'
    test2='sin(t*pi)'
    test2='-1-1'
    test='ln(x)'
    test='1+x*15^3+sin(8*y)'
    test='4*y*x'
    test='2*2+sin(x+1)'
    k='(x-1)*(x-5)'
    # k='1-1+x'
    t=treeParser(k)


    # print((t.travel()(2,[5.5,2],[1,2])))
    # print((t.travel()(t=3,x=[5,2],y=[1,2],k=2)))

    # t.simplify_basic()
    # print(t)
    print(t.travel()(2))
    # a=t.integrate('x')
    # print(a)
    # a.simplify_basic()
    # print(a)


