import csv
import os

class FileHandler:
    """Handles parsing of files"""
    def readRaw(self, filename):
        """"Reads a file and returns the raw data contained in the file
        """
        if not isinstance(filename, str):
            raise TypeError("Filename is not a string")

        with open(filename) as file:
            data = file.read()

            return data

    def readCSV(self, filename='../test_files/LMT85_LookUpTableCSV.csv', data_format='str', header=True, delimiter_arg = ';'):
        """"Read a CSV file regardless of how many arguments per row. First row in the CSV should be the type identifier and all following lines should be data

        'data_format' can be either of these types: int, float or str. If no format is specified, str is assumed.
        'header' flags the first row as title columns. If set to false, all values will be converted to 'data_format'

        Hex values are untested in this method #WIP

        All empty rows are ignored

        Return data will be in the form of a 2D array.
        Example:
            A CSV file contains the following lines
            Ube, Uce, Temp
            5, 1, 25
            3, 2.3, 22
            11, 15, 100

            And the function is called with no additional parameters.

            The function will return:
            [['Ube', 'Uce', 'Temp'],
             ['5', '1', '25'],
             ['3', '2.3', '22'],
             ['11', '15', '100']]
        """
        valid_types = ['int', 'str', 'float', 'hex']

        if not isinstance(filename, str):
            raise TypeError("Filename is not a string")
        if not isinstance(data_format, str) or data_format not in valid_types:
            raise TypeError(f'data_format: {data_format} is not in list of valid types.')

        data = []
        first_row = True
        # print(os.getcwd())
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=delimiter_arg)
            for row in csv_reader:
                # Gather data in a list
                row_data = []

                # Convert first row to the correct data format if header is false
                if first_row and header == True:
                    first_row = False
                    for l in range(len(row)):
                        row_data.append(row[l])
                else:
                    for l in range(len(row)):
                        if data_format == 'int' or data_format == 'hex':
                            row_data.append(int(row[l], 0))
                        elif data_format == 'float':
                            row_data.append(float(row[l]))
                        else:
                            row_data.append(row[l])

                if row_data:
                    data.append(row_data)
        return data

    def readConfig(self, file_path):
        """"Parses the config file"""
        config = self.readRaw(file_path)
        config = config.split("\n")

        resistor_values = {}
        graph_settings = {}

        resistor_values_found = False
        graph_settings_found = False

        for line in config:
            if line:  # Skip all empty lines
                if line[0] != "#":  # Skip all commented lines
                    if line == "//Resistor values" or resistor_values_found and line != "//Resistor end":  # Find resistor values
                        resistor_values_found = True
                        if line != "//Resistor values":
                            resistor = line.split(" ")
                            multiplier = 1
                            if len(resistor) > 3:
                                if resistor[3] == 'k':
                                    multiplier = 1000
                                elif resistor[3] == 'M':
                                    multiplier = 1000000

                            resistor_values[resistor[0]] = int(resistor[2]) * multiplier
                    elif line == "//Graph settings" or graph_settings_found and line != "//End graph":  # Find graph settings
                        graph_settings_found = True
                        if line != "//Graph settings":
                            graph_setting = line.split(" ")
                            graph_settings[graph_setting[0]] = graph_setting[2]
                    elif line.split(" ")[0] == 'filename':
                        graph_settings['filename'] = line.split(" ")[2]
                    else:
                        resistor_values_found = False
                        graph_settings_found = False

        return resistor_values, graph_settings

    def write_data(self, data, headers, filename='data_dump.csv'):
        with open(filename, 'w', newline='') as file:
            wr = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=';')
            wr.writerow(headers)
            for line in data:
                wr.writerow(line)


if __name__ == "__main__":
    fh = FileHandler()
    resistor, graph_settings = fh.readConfig()
    for k in resistor:
        print(f'{k} => {resistor[k]}')
    for k in graph_settings:
        print(f'{k} => "{graph_settings[k]}"')
    # print(fh.readCSV('LMT85_LookUpTableCSV.csv', 'int', False))
