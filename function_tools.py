'''
File name: function_tools.py
Author: Michal Adamkiewicz
Date: 2015

Tools for helping with function heavy homeworks, including finding contrived derivatives
'''

import tkinter as tk
import math

from parsers import CalcTree

class FuncTools:
	def __init__(self):

		self.root=tk.Tk()
		self.root.title('Function Tools')
		self.root.resizable(True,False)


		tk.Label(self.root,text='f(t)=').grid(row=0,column=0,columnspan=2,sticky='ew')

		self.function_main=tk.Entry(self.root,width=30)
		self.function_main.grid(row=0,column=2,columnspan=3,sticky='ew')

		self.diff_button=tk.Button(self.root,text='Diff',command=self.differ)
		self.diff_button.grid(row=0,column=5,columnspan=3,sticky='ew')

		self.roots_button=tk.Button(self.root,text='Roots',command=self.find_roots)
		self.roots_button.grid(row=0,column=8,columnspan=1,sticky='ew')


		tk.Label(self.root,text='F(').grid(row=1,column=0,columnspan=1,sticky='ew')

		self.int_time=tk.Entry(self.root,width=2)
		self.int_time.grid(row=1,column=1,columnspan=1,sticky='ew')

		tk.Label(self.root,text=')=').grid(row=1,column=2,columnspan=1,sticky='ew')

		self.int_value=tk.Entry(self.root,width=15)
		self.int_value.grid(row=1,column=3,columnspan=1,sticky='ew')

		self.int_button=tk.Button(self.root,text='Integrate',command=self.inter)
		self.int_button.grid(row=1,column=4,columnspan=1,sticky='ew')

		tk.Label(self.root,text='f(').grid(row=1,column=5,columnspan=1,sticky='ew')

		self.sub_value=tk.Entry(self.root,width=2)
		self.sub_value.grid(row=1,column=6,columnspan=1,sticky='ew')

		tk.Label(self.root,text=')=').grid(row=1,column=7,columnspan=1,sticky='ew')

		self.sub_button=tk.Button(self.root,text='Eval',command=self.substitute)
		self.sub_button.grid(row=1,column=8,columnspan=1,sticky='ew')

		tk.Label(self.root,text='Output:').grid(row=2,column=0,columnspan=3,sticky='ew')

		self.output=tk.Entry(self.root,width=30)
		self.output.grid(row=2,column=3,columnspan=6,sticky='ew')




		self.root.grid_columnconfigure(0,weight=0)
		self.root.grid_columnconfigure(1,weight=1)
		self.root.grid_columnconfigure(2,weight=0)
		self.root.grid_columnconfigure(3,weight=1)
		self.root.grid_columnconfigure(4,weight=0)
		self.root.grid_columnconfigure(5,weight=0)
		self.root.grid_columnconfigure(6,weight=6)
		self.root.grid_columnconfigure(7,weight=0)
		self.root.grid_columnconfigure(8,weight=0)


		self.root.grid_rowconfigure(0,weight=0)
		self.root.grid_rowconfigure(1,weight=1)
		self.root.grid_rowconfigure(2,weight=0)



		#mac tkinter bug workaround
		self.function_main.bind("<Key>", self.arrow_bug_workaround)
		self.output.bind("<Key>", self.arrow_bug_workaround)
		self.int_time.bind("<Key>", self.arrow_bug_workaround)
		self.int_value.bind("<Key>", self.arrow_bug_workaround)
		self.sub_value.bind("<Key>", self.arrow_bug_workaround)

		#draw elements
		self.root.update()


	def arrow_bug_workaround(self,event): 
		if event.keycode in {8320768, 8255233}: 
			return "break" 


	def substitute(self):

		sub_val=float(self.sub_value.get())
		sub_tree=CalcTree(self.sub_value.get())


		func_tree=CalcTree(self.function_main.get())

		ans_val=func_tree.travel()(t=sub_val)

		if(int(ans_val)==ans_val):
			ans_val=int(ans_val)

		# func_tree=func_tree.substitute('t',sub_tree)
		# func_tree.simplify_basic()

		self.output.delete(0,tk.END)
		# self.output.insert(0,"Float: "+str(ans_val)+' Attempted to simplyify: '+str(func_tree))

		self.output.insert(0,"f("+str(self.sub_value.get())+")= "+str(ans_val))


	def differ(self):
		func_tree=CalcTree(self.function_main.get())
		func_tree=func_tree.diffrenciate('t')
		func_tree.simplify_basic()
		self.output.delete(0,tk.END)
		self.output.insert(0,"f'(t)= "+str(func_tree))


	def inter(self):
		func_tree=CalcTree(self.function_main.get())
		func_tree=func_tree.integrate('t')
		func_tree.simplify_basic()

		t_val=self.int_time.get().strip()
		F_val=self.int_value.get().strip()

		if(t_val=='' or F_val==''):

			self.output.delete(0,tk.END)
			self.output.insert(0,"F(t)= "+str(func_tree)+' + C')	

		else:

			t_val=float(t_val)
			F_val=float(F_val)

			c=F_val-func_tree.travel()(t=t_val)

			if(int(c)==c):
				c=int(c)

			self.output.delete(0,tk.END)

			if(c<0):
				self.output.insert(0,"F(t)= "+str(func_tree)+' - '+str(-c))
			elif(c==0):
				self.output.insert(0,"F(t)= "+str(func_tree))
			else:
				self.output.insert(0,"F(t)= "+str(func_tree)+' + '+str(c))	

	def find_roots(self):
		func_tree=CalcTree(self.function_main.get())


		func_function=func_tree.travel()
		derivative_function=func_tree.diffrenciate('t').travel()


		search_size=100
		search_density=2
		search_decimal_places=3
		#This is used as both the rounding and closeness parameter - low gradients might break it
		candidates=[]
		sign=0
		for t,f in zip(map(lambda x:(x-search_size)/search_density,range(2*search_size+1)),map(lambda x:func_function(t=((x-search_size)/search_density)),range(2*search_size+1))):

			if(f==0):
				candidates.append(t)
				sign=-sign
			elif(sign==0):
				sign=f//math.fabs(f)
			elif(sign!=f//math.fabs(f)):
				sign=f//math.fabs(f)
				candidates.append(t)
			# print(t,f)

		sol=[]
		for x_0 in candidates:
			x=x_0
			while(math.fabs(func_function(t=x))>10**(-search_decimal_places)):
				x=x-func_function(t=x)/derivative_function(t=x)
			if(int(x)==x):
				x=int(x)
			sol.append(round(x,search_decimal_places))

		self.output.delete(0,tk.END)
		self.output.insert(0,"f(t)=0 at: "+", ".join(map(lambda x:"t="+str(x),sol)))	





if __name__ == '__main__':
	M=FuncTools()

	M.root.mainloop()