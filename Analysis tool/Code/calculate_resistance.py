"""This file is to calculate the resistance values for the transistors bases"""
import math


rb1 = 15000
rb2 = 22000

rb_range = []
min_resistance = 1000
max_resistance = 30000
resistance_step = 1000

voltages = []
min_voltage = 0.1
max_voltage = 10
step = 0.1
ube = 3

relation_list = []

for volt in range(int(min_voltage*100), int(max_voltage*100), int(step*100)):
    voltages.append(volt/100)

for resistance in range(min_resistance, max_resistance + resistance_step, resistance_step):
    rb_range.append(resistance)

for volt in voltages:
    for resistance in rb_range:
        voltage_divide = (volt - ube) * resistance/(rb2 + resistance)
        relation_list.append([round(voltage_divide, 3), resistance, volt, volt - ube, round(resistance/(rb2 + resistance), 2)])

if __name__ == "__main__":
    for item in relation_list:
        print(item)
    test = input("Enter resistance\n")
    res = int(test)

    for item in relation_list:
        if res in item:
            print(item)