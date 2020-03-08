import random
import datetime
import numpy as np

def get_random_number(range):
    return random.randrange(range)


def run():
    x = 0
    print('time, sic ube, sic uc, sic ub, sic temp, si ube, si ub, si uc, si temp')
    while x != 82:
        datetime.timedelta(hours=(1*x))
        sic_ube = 2
        sic_uc = get_random_number(10) + 1
        sic_ub = get_random_number(10) + 1
        sic_temp = get_random_number(1654) + 301

        si_ube = 0.7
        si_uc = get_random_number(10) + 1
        si_ub = get_random_number(10) + 1
        si_temp = get_random_number(1654) + 301
        # print(f'{datetime.datetime.now()+datetime.timedelta(hours=(1*x))}\t{sic_ube}\t{sic_uc}\t{sic_ub}\t{sic_temp}\t{si_ube}\t{si_ub}\t{si_uc}\t{si_temp}')
        print(f'{datetime.datetime.now()+datetime.timedelta(hours=(1*x))},{sic_ube},{sic_uc},{sic_ub},{sic_temp},{si_ube},{si_ub},{si_uc},{si_temp}')
        x += 1


def generate_temperature_data():
    """Generate data that is dependent on temperature. Higher temperature should give higher beta values."""
    x = 0
    print('time, sic ube, sic uc, sic ub, sic temp, si ube, si ub, si uc, si temp')
    sic_ube = 2
    si_ube = 0.7
    while x != 82:
        datetime.timedelta(hours=(1 * x))

        sic_temp = get_random_number(1654) + 301
        si_temp = get_random_number(1654) + 301

        # higher Ub = higher beta
        # higher uc = lower beta
        # beta = (ub * rc)/ (uc * rb)

        # increase ub with 0.05 with each step? Or maybe set so Ub
        sic_uc = np.exp((2000 - sic_temp)/1000)
        si_uc = np.exp((2000 - si_temp)/1000)

        if sic_temp % 2 > 0:
            sign = -1
        else:
            sign = 1

        noise = random.random() * sign / 5

        sic_ub = 1.8 + noise * sic_temp/2000
        si_ub = 1.8 + noise * si_temp/2000

        print(f'{datetime.datetime.now() + datetime.timedelta(hours=(1 * x))},{sic_ube},{sic_uc},{sic_ub},{sic_temp},{si_ube},{si_ub},{si_uc},{si_temp}')
        x += 1


if __name__ == "__main__":
    # run()
    generate_temperature_data()