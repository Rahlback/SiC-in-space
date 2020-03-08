import math


def calc_temp(mv):
    """Calculates the temperature from the voltage reading of a LMT85dckt with the formula
    (8.194 - math.sqrt((-8.192) ** 2 + 4 * 0.00262 * (1324 - mv))) / (2 * -0.00262) + 30

    Rounds the temperature to the set "round" parameter, defaults to 2 decimals
    """
    temperature = round((8.194 - math.sqrt((-8.192) ** 2 + 4 * 0.00262 * (1324 - mv))) / (2 * -0.00262) + 30, 2)
    return temperature


if __name__ == "__main__":
    print(calc_temp(1743))
    