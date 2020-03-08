import matplotlib.pyplot as plt
import math
from filehandler import FileHandler
import numpy as np
from scipy import optimize


def func(x, a, b, c):
    return a * np.exp(x * b) + c


def poly_2(x, a, b, c):
    return a*x**2 + b*x + c


def poly_3(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d


class DataHandler:
    """Class for handling data calculations specific for the SiC in space project."""
    def __init__(self):
        self.current_graph = 1
        self.graph_rows = 1
        self.graph_cols = 2
        self.figure_sub_plots = {}

    def set_graph_grid(self, rows, cols):
        """Sets the number of graphs that will be shown. Reserves space for graphs in window when run."""
        self.graph_rows = rows
        self.graph_cols = cols

    def calculate_current(self, u, r):
        """Calculates current from a known voltage and resistance using U = RI -> I = U/R"""
        return u/r

    def calculate_current_from_list(self, list, r, suffix=3):
        """Calculates the currents for a list

        suffix = power of unit
        Examples:
            list = [10, 20, 30]
            r = 20
            suffix = -3 # Unit is in mV, the method requires SI units.
            result = [10 * 10^(suffix)/r, 20 * 10^(suffix)/r, 30 * 10^(suffix)/r
        """
        temp_list = []
        for index, item in enumerate(list):
            temp_list.append(self.calculate_current(item*10**(suffix), r))
        return temp_list

    def filter_data_by(self, list_2d, match_value, stray, index):
        """Extracts data which has a matching value from list_2d (2D list)
        stray = offset of match_value. Real match_value is => match_value +- stray
        index = index of value to match

        Example:
            list_2d = [['time', 1, 2, 3, 4, 5],['time', 6, 2, 3, 4, 5],['time', 5, 1, 2, 7, 3]]
            stray = 1
            filter_data_by(list_2d, 5, stray, 5) # The two first lists in list_2d has a '5' at index 5

            return:
                [['time', 1, 2, 3, 4, 5],['time', 6, 2, 3, 4, 5]]
        """

        filtered_list = []
        for row in list_2d:
            if isinstance(row[index], int) or isinstance(row[index], float):
                if row[index] - stray <= match_value <= row[index]+stray:
                    filtered_list.append(row)
        if filtered_list:
            return filtered_list
        else:
            return

    def filter_data_below(self, list_2d, target_value, index, keep_exact_match=True):
        """Filters all data points in a 2D array based on the target_value. Removes all data points that are below
        target value. Index parameter specifies which value in each sub-list to compare against target_value.

        :param keep_exact_match. Bool, if true, keeps the data point if there is an exact match

        Example:
             list = [[1, 3, 5, 6, 6, 7], [1, 2, 4, 5, 6, 7], [7, 5, 4, 3, 65, 12]]
             filter_data_below(list, 3, 1)

             Return:
                [[1, 3, 5, 6, 6, 7], [7, 5, 4, 3, 65, 12]]

            """

        temp_list = []

        for row in list_2d:
            if target_value <= row[index]:
                temp_list.append(row)

        return temp_list


    def calculate_current_gain(self, ub, rb, uc, rc):
        """ TODO: Implement complete formula. Change test once formula implemented
        Ib = Ub/rb, Ic = Uc/rc"""
        if not isinstance(ub, int) and not isinstance(ub, float):
            raise TypeError(f'Wrong type specified: {type(ub)}, expected float or int')
        if not isinstance(rb, int) and not isinstance(rb, float):
            raise TypeError(f'Wrong type specified: {type(rb)}, expected float or int')
        if not isinstance(uc, int) and not isinstance(uc, float):
            raise TypeError(f'Wrong type specified: {type(uc)}, expected float or int')
        if not isinstance(rc, int) and not isinstance(rc, float):
            raise TypeError(f'Wrong type specified: {type(rc)}, expected float or int')

        ib = ub/rb
        ic = uc/rc

        beta = ic/ib

        return round(beta, 10)

    def extract_data(self, data, index_list):
        """Extracts data from a 2D array."""

        temp_list = []

        for data_row in data:
            list_line = []
            for index_element in index_list:
                if len(index_list) > 1:
                    list_line.append(data_row[index_element])
                else:
                    temp_list.append(data_row[index_element])
            if len(index_list) > 1:
                temp_list.append(list_line)

        return temp_list

    def convert_from_adc_value(self, adc_value, vref=3.19, adc_bits=12):
        """Converts a reading from the ADC into a real value.

        Uses formula:
            (vref/(2**adc_bits) )*adc_value
        """

        return (vref/(2**adc_bits))*adc_value

    def convert_2d_array_adc_values(self, data, indexes, exclude=False, vref=3.19, adc_bits=12):
        """Converts a 2D array to digital values according to conert_from_adc_value(). This is a macro function."""

        # print(len(data))
        for row, data_line in enumerate(data):
            for index, data_cell in enumerate(data_line):
                if exclude:
                    if index not in indexes:
                        # print(data[row][index])
                        data[row][index] = self.convert_from_adc_value(int(data[row][index]), vref, adc_bits) * 1000
                else:
                    if index in indexes:
                        data[row][index] = self.convert_from_adc_value(data[row][index], vref, adc_bits)

        return data

    def calculate_beta(self, ib, ic):
        """"Calculate beta. Used instead of calculate_current_gain() if currents are already known.
        """
        beta = ib/ic
        return beta

    def curve_fit(self, beta_values, x_values, function):
        """Curve fitting for beta values and temperature."""
        params, params_covariance = optimize.curve_fit(function, x_values, beta_values)
        # print(params)
        # print(params_covariance)
        return params

    def extract_data_from(self, custom_data, x_value):
        """Extracts data from custom data"""

        beta_values = []
        x_values = []
        rotate = False

        # Extract beta values
        for data in custom_data:
            beta_values.append(data[2])
            if x_value == 'temp':
                x_values.append(data[3])
            else:
                rotate = True
                x_values.append(data[0])

        return beta_values, x_values

    def make_sub_graph(self, custom_data, x_value, title, x_label, y_label, plot_type):
        """Creates a standalone graph from the custom data for the SiC in space project

                Parameter x_value = 'temp' or 'time' """

        beta_values = []
        x_values = []
        rotate = False

        # Extract beta values
        for data in custom_data:
            beta_values.append(data[2])
            if x_value == 'temp':
                x_values.append(data[3])
            else:
                rotate = True
                x_values.append(data[0])

        self.make_standalone_graph(beta_values, x_values, title, x_label, y_label, plot_type, rotate)

        # plt.plot(x_values, beta_values, plot_type)
        # plt.title(title)
        # plt.ylabel(y_label)
        # plt.xlabel(x_label)

    def make_graph(self, custom_data, x_value, title, x_label, y_label, plot_type):
        """Creates a standalone graph from the custom data for the SiC in space project

        Parameter x_value = 'temp' or 'time' """

        beta_values = []
        x_values = []

        # Extract beta values
        for data in custom_data:
            beta_values.append(data[2])
            if x_value == 'temp':
                x_values.append(data[3])
            else:
                x_values.append(data[0])

        # self.make_standalone_graph(beta_values, x_values, title, x_label, y_label, plot_type)

        plt.plot(x_values, beta_values, plot_type)
        plt.title(title)

        if x_value == 'time':
            plt.xticks(x_values, x_values, rotation='vertical')

        plt.ylabel(y_label)
        plt.xlabel(x_label)

    def make_standalone_graph(self, list_of_beta_values, list_of_x_values, title, x_label, y_label, plot_type, rotate=False, figure=1):
        """"Creates a subplot with the specified input"""
        plt.figure(figure)

        #print(self.figure_sub_plots)
        if figure not in self.figure_sub_plots:
            self.figure_sub_plots[figure] = 1
        else:
            self.figure_sub_plots[figure] += 1

        #print(self.figure_sub_plots[figure])
        plt.subplot(self.graph_rows, self.graph_cols, self.figure_sub_plots[figure])
        plt.plot(list_of_x_values, list_of_beta_values, plot_type)
        plt.title(title)
        plt.ylabel(y_label)
        plt.xlabel(x_label)

        if rotate:
            plt.xticks(list_of_x_values, list_of_x_values, rotation='vertical')

        #self.current_graph += 1

    def combine_graphs(self, beta_values, x_values, x_identifier, title, x_label, y_label, plot_types, label_1='SiC', label_2='Si'):
        """ Shows a graph that is combined for two lists of data.
        :arg beta_values = [ custom_data for SiC, custom_data for Si ]. Y values.
        :arg x_values = [ x values for SiC, x values for Si]. X values.
        :arg x_identifier. If 'time', rotate x labels 90 degrees.
        :arg title. Title of plot.
        :arg x_label. Label for x axis. Usually 'Deg C' or 'Time'
        :arg y_label. Label for y axis. Usually 'Beta'
        :arg plot_types = [ plot_type for SiC, plot_type for Si ]. Specified labels.
        :arg label_1. Label for SiC
        :arg label_2. Label for Si
        """
        # dh.combine_graphs([sic_beta, si_beta], [sic_x_values, si_x_values], config[1]['x_axis'], 'Beta values over temperature', 'Deg C', 'Beta',
        #                   [sic_plot_type, si_plot_type])
        rotate = False
        if x_identifier == 'time':
            rotate = True

        # print(beta_values)
        # print(x_values)
        plt.subplot(self.graph_rows, self.graph_cols, self.current_graph)
        plt.plot(x_values[0], beta_values[0], plot_types[0], label=label_1)
        plt.plot(x_values[1], beta_values[1], plot_types[1], label=label_2)
        plt.title(title)
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.legend()

        if rotate:
            plt.xticks(x_values[0], x_values[0], rotation='vertical')
            plt.xticks(x_values[1], x_values[1], rotation='vertical')

        self.current_graph += 1

    def multi_graph_plot_in_graph(self, x_values, y_values, plot_types, labels, figure=1):
        """Create a graph with multiple plots.
        x_values = 2D array
        y_values = 2D array
        plot_types = 1D array
        labels = 1D array

        The argument lengths must match.
         """
        
        plt.figure(figure)
        if figure not in self.figure_sub_plots:
            self.figure_sub_plots[figure] = 1
        else:
            self.figure_sub_plots[figure] += 1

        #print(self.figure_sub_plots[figure])
        plt.subplot(self.graph_rows, self.graph_cols, self.figure_sub_plots[figure])


        for i, x_value in enumerate(labels): # Basically, I was just to tired to solve this any other way
            # print(f'x: {len(x_values)}, y:{len(y_values)}, i: {i}')
            plt.plot(x_values[i], y_values[i], plot_types[i], label=labels[i])

    def set_plot_info(self, title, x_label, y_label, legend=False):
        """Sets the information of title, x axis and y axis. If 'legend' is True, sets legends."""
        plt.title(title)
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        if legend:
            plt.legend()

    def make_combined_graph(self, list_of_beta_values, list_of_x_values, title, x_label, y_label, plot_type, rotate=False):
        pass

    def show_graphs(self):
        plt.show()

    def parse_plt_type(self, color, config):
        """Parses the plt type of the config. Works on both 'Si' and 'SiC' data."""
        string_builder = ''
        # print(color)
        if not isinstance(color, str):
            raise TypeError(f'color is not of type "str", received type {type(color)}')
        elif color == 'blue':
            string_builder += 'b'
        elif color == 'red':
            string_builder += 'r'
        elif color == 'green':
            string_builder += 'g'
        else:
            raise ValueError("color is not a string with value: 'blue', 'red' or 'green'")

        if not isinstance(config['dotted'], str):
            raise TypeError(f'config["dotted"] not a string, config["dotted"] = {type(config["dotted"])}')
        elif config['dotted'] == 'True':
            string_builder += 'o'

        if not isinstance(config['lines'], str):
            raise TypeError(f'config["lines"] not a string, config["dotted"] = {type(config["lines"])}')
        elif config['lines'] == 'True':
            string_builder += '-'

        return string_builder

    def make_combined_plot(self, x_values_1, y_values_1, plt_type_1, x_values_2, y_values_2, plt_type_2):
        """Combines two plots into a single graph"""
        plt.plot(x_values_1, y_values_1, plt_type_1, x_values_2, y_values_2, plt_type_2)

    def parse_csv_data(self, data):
        """"Parses csv data by creating a list which matches the values with each other.
        
        Will not generate proper data if any of the headers are missing
        Data will be in the order of: time, Ube, Uc, Ub, Temp"""  # TODO Fix this description
        # Voltage values should be sorted by 'time', 'Ube', 'Uc', 'Ub', 'Temp'
        sic_indexes = [0, 0, 0, 0, 0]
        si_indexes = [0, 0, 0, 0, 0]
        sic_values = []
        si_values = []
        # print(data)

        # Check the header for proper header strings and extract positions.
        for index, header in enumerate(data[0]):
            if not isinstance(header, str):
                raise TypeError("Header is not a string")
            header = header.lower()
            if "time" in header:
                sic_indexes[0] = index
                si_indexes[0] = index
            elif "sic" in header:
                if "ube" in header:
                    sic_indexes[1] = index
                elif "uc" in header:
                    sic_indexes[2] = index
                elif "ub" in header:
                    sic_indexes[3] = index
                elif "temp" in header:
                    sic_indexes[4] = index
            elif "si" in header:
                if "ube" in header:
                    si_indexes[1] = index
                elif "uc" in header:
                    si_indexes[2] = index
                elif "ub" in header:
                    si_indexes[3] = index
                elif "temp" in header:
                    si_indexes[4] = index

        for index, value in enumerate(sic_indexes):
            for index_2, value_2 in enumerate(sic_indexes):
                #print(data[0][sic_indexes[0]])
                if index != index_2 and value == value_2:
                    raise ValueError(f'Headers has the same index value at {index} and {index_2}. This is usually due to a missing header or wrong CSV delimiter')

        for index, value in enumerate(si_indexes):
            for index_2, value_2 in enumerate(si_indexes):
                if index != index_2 and value == value_2:
                    raise ValueError(f'Headers has the same index value at {index} and {index_2}. This is usually due to a missing header or wrong CSV delimiter')

        row_length = len(data[0])
        for index, values in enumerate(data):
            if len(values) != row_length:
                raise ValueError(f'Row at index {index} is not the same length as header row (first row)')
            if index != 0:
                temp_sic = []
                temp_si = []

                temp_sic.append(values[sic_indexes[0]])  # Time
                temp_si.append(values[si_indexes[0]])  # Time

                temp_sic.append(values[sic_indexes[1]])  # Ube
                temp_si.append(values[si_indexes[1]])  # Ube

                temp_sic.append(values[sic_indexes[2]])  # Uc
                temp_si.append(values[si_indexes[2]])  # Uc

                temp_sic.append(values[sic_indexes[3]])  # Ub
                temp_si.append(values[si_indexes[3]])  # Ub

                temp_sic.append(values[sic_indexes[4]])  # Temp
                temp_si.append(values[si_indexes[4]])  # Temp

                sic_values.append(temp_sic)
                si_values.append(temp_si)

        # print(sic_values)
        # print(si_values)
        return sic_values, si_values

    def sort_by_value_at_index(self, data, temperature_index=4):
        """Sorts parsed data by temperature

        temperature_index is the index in the second layer of a 2D array that represents temperature"""
        # print(sic_data)
        sorted_sic_list = sorted(data, key=lambda x: x[temperature_index])
        sorted_sic_list.reverse()
        return sorted_sic_list

    def convert_data_to_float(self, data, index_pos, data_format):
        """"Converts data in a 2D array into ints. Only converts the data at specified indexes in the second layer.
        If data contains floats, data_format can not be "hex"

        Example:
            list = [['string', '2', 'string', '3', 'a', '4'], ['string', '5', 'string', '6', 'string', '7']
            indexes_to_convert = [1, 3, 5]
            convert_data_to_int(list, indexes_to_convert)

            Returns:
                [['string', 2, 'string', 3, 'a', 4], ['string', 5, 'string', 6, 'string', 7]]
        """
        for cell_index, cell_data in enumerate(data):
            for index in index_pos:
                if data_format == "hex":
                    if '.' in data[cell_index][index]:
                        raise TypeError("Hexadecimal numbers specified. Illegal type 'float'. (There is a dot('.') in a data field somewhere)")
                    data[cell_index][index] = int(cell_data[index], 0)
                else:
                    data[cell_index][index] = float(cell_data[index])
        return data

    def calculate_temperature(self, mv, decimals=2):
        """Calculates the temperature from the voltage reading of a LMT85dckt with the formula
        (8.194 - math.sqrt((-8.192) ** 2 + 4 * 0.00262 * (1324 - mv))) / (2 * -0.00262) + 30

        Rounds the temperature to the sef "decimals" parameter, defaults to 2 decimals
        """
        temperature = round((8.194 - math.sqrt((-8.192) ** 2 + 4 * 0.00262 * (1324 - mv))) / (2 * -0.00262) + 30, decimals)
        return temperature

    def average_temperature_data(self, data, temperature_index, index_to_average):
        """Averages the data points which has the same temperature value. Due to time-stamping, sets the value at each
        data point to be the same rather than merging them into one data point.

        This method is not used for anything since the curvefit of SciPy can handle multiple y values for a single x
        value.

        Example:
            sic_data = [[XXXXX, 2, 200, 149], [XXXXX, 2, 210, 149], [XXXXX, 2, 190, 140], [XXXXX, 2, 187, 120]]

            returns:
                sic_data = [[XXXXX, 2, 205, 149], [XXXXX, 2, 205, 149], [XXXXX, 2, 190, 149], [XXXXX, 2, 187, 149]]
                # The beta value is the same for the data points which shared temperature, which is the average of
                # all data points with the same temperature.
        """

        list_of_indexs_to_average = {}
        for index, data_line in enumerate(data):
            # print(data_line)
            temperature = data_line[temperature_index]
            if temperature in list_of_indexs_to_average:
                list_of_indexs_to_average[temperature][0] += data_line[index_to_average]  # Value of data summed
                list_of_indexs_to_average[temperature][1] += 1  # Number of times the same temperature has appeared
                list_of_indexs_to_average[temperature][2].append(index)  # Index of each data
            else:
                list_of_indexs_to_average[temperature] = [data_line[index_to_average], 1, [index]]
                # print(list_of_indexs_to_average)

        for k in list_of_indexs_to_average:
            # print(list_of_indexs_to_average[k])
            mean_value = list_of_indexs_to_average[k][0] / list_of_indexs_to_average[k][1]
            for index in list_of_indexs_to_average[k][2]:
                data[index][index_to_average] = mean_value

        return data

    def look_up_temperature_in_lut(self, data, temperature_index=4, filename="../LMT85_LookUpTableCSV.csv"):
        """Attempts to find a matching value in the LUT. If no matching value is found it chooses whichever value is
        closest

        This function changes the values in the object that is passed to it.
        """
        fh = FileHandler()
        lut_content = fh.readCSV(filename, 'int', False)

        # print(self.search_2d_temperature_tree(lut_content, 1, 716))
        last_length = len(data[0])
        for index, value in enumerate(data):
            if last_length != len(value) or temperature_index > len(value) + 1:
                raise IndexError("Columns are not the same across all rows")
            # Find nearest voltage level
            if isinstance(value, float):
                value = round(value)

            temp = self.search_2d_temperature_tree(lut_content, 1, int(value[temperature_index]))
            # print(f'{lut_content[temp+50][1] - int(value[temperature_index])}')
            if abs(lut_content[temp+50][1] - int(value[temperature_index]) > 5):
                print(f'Searched for: {value[temperature_index]}, Return value: {temp}')
            data[index][temperature_index] = temp

        return data

    def search_2d_temperature_tree(self, temperature_data, index_pos_of_second_layer, target, max_jumps=12):
        """"Looks up a value in a LUT. If the specific value can not be found it returns the closest value that can be
        found. This is a support function for look_up_temperature_in_lut().

        The variable jumps in search_2d_temp_recursion() limits the amount of times the function can try to find the
        target value. It is currently set to 10 which is enough for the specific LUT used in this project.
        Should you use a bigger list, it might be worthwhile to change the condition of return.
        The max number of jumps should be slighty higher than log2(length_of_data_list) since this method could potentially
        take slightly longer than O(log(n)).

        Returns matching temperature data
        or None"""
        # print(f'{temperature_data[0][index_pos_of_second_layer]} < {target}')
        # print(f'{temperature_data[-1][index_pos_of_second_layer]} > {target}')

        if temperature_data[0][index_pos_of_second_layer] == target:  # Handle edge-case scenario
            return temperature_data[0][0]
        elif temperature_data[-1][index_pos_of_second_layer] == target:
            return temperature_data[-1][0]

        if temperature_data[0][index_pos_of_second_layer] < target or temperature_data[-1][index_pos_of_second_layer] > target:
            # print("Requested temperature is outside of temperature LUT")
            raise ValueError(f'Requested value "{target}" is outside of temperature LUT range')
        else:
            return self.search_2d_temp_recursion(temperature_data, index_pos_of_second_layer, target, len(temperature_data)//2, len(temperature_data) - 1, 0, 0, max_jumps)

    def search_2d_temp_recursion(self, temperature_data, index_pos_of_second_layer, target, current_index, upper_bound,
                                 lower_bound, jumps, max_jumps):
        """Binary search function. Use search_2d_temperature_tree() instead since it is basically the same but with
        edge-case handling. If this function is used directly there is a small chance that the edges of the list
        is not found due to index constraints in this method."""
        temp_temperature = temperature_data[current_index][index_pos_of_second_layer]
        # print(f'Holding temperature: {temp_temperature}, searching for: {target}    Upper bound: {upper_bound},'
        #       f' lower bound: {lower_bound}'
        #       f'    Upper value: {temperature_data[upper_bound][index_pos_of_second_layer]}, '
        #       f'lower value: {temperature_data[lower_bound][index_pos_of_second_layer]}')
        jumps += 1

        if temp_temperature == target:
            return temperature_data[current_index][0]

        if temperature_data[current_index-1][index_pos_of_second_layer] > target > temperature_data[current_index + 1][index_pos_of_second_layer]:
            # print(temp_temperature)
            current_difference = abs(temp_temperature - target)
            lower_difference = abs(temperature_data[current_index-1][index_pos_of_second_layer] - target)
            upper_difference = abs(temperature_data[current_index+1][index_pos_of_second_layer] - target)
            # print(f'lower = {lower_difference}  upper = {upper_difference}  current = {current_difference}      Current index = {current_index}')

            if current_difference <= lower_difference and current_difference <= upper_difference:
                return temperature_data[current_index][0]
            elif upper_difference <= lower_difference and upper_difference <= current_difference:
                return temperature_data[current_index+1][0]
            elif lower_difference <= upper_difference and lower_difference <= current_difference:
                return temperature_data[current_index-1][0]

        elif jumps == max_jumps:
            return

        elif temp_temperature > target:
            next_index = (upper_bound+current_index)//2
            next_lower_bound = current_index
            return self.search_2d_temp_recursion(temperature_data, index_pos_of_second_layer, target, next_index, upper_bound, next_lower_bound, jumps, max_jumps)
        elif temp_temperature < target:
            next_index = (lower_bound+current_index)//2
            next_upper_bound = current_index
            return self.search_2d_temp_recursion(temperature_data, index_pos_of_second_layer, target, next_index, next_upper_bound, lower_bound, jumps, max_jumps)




if __name__ == "__main__":
    test_time_stamp = ["2019-12-17 13:05:19.127398",
                       "2019-12-17 13:05:19.128395",
                       "2019-12-17 13:05:19.128395",
                       "2019-12-17 13:05:19.129392",
                       "2019-12-17 13:05:19.129392",
                       "2019-12-17 13:05:19.130389",
                       "2019-12-17 13:05:19.130389",
                       "2019-12-17 13:05:19.131387"]

    test_sic_beta = [1,2,3,4,5,6,7,8]
    test_sic_temp = [20,22,23,24,25,26,27,29]

    test_si_beta = [1,2,3,4,5,6,7,8]
    test_si_temp = [20,22,23,24,25,26,27,29]

    fh = FileHandler()
    config = fh.readConfig()
    # print(config[0])

    dh = DataHandler()

    # print(config)
    if config[1]['combined'] == 'True':
        sic_plot_type = dh.parse_plt_type(config[1]['sic_color'], config[1])
        si_plot_type = dh.parse_plt_type(config[1]['si_color'], config[1])
        # print(sic_plot_type)
        # print(si_plot_type)
        # dh.make_combined_plot(test)
        # plt.plot(test_sic_temp, test_sic_beta, )

        catch = fh.readCSV("../test_files/test_data.csv", 'str', True, ',')
        sic_data, si_data = dh.parse_csv_data(catch)
        # print(sic_data)
        sic_data = dh.look_up_temperature_in_lut(sic_data)
        si_data = dh.look_up_temperature_in_lut(si_data)
        # print(sic_data)
        sic_data = dh.convert_data_to_int(sic_data, [1, 2, 3])
        si_data = dh.convert_data_to_int(si_data, [1, 2, 3])
        # print(sic_data)

        # time, Ube, Uc, Ub, Temp
        sic_beta = []
        si_beta = []
        for data_line in sic_data:
            temp_sic_beta = []
            temp_sic_beta.append(data_line[0])
            temp_sic_beta.append(data_line[1])
            temp_sic_beta.append(dh.calculate_current_gain(data_line[3], config[0]['r1'], data_line[2], config[0]['r2']))
            temp_sic_beta.append(data_line[4])
            sic_beta.append(temp_sic_beta)

        for data_line in si_data:
            temp_si_beta = []
            temp_si_beta.append(data_line[0])
            temp_si_beta.append(data_line[1])
            temp_si_beta.append(dh.calculate_current_gain(data_line[3], config[0]['r3'], data_line[2], config[0]['r4']))
            temp_si_beta.append(data_line[4])
            si_beta.append(temp_si_beta)

        # print(sic_beta)
        sic_beta = dh.sort_by_value_at_index(sic_beta, 3)
        si_beta = dh.sort_by_value_at_index(si_beta, 3)
        # dh.make_graph(sic_beta, 'temp', 'SiC beta values', 'Deg C', 'Beta', sic_plot_type)

        dh.combine_graphs([sic_beta, si_beta], 'temp', 'Beta values over temperature', 'Deg C', 'Beta', [sic_plot_type, si_plot_type])
        # dh.make_sub_graph(sic_beta, 'temp', 'SiC beta values', 'Deg C', 'Beta', sic_plot_type)
        # dh.make_sub_graph(si_beta, 'temp', 'Si Beta values', 'Deg C', 'Beta', si_plot_type)
        dh.show_graphs()


        # dh.sort_by_value_at_index(sic_data)



    # dh.make_standalone_graph(test_sic_beta, test_sic_temp, 'SiC', "Deg C", "Beta", 'o-') # Test adding SiC plot
    # dh.make_standalone_graph(test_sic_beta, test_time_stamp, 'SiC', "Time", "Beta", 'o-') # Test adding SiC plot
    #
    # dh.make_standalone_graph(test_si_beta, test_si_temp, 'Si', "Deg C", "Beta", 'ro-') # Test adding SiC plot
    # dh.make_standalone_graph(test_si_beta, test_time_stamp, 'Si', "Deg C", "Beta", 'ro-') # Test adding SiC plot
    # dh.show_graphs()


#
#
# x1 = np.linspace(0.0, 5.0)
# x2 = np.linspace(0.0, 2.0)
#
# y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
# y2 = np.cos(2 * np.pi * x2)
#
# plt.subplot(2, 2, 1)
# plt.plot(x1, y1, 'o-')
# plt.title('A tale of 2 subplots')
# plt.ylabel('Damped oscillation')
#
# plt.subplot(2, 2, 2)
# plt.plot(x2, y2, '.-')
# plt.xlabel('time (s)')
# plt.ylabel('Undamped')
#
# plt.subplot(2, 2, 3)
# plt.plot(x2, y2, '.-')
# plt.xlabel('time (s)')
# plt.ylabel('Undamped')
#
# plt.subplot(2, 2, 4)
# plt.plot(x1, y1, 'o-')
# plt.title('A tale of 2 subplots')
# plt.ylabel('Damped oscillation')
#
#
# plt.show()