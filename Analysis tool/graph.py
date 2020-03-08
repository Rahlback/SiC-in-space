"""This file is not part of the project and is only used to produce specific graphs to demonstrate
the desired results from the project."""
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy import optimize

def exp(x, a, b, c):
    return a * np.exp(x * b) + c

plt.rcParams.update({'font.size': 22})
steps = 0.01
lower_x = 4
upper_x = 15

list_of_x = []
list_of_y = []

for i in np.arange(lower_x, upper_x, steps):
    list_of_x.append(i)
    list_of_y.append(exp((i), 1, 1, 0))




if __name__ == "__main__":

    figure = plt.plot(list_of_x, list_of_y, 'b-')
    # plt.grid(True)
    plt.title("Ib/Ube")
    plt.xlabel("Ube")
    plt.ylabel("Ib")
    # plt.arrow()
    plt.xticks([])
    plt.yticks([])
    plt.show()


    print(list_of_x)
    print(list_of_y)

