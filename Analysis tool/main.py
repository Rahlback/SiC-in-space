from DataAnalysis import DataHandler
from filehandler import FileHandler
import numpy as np

# This is the driver for the code.
# Edit the config
""""This is the driver for the SiC in space experiment graphing tool. This driver will not work with most other 
data since methods that have been built for this project is quite specific. Change methods in 'DataAnalysis' to work
with your projects specific headers and data. Don't forget that the unittests will need to be changed as well if any 
changes are made."""


def exp(x, a, b, c):
    return a * np.exp(x * b) + c

def poly_1(x, a, b):
    return a*x + b

def poly_2(x, a, b, c):
    return a*x**2 + b*x + c

def poly_3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d


if __name__ == "__main__":
    fh = FileHandler()
    config = fh.readConfig('config')
    # for key in config:
    #     print(key)
    dh = DataHandler()

    sic_plot_type = dh.parse_plt_type(config[1]['sic_color'], config[1])
    si_plot_type = dh.parse_plt_type(config[1]['si_color'], config[1])

    csv_path = './'
    csv_path = csv_path + config[1]['filename']

    catch = fh.readCSV(csv_path, 'str', True, ';')
    sic_data, si_data = dh.parse_csv_data(catch)

    #print(sic_data)
    # Convert ADC values
    if config[1]['convert_from_adc_values'] == 'True':
        sic_data = dh.convert_2d_array_adc_values(sic_data, [0], True)
        si_data = dh.convert_2d_array_adc_values(si_data, [0], True)
    #print(sic_data)

    list_of_indexes_to_convert = [1, 2, 3]


    # If temperature is in mV, look up the temperature in LUT. Else convert the string to an int.
    if config[1]['temperature_unit'] == 'mV':
        sic_data = dh.look_up_temperature_in_lut(sic_data, 4, './LMT85_LookUpTableCSV.csv')
        si_data = dh.look_up_temperature_in_lut(si_data, 4, './LMT85_LookUpTableCSV.csv')
    else:
        list_of_indexes_to_convert.append(4)

    sic_data = dh.convert_data_to_float(sic_data, list_of_indexes_to_convert, config[1]['number_base'])
    si_data = dh.convert_data_to_float(si_data, list_of_indexes_to_convert, config[1]['number_base'])

    # time, Ube, Uc, Ub, Temp -> time, Ube, Uc, Ub, Temperature, Ic, Ib, Beta
    # print(si_data)
    sic_beta = []
    si_beta = []
    for data_line in sic_data:
        temp_sic_beta = []
        temp_sic_beta.append(data_line[0])
        temp_sic_beta.append(data_line[1])
        temp_sic_beta.append(
            dh.calculate_current_gain(data_line[3], config[0]['sic_rb'], data_line[2], config[0]['sic_rc']))
        temp_sic_beta.append(data_line[4])
        sic_beta.append(temp_sic_beta)
        data_line.append(dh.calculate_current(data_line[2], config[0]['sic_rc']))  # Ic
        data_line.append(dh.calculate_current(data_line[3], config[0]['sic_rb']))  # Ib
        data_line.append(temp_sic_beta[2])  # Beta

    for data_line in si_data:
        temp_si_beta = []
        temp_si_beta.append(data_line[0])
        temp_si_beta.append(data_line[1])
        temp_si_beta.append(dh.calculate_current_gain(data_line[3], config[0]['si_rb'], data_line[2], config[0]['si_rc']))
        temp_si_beta.append(data_line[4])
        si_beta.append(temp_si_beta)
        data_line.append(dh.calculate_current(data_line[2], config[0]['si_rc']))  # Ic
        data_line.append(dh.calculate_current(data_line[3], config[0]['si_rb']))  # Ib
        data_line.append(temp_si_beta[2])  # Beta



    sic_data = dh.sort_by_value_at_index(sic_data, 4)
    si_data = dh.sort_by_value_at_index(si_data, 4)

    ### Filter bad Ube from the data. Specified in the config file.
    sic_ube_target = float(config[1]['filter_bad_ube_sic'])
    sic_ic_target = float(config[1]['filter_bad_ic_sic'])

    si_ube_target = float(config[1]['filter_bad_ube_si'])
    si_ic_target = float(config[1]['filter_bad_ic_si'])

    sic_data = dh.filter_data_below(sic_data, sic_ube_target, 1)
    si_data = dh.filter_data_below(si_data, si_ube_target, 1)

    sic_data = dh.filter_data_below(sic_data, sic_ic_target, 5)
    si_data = dh.filter_data_below(si_data, si_ic_target, 5)

    # time, Ube, Uc, Ub, Temperature, Ic, Ib, Beta



    ### Extract temperature interval
    temperatures = config[1]['temperature_splits_for_ube'].split(',')
    temperatures = list(map(int, temperatures))
    stray = float(config[1]['stray_value'])

    #### Extract Ube temperature range from config
    si_ube_ib_pairs = {}
    si_beta_ic_pairs = {}  # Key is temperature, same as Ib/Ube. Key -->  [Ic, Beta]

    sic_beta_ic_pairs = {}
    sic_ube_ib_pairs = {}
    for temp in temperatures:
        temp_list = []
        # si_ube_ib_pairs[temp] = []
        # ube_list.append(dh.filter_data_by(si_data, temp, stray, 4))
        filtered_list = dh.filter_data_by(si_data, temp, stray, 4)

        if filtered_list:
            filtered_list = dh.average_temperature_data(filtered_list, 1, 3)
            for row in filtered_list:
                # print(row)
                temp_list.append(row)
            # sic_ube_ub = dh.extract_data(temp_list, [1, 3])
            si_ube_ub = dh.extract_data(temp_list, [1, 3])
            # sic_ube_ub = dh.sort_by_value_at_index(sic_ube_ub, 0)
            si_ube_ub = dh.sort_by_value_at_index(si_ube_ub, 0)

            si_beta_ic = dh.extract_data(temp_list, [5, 7])
            si_beta_ic = dh.sort_by_value_at_index(si_beta_ic, 0)
            si_ic = dh.extract_data(si_beta_ic, [0])
            si_beta = dh.extract_data(si_beta_ic, [1])
            si_beta_ic_pairs[temp] = [si_ic, si_beta]
            # sic_ube = dh.extract_data(sic_ube_ub, [0])
            # sic_ub = dh.extract_data(sic_ube_ub, [1])

            si_ube = dh.extract_data(si_ube_ub, [0])
            si_ub = dh.extract_data(si_ube_ub, [1])

            # sic_ib = dh.calculate_current_from_list(sic_ub, config[0]['si_rb'], 0)
            # sic_ube_ib_pairs[temp] = [si_ib, si_ube]

            si_ib = dh.calculate_current_from_list(si_ub, config[0]['si_rb'], 0)
            si_ube_ib_pairs[temp] = [si_ib, si_ube]

    si_ib = []
    si_ube = []
    si_ic = []
    si_beta = []
    labels = []
    for k in si_ube_ib_pairs:
        print(f'{k}: {si_ube_ib_pairs[k]}')
        si_ib.append(si_ube_ib_pairs[k][0])
        si_ube.append(si_ube_ib_pairs[k][1])

        si_ic.append(si_beta_ic_pairs[k][0])
        si_beta.append(si_beta_ic_pairs[k][1])
        labels.append(str(k) + "°C")

    print('------ SiC -------')
    #### SiC ####
    sic_ube_ib_pairs = {}
    for temp in temperatures:
        temp_list = []
        # si_ube_ib_pairs[temp] = []
        # ube_list.append(dh.filter_data_by(si_data, temp, stray, 4))
        filtered_list = dh.filter_data_by(sic_data, temp, stray, 4)

        # print(filtered_list)
        if filtered_list:
            filtered_list = dh.average_temperature_data(filtered_list, 1, 6)
            filtered_list = dh.average_temperature_data(filtered_list, 1, 3)
            for row in filtered_list:
                # print(row)
                temp_list.append(row)
            # sic_ube_ub = dh.extract_data(temp_list, [1, 3])
            sic_ube_ub = dh.extract_data(temp_list, [1, 3])

            # sic_ube_ub = dh.sort_by_value_at_index(sic_ube_ub, 0)
            sic_ube_ub = dh.sort_by_value_at_index(sic_ube_ub, 0)

            # sic_ube = dh.extract_data(sic_ube_ub, [0])
            # sic_ub = dh.extract_data(sic_ube_ub, [1])

            sic_ube = dh.extract_data(sic_ube_ub, [0])
            sic_ub = dh.extract_data(sic_ube_ub, [1])

            # sic_ib = dh.calculate_current_from_list(sic_ub, config[0]['si_rb'], 0)
            # sic_ube_ib_pairs[temp] = [si_ib, si_ube]

            sic_ib = dh.calculate_current_from_list(sic_ub, config[0]['sic_rb'], 0)
            sic_ube_ib_pairs[temp] = [sic_ib, sic_ube]

            sic_beta_ic = dh.extract_data(temp_list, [5, 7])
            sic_beta_ic = dh.sort_by_value_at_index(sic_beta_ic, 0)
            sic_ic = dh.extract_data(sic_beta_ic, [0])
            sic_beta = dh.extract_data(sic_beta_ic, [1])
            sic_beta_ic_pairs[temp] = [sic_ic, sic_beta]

    sic_ib = []
    sic_ube = []
    sic_ic = []
    sic_beta = []
    for k in sic_ube_ib_pairs:
        print(f'{k}: {sic_beta_ic_pairs[k]}')
        sic_ib.append(sic_ube_ib_pairs[k][0])
        sic_ube.append(sic_ube_ib_pairs[k][1])

        sic_ic.append(sic_beta_ic_pairs[k][0])
        sic_beta.append(sic_beta_ic_pairs[k][1])
        # labels.append(str(k) + "°C")

    #### Parse graph type
    if config[1]['graph_type'] == 'standalone':
        x_label = 'Deg C'

        if config[1]['dotted'] == 'True':
            si_plot_types = ['bo-', 'go-', 'ro-', 'yo-']
            sic_plot_types = ['bo-', 'go-', 'ro-', 'yo-']
        else:
            sic_plot_types = ['b-', 'g-', 'r-', 'y-']
            si_plot_types = ['b-', 'g-', 'r-', 'y-']

        if config[1]['x_axis'] == 'time':
            x_label = 'Time'
            rotate = True
        else:
            rotate = False

        if config[1]['separate_windows_for_si_sic'] == 'True':
            dh.set_graph_grid(1, 2)

            dh.multi_graph_plot_in_graph(sic_ic, sic_beta, sic_plot_types, labels)  # SiC beta/Ic
            dh.set_plot_info('SiC Beta/Ic', 'Ic[mA]', 'Beta', True)

            dh.multi_graph_plot_in_graph(si_ic, si_beta, si_plot_types, labels, 2)  # SiC beta/Ic
            dh.set_plot_info('Si Beta/Ic', 'Ic[mA]', 'Beta', True)

            dh.multi_graph_plot_in_graph(sic_ube, sic_ib, sic_plot_types, labels)
            dh.set_plot_info('SiC Ib/Ube', 'Ube[mV]', 'Ib[mA]', True)

            # dh.make_standalone_graph(si_ib, si_ube, 'Si Ib/Ube', 'Ube[mV]', 'Ib[mA]', si_plot_type, rotate,2)

            dh.multi_graph_plot_in_graph(si_ube, si_ib, si_plot_types, labels, 2)
            dh.set_plot_info('Si Ib/Ube', 'Ube[mV]', 'Ib[mA]', True)

        else:
            dh.set_graph_grid(2, 2)
            # dh.make_standalone_graph(sic_beta_values, sic_x_values, 'SiC Beta values', x_label, 'Beta', sic_plot_type, rotate)

            dh.multi_graph_plot_in_graph(sic_ic, sic_beta, sic_plot_types, labels)  # SiC beta/Ic
            dh.set_plot_info('SiC Beta/Ic', 'Ic[mA]', 'Beta', True)

            dh.multi_graph_plot_in_graph(si_ic, si_beta, si_plot_types, labels)  # SiC beta/Ic
            dh.set_plot_info('Si Beta/Ic', 'Ic[mA]', 'Beta', True)

            dh.multi_graph_plot_in_graph(sic_ube, sic_ib, sic_plot_types, labels)  # SiC Ib/Ube
            dh.set_plot_info('SiC Ib/Ube', 'Ube[mV]', 'Ib[mA]', True)

            dh.multi_graph_plot_in_graph(si_ube, si_ib, si_plot_types, labels)  # Si Ib/Ube
            dh.set_plot_info('Si Ib/Ube', 'Ube[mV]', 'Ib[mA]', True)


    # if config[1]['graph_type'] == 'fitted_standalone':
    #     #TODO: Change the fitted points from being -40 to 150 to be between the lowest temperature measured
    #     # and the highest temperature measured
    #
    #     # a, b, c, d = dh.curve_fit(sic_beta_values, sic_x_values)
    #     # print(a)
    #     # print(b)
    #     sic_fitted_points = []
    #     si_fitted_points = []
    #
    #     function_type = config[1]['fit_function']
    #     sic_function_string = ''
    #     si_function_string = ''
    #
    #     if function_type == 'exp':
    #         a, b, c = dh.curve_fit(sic_beta_values, sic_x_values, exp)
    #         si_a, si_b, si_c = dh.curve_fit(si_beta_values, si_x_values, exp)
    #
    #         for x in range(-40, 150):
    #             sic_fitted_points.append(exp(x, a, b, c))
    #             si_fitted_points.append(exp(x, si_a, si_b, si_c))
    #
    #         sic_function_string = f'{a} * e^({b} * x) + {c}'
    #         si_function_string = f'{si_a} * e^({si_b} * x) + {si_c}'
    #
    #     if function_type == '3':
    #         a, b, c, d = dh.curve_fit(sic_beta_values, sic_x_values, poly_3)
    #         si_a, si_b, si_c, si_d = dh.curve_fit(si_beta_values, si_x_values, poly_3)
    #         print(f'{si_a}\n{si_b}\n{si_c}\n{si_d}')
    #
    #         for x in range(-40, 150):
    #             sic_fitted_points.append(poly_3(x, a, b, c, d))
    #             si_fitted_points.append(poly_3(x, si_a, si_b, si_c, si_d))
    #
    #         sic_function_string = f'{round(a, 2)}*x^3 + {round(b, 2)}*x^2 + {round(c, 2)} * x + {round(d, 2)}'
    #         si_function_string = f'{round(si_a, 2)}*x^3 + {round(si_b, 2)}*x^2 + {round(si_c, 2)} * x + {round(si_d, 2)}'
    #
    #     if function_type == '2':
    #         a, b, c = dh.curve_fit(sic_beta_values, sic_x_values, poly_2)
    #         si_a, si_b, si_c = dh.curve_fit(si_beta_values, si_x_values, poly_2)
    #         print(f'{si_a}\n{si_b}\n{si_c}')
    #         for x in range(-40, 150):
    #             sic_fitted_points.append(poly_2(x, a, b, c))
    #             si_fitted_points.append(poly_2(x, si_a, si_b, si_c))
    #
    #         sic_function_string = f'{round(a, 2)}*x^2 + {round(b, 2)} * x + {round(c, 2)}'
    #         si_function_string = f'{round(si_a, 2)}*x^2 + {round(si_b, 2)} * x + {round(si_c, 2)}'
    #
    #     if function_type == '1':
    #         a, b = dh.curve_fit(sic_beta_values, sic_x_values, poly_1)
    #         si_a, si_b = dh.curve_fit(si_beta_values, si_x_values, poly_1)
    #         print(f'{si_a}\n{si_b}')
    #         for x in range(-40, 150):
    #             sic_fitted_points.append(poly_1(x, a, b))
    #             si_fitted_points.append(poly_1(x, si_a, si_b))
    #
    #         sic_function_string = f'{round(a, 2)} * x + {round(b, 2)}'
    #         si_function_string = f'{round(si_a, 2)} * x + {round(si_b, 2)}'
    #
    #     # print(sic_beta_values)
    #     dh.set_graph_grid(1, 2)
    #     dh.combine_graphs([sic_beta_values, sic_fitted_points], [sic_x_values, range(-40, 150)], config[1]['x_axis'],
    #                       'SiC Beta values', 'Deg °C', 'Beta',
    #                       [sic_plot_type, 'b-'], 'Raw data', sic_function_string)
    #
    #     dh.combine_graphs([si_beta_values, si_fitted_points], [si_x_values, range(-40, 150)], config[1]['x_axis'], 'Si Beta values',
    #                     'Deg °C', 'Beta', [sic_plot_type, 'b-'], 'Raw data', si_function_string)

    data = []
    for index, data_line in enumerate(sic_data):
        data.append(si_data[index] + sic_data[index])
    print(si_data[0])
    print(sic_data[0])
    print(data[0])

    data = dh.sort_by_value_at_index(data, 1)
    headers = ['Time', 'Si ube', 'Si Uc', 'Si Ub', 'Si Temp', 'Si Ic', 'Si Ib', 'Si Beta',
               'Time', 'SiC ube', 'SiC Uc', 'SiC Ub', 'SiC Temp', 'SiC Ic', 'SiC Ib', 'SiC Beta']
    # Time	Si ube	Si Uc	Si Ub	Si Temp	Si Ic	Si Ib	Si Beta	Time	SiC ube	SiC Uc	SiC Ub	SiC Temp	SiC Ic	SiC Ib	SiC Beta
    try:
        fh.write_data(data, headers)
    except:
        print("\nCan not write to data dump file. Is the file open in another program?")


    dh.show_graphs()
