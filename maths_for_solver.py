'''
File name: maths_for_solver.py
Author: Michal Adamkiewicz
Date: 2014 - 2015

Contains the functions which calculate numpy arrays for differential equations using Euler's Modified Method
'''

import math
from numpy import zeros, arange, array

from multiprocessing import Array


def non_dif_graph(pipe, func, x_init, x_max, step_size, skip_size):

    x_a = arange(x_init, x_max, step_size * skip_size)

    # y_a=func(x_a,[])

    y_a = []

    for x in x_a:
        y_a.append(func(x, []))
    y_a = array(y_a)

    pipe.send((x_a, y_a))


def d1_Euler(pipe, derivative, init, x_init, x_max, step_size, skip_size):

    exp_size = int((x_max - x_init) // (step_size * skip_size)) + 2
    x = x_init
    y = init[:]

    order = len(y)
    y_derivative = y[:]

    x_a = zeros((exp_size))
    y_a = zeros((exp_size))

    for big_step in range(exp_size):

        x_a[big_step] = x
        y_a[big_step] = y[0].real

        for small_step in range(skip_size):
            for i in range(order - 1):
                y_derivative[i] = y[(i + 1)]
            y_derivative[(order - 1)] = derivative(x, y)

            for i in range(order):
                y[i] = y[i] + step_size * y_derivative[i]
            x = x + step_size

    pipe.send((x_a, y_a))
    # return x_a,y_a


def d2_Euler(pipe, func_x, func_y, x_init, y_init, t_init, t_max, step_size, skip_size):

    exp_size = int((t_max - t_init) // (step_size * skip_size)) + 2

    print('expected size:', exp_size)
    t = t_init

    if(x_init != None):
        x = x_init[:]
        order_x = len(x)
        x_derivative = x[:]
    else:
        x = [0]
        x[0] = func_x(t_init, [], [])

    if(y_init != None):
        y = y_init[:]
        order_y = len(y)
        y_derivative = y[:]
    else:
        y = [0]
        y[0] = func_y(t_init, [], [])

    t_a = zeros((exp_size))
    x_a = zeros((exp_size))
    y_a = zeros((exp_size))

    for big_step in range(exp_size):

        t_a[big_step] = t
        x_a[big_step] = x[0].real
        y_a[big_step] = y[0].real
        print(big_step)

        for small_step in range(skip_size):

            if(x_init == None):
                x[0] = func_x(t, x, y)
            else:
                for i in range(order_x - 1):
                    x_derivative[i] = x[(i + 1)]
                x_derivative[(order_x - 1)] = func_x(t, x, y)

                for i in range(order_x):
                    x[i] = x[i] + step_size * x_derivative[i]

            if(y_init == None):
                y[0] = func_y(t, x, y)
            else:
                for i in range(order_y - 1):
                    y_derivative[i] = y[(i + 1)]
                y_derivative[(order_y - 1)] = func_y(t, x, y)

                for i in range(order_y):
                    y[i] = y[i] + step_size * y_derivative[i]

            t = t + step_size

    print('prep to send')

    pipe.send((t_a, x_a, y_a))

    print('sent')
    # return x_a,y_a


def d2_Euler_shared(count, arr_t, arr_x, arr_y, func_x, func_y, x_init, y_init, t_init, t_max, step_size, skip_size):

    exp_size = int((t_max - t_init) // (step_size * skip_size)) + 2

    print('expected size:', exp_size)
    t = t_init

    if(x_init != None):
        x = x_init[:]
        order_x = len(x)
        x_derivative = x[:]
    else:
        x = [0]
        x[0] = func_x(t_init, [], [])

    if(y_init != None):
        y = y_init[:]
        order_y = len(y)
        y_derivative = y[:]
    else:
        y = [0]
        y[0] = func_y(t_init, [], [])

    # t_a=zeros((exp_size))
    # x_a=zeros((exp_size))
    # y_a=zeros((exp_size))

    for big_step in range(exp_size):

        arr_t[big_step] = t
        arr_x[big_step] = x[0].real
        arr_y[big_step] = y[0].real
        # print(big_step)
        count.value = big_step

        for small_step in range(skip_size):

            if(x_init == None):
                x[0] = func_x(t, x, y)
            else:
                for i in range(order_x - 1):
                    x_derivative[i] = x[(i + 1)]
                x_derivative[(order_x - 1)] = func_x(t, x, y)

                for i in range(order_x):
                    x[i] = x[i] + step_size * x_derivative[i]

            if(y_init == None):
                y[0] = func_y(t, x, y)
            else:
                for i in range(order_y - 1):
                    y_derivative[i] = y[(i + 1)]
                y_derivative[(order_y - 1)] = func_y(t, x, y)

                for i in range(order_y):
                    y[i] = y[i] + step_size * y_derivative[i]

            t = t + step_size

    # print('prep to send')

    # pipe.send((t_a,x_a,y_a))

    print('sent')
    # return x_a,y_a


if __name__ == '__main__':

    func = '-50*y[0]*(1-2/((9+y[0]**2)**(0.5)))'
    init = '[2,0]'

    step_size = 0.001
    skip_size = 1000
    x_init = 0
    x_max = 20

    # no pipe - broken
    a = d1_Euler(func, init, x_init, x_max, step_size, skip_size)

    print(a[0])
    print(a[1])

    print('done')
