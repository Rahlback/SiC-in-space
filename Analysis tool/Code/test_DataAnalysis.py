import unittest
from DataAnalysis import DataHandler


class DataAnalysisTest(unittest.TestCase):

    def setUp(self):
        self.dh = DataHandler()
        self.config = ({'r1': 100, 'r2': 100000, 'r3': 9000, 'r4': 3000},
                  {'sic_color': 'green', 'si_color': 'green', 'dotted': 'True', 'lines': 'True', 'combined': 'True'})

    def test_convert_data_to_float(self):
        test_list = [['string', '2', 'string', '3', 'a', '4'], ['string', '5', 'string', '6', 'string', '7']]
        indexes_to_convert = [1, 3, 5]
        returned_list = self.dh.convert_data_to_float(test_list, indexes_to_convert, 'decimal')
        self.assertEqual(returned_list, [['string', 2, 'string', 3, 'a', 4], ['string', 5, 'string', 6, 'string', 7]])

    def test_convert_data_to_float_from_float(self):
        test_list = [['string', '0.7', 'string', '3', 'a', '4'], ['string', '5', 'string', '6', 'string', '7']]
        indexes_to_convert = [1, 3, 5]
        returned_list = self.dh.convert_data_to_float(test_list, indexes_to_convert, 'decimal')
        self.assertEqual(returned_list, [['string', 0.7, 'string', 3.0, 'a', 4.0], ['string', 5.0, 'string', 6.0, 'string', 7.0]])

    def test_convert_data_to_float_from_hex(self):
        """Tests if it is possible to convert a string formatted like a hexadecimal number into integers"""
        test_list = [['string', '0x1', 'string', '3', 'a', '4'], ['string', '0x5', 'string', '6', 'string', '0xff']]
        indexes_to_convert = [1, 3, 5]
        returned_list = self.dh.convert_data_to_float(test_list, indexes_to_convert, 'hex')
        expected_list = [['string', 1, 'string', 3, 'a', 4], ['string', 5, 'string', 6, 'string', 255]]
        self.assertEqual(returned_list, expected_list)

    def test_convert_data_to_float_from_hex_and_float(self):
        """Tests if TypeError is raised when trying to convert a string formatted like a hexadecimal number when
        floats are in the data."""
        test_list = [['string', '0x1', 'string', '3', 'a', '4'], ['string', '0x5', 'string', '6.2', 'string', '0xff']]
        indexes_to_convert = [1, 3, 5]
        # returned_list = self.dh.convert_data_to_float(test_list, indexes_to_convert, 'hex')
        # expected_list = [['string', 1, 'string', 3, 'a', 4], ['string', 5, 'string', 6, 'string', 255]]
        with self.assertRaises(TypeError): self.dh.convert_data_to_float(test_list, indexes_to_convert, 'hex')

    def test_look_up_temperature_in_lut_correct_returns(self):
        """This function reads a predefined lookup table, should call an error if the file can not be found.

        Wrong temperature_index is not testable unless it points to a string containing letters.
        """
        data = [['string', 'temperature', 756, 'false', 5],
                ['string', 'temperature', 1955, 'false', 5],  # Highest value
                ['string', 'temperature', 301, 'false', 5],  # Lowest value
                ['string', 'temperature', 1831, 'false', 5]]
        temperature_index = 2

        expected_data = [['string', 'temperature', 98, 'false', 5],
                ['string', 'temperature', -50, 'false', 5],  # Highest value
                ['string', 'temperature', 150, 'false', 5],  # Lowest value
                ['string', 'temperature', -33, 'false', 5]]
        self.assertEqual(self.dh.look_up_temperature_in_lut(data, temperature_index), expected_data)

        data_with_strings = [['string', 'temperature', '756', 'false', 5],
                ['string', 'temperature', '1955', 'false', 5],  # Highest value
                ['string', 'temperature', '301', 'false', 5],  # Lowest value
                ['string', 'temperature', '1831', 'false', 5]]
        temperature_index = 2
        self.assertEqual(self.dh.look_up_temperature_in_lut(data_with_strings, temperature_index), expected_data)

    def test_look_up_temperature_corrupt_data(self):
        corrupted_data = [['stirng', '2a', 'f', 'aw', 'a'], ['stirng', '2a', 'f', 'aw', 'a']]
        temperature_index = 1
        with self.assertRaises(ValueError): self.dh.look_up_temperature_in_lut(corrupted_data, temperature_index)

    def test_look_up_temperature_1d_array(self):
        non_2d_array = ['string', '2', '3', '4', '5', '6']
        with self.assertRaises(ValueError): self.dh.look_up_temperature_in_lut(non_2d_array, 1)

    def test_look_up_temperature_floats(self):
        floats_in_data = [['string', 'temperature', 756.6, 'false', 5],
                ['string', 'temperature', 1955.1, 'false', 5],  # Highest value
                ['string', 'temperature', 301.2, 'false', 5],  # Lowest value
                ['string', 'temperature', 1831.7, 'false', 5]]
        temperature_index = 2
        expected_data = [['string', 'temperature', 98, 'false', 5],
                ['string', 'temperature', -50, 'false', 5],  # Highest value
                ['string', 'temperature', 150, 'false', 5],  # Lowest value
                ['string', 'temperature', -33, 'false', 5]]
        self.assertEqual(self.dh.look_up_temperature_in_lut(floats_in_data, temperature_index), expected_data)

    def test_look_up_temperature_row_lengths(self):
        # Number of columns is not the same in all rows
        data = [[1000, 1001, 1002, 1003, 1004, 1005], [1000, 1002, 1003, 1004, 1005, 1006],
                [1000, 1002, 1003, 1004], [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009]]
        with self.assertRaises(IndexError): self.dh.look_up_temperature_in_lut(data)

    def test_look_up_temperature_tuples(self):
        tuple_data = ((234, 234, 324, 234, 234, 234), (234, 234, 324, 234, 234, 234), (234, 234, 324, 234, 234, 234),
                      (234, 234, 324, 234, 234, 234))
        with self.assertRaises(TypeError): self.dh.look_up_temperature_in_lut(tuple_data, 2)

    def test_sort_by_value_at_index_return_correct_values(self):
        data = [['string', 'temperature', 756, 'false', 5],
                ['string', 'temperature', 1955, 'false', 5],  # Highest value
                ['string', 'temperature', 301, 'false', 5],  # Lowest value
                ['string', 'temperature', 1831, 'false', 5]]
        expected_data = [
            ['string', 'temperature', 301, 'false', 5],
            ['string', 'temperature', 756, 'false', 5],
            ['string', 'temperature', 1831, 'false', 5],
            ['string', 'temperature', 1955, 'false', 5]
        ]
        expected_data.reverse()
        self.assertEqual(self.dh.sort_by_value_at_index(data, 2), expected_data)

    def test_sort_by_value_at_index_out_of_bounds(self):
        data = [['string', 'temperature', 756, 'false', 5],
                ['string', 'temperature', 1955, 'false', 5],  # Highest value
                ['string', 'temperature', 301, 'false', 5],  # Lowest value
                ['string', 'temperature', 1831, 'false', 5]]
        with self.assertRaises(IndexError): self.dh.sort_by_value_at_index(data, 6)

    def test_parse_csv_data_correct_return(self):
        data = [['time', ' sic ube', ' sic uc', ' sic ub', ' sic temp', ' si ube', ' si ub', ' si uc', ' si temp'],
                ['2019-12-18 16:43:56.452686', '2', '9', '7', '643', '0.7', '0', '5', '455'],
                ['2019-12-18 17:43:56.452686', '2', '5', '8', '1942', '0.7', '5', '6', '782'],
                ['2019-12-18 18:43:56.452686', '2', '0', '7', '716', '0.7', '7', '8', '545'],
                ['2019-12-18 19:43:56.452686', '2', '7', '3', '654', '0.7', '2', '1', '443'],
                ['2019-12-18 20:43:56.452686', '2', '9', '4', '1706', '0.7', '6', '6', '424']]

        sic_expected_data = [['2019-12-18 16:43:56.452686', '2', '9', '7', '643'], ['2019-12-18 17:43:56.452686', '2', '5', '8', '1942'],
                             ['2019-12-18 18:43:56.452686', '2', '0', '7', '716'], ['2019-12-18 19:43:56.452686', '2', '7', '3', '654'],
                             ['2019-12-18 20:43:56.452686', '2', '9', '4', '1706']]

        si_expected_data = [['2019-12-18 16:43:56.452686', '0.7', '5', '0', '455'], ['2019-12-18 17:43:56.452686', '0.7', '6', '5', '782'],
                            ['2019-12-18 18:43:56.452686', '0.7', '8', '7', '545'], ['2019-12-18 19:43:56.452686', '0.7', '1', '2', '443'],
                            ['2019-12-18 20:43:56.452686', '0.7', '6', '6', '424']]

        sic_data, si_data = self.dh.parse_csv_data(data)

        self.assertEqual(sic_data, sic_expected_data)
        self.assertEqual(si_data, si_expected_data)

    def test_parse_csv_data_corrupt_header_string(self):
        corrupt_data = [['no', 'should be vbe', ' sic uc', ' sic ub', ' sic temp', ' si ube', ' si ub', ' si uc', ' si temp'],
                ['2019-12-18 16:43:56.452686', '2', '9', '7', '643', '0.7', '0', '5', '455'],
                ['2019-12-18 17:43:56.452686', '2', '5', '8', '1942', '0.7', '5', '6', '782'],
                ['2019-12-18 18:43:56.452686', '2', '0', '7', '716', '0.7', '7', '8', '545'],
                ['2019-12-18 19:43:56.452686', '2', '7', '3', '654', '0.7', '2', '1', '443'],
                ['2019-12-18 20:43:56.452686', '2', '9', '4', '1706', '0.7', '6', '6', '424']]
        with self.assertRaises(ValueError): self.dh.parse_csv_data(corrupt_data)

    def test_parse_csv_data_corrupt_header_with_int(self):
        corrupt_data = [[1, 'should be vbe', ' sic uc', ' sic ub', ' sic temp', ' si ube', ' si ub', ' si uc', ' si temp'],
                ['2019-12-18 16:43:56.452686', '2', '9', '7', '643', '0.7', '0', '5', '455'],
                ['2019-12-18 17:43:56.452686', '2', '5', '8', '1942', '0.7', '5', '6', '782'],
                ['2019-12-18 18:43:56.452686', '2', '0', '7', '716', '0.7', '7', '8', '545'],
                ['2019-12-18 19:43:56.452686', '2', '7', '3', '654', '0.7', '2', '1', '443'],
                ['2019-12-18 20:43:56.452686', '2', '9', '4', '1706', '0.7', '6', '6', '424']]
        with self.assertRaises(TypeError): self.dh.parse_csv_data(corrupt_data)

    def test_parse_csv_data_row_length(self):
        data = [['time', ' sic ube', ' sic uc', ' sic ub', ' sic temp', ' si ube', ' si ub', ' si uc', ' si temp'],
                ['2019-12-18 16:43:56.452686', '2', '9', '7', '643', '0.7', '0', '5', '455'],
                ['2019-12-18 17:43:56.452686', '2', '5', '8', '1942', '0.7', '5', '6', '782'],
                ['2019-12-18 18:43:56.452686', '2', '0', '7', '716', '0.7', '7', '8', '545'],
                ['2019-12-18 19:43:56.452686', '2', '7', '3', '654', '0.7', '2', '1', '443'],
                ['2019-12-18 20:43:56.452686', '2', '9', '4', '1706', '0.7', '6', '424']]
        with self.assertRaises(ValueError): self.dh.parse_csv_data(data)
    
    def test_parse_plt_type_correct_return_value(self):
        resistor_values = self.config[0]
        graph_settings = self.config[1]
        
        expected_sic_plt = 'go-'
        expected_si_plt = 'go-'
        
        self.assertEqual(self.dh.parse_plt_type(graph_settings['sic_color'], graph_settings), expected_sic_plt)
        self.assertEqual(self.dh.parse_plt_type(graph_settings['si_color'], graph_settings), expected_si_plt)
    
    def test_parse_plt_type_color_wrong_type(self):
        graph_settings = self.config[1]
        with self.assertRaises(ValueError): self.dh.parse_plt_type('orange', graph_settings)
        with self.assertRaises(TypeError): self.dh.parse_plt_type(1, graph_settings)
    
    def test_parse_plt_type_missing_keys(self):
        graph_settings = {'dotted': 'True'}  # Missing 'lines'
        graph_settings_lines = {'lines': 'True'}
        with self.assertRaises(KeyError): self.dh.parse_plt_type('blue', graph_settings)
        with self.assertRaises(KeyError): self.dh.parse_plt_type('blue', graph_settings_lines)
    
    def test_parse_plt_type_settings_not_string(self):
        graph_settings = {'dotted': 1, 'lines': (10, 10)}
        with self.assertRaises(TypeError): self.dh.parse_plt_type('blue', graph_settings)

    def test_calculate_beta_return_value(self):
        """This test function is a WIP since the equation for calculation is currently not known"""
        ub = 7
        uc = 3
        rb = 1000
        rc = 5000

        ib = ub/rb
        ic = uc/rc
        beta = ic/ib # Should be 0.0857142857
        beta = round(0.0857142857, 10)
        return_value = self.dh.calculate_current_gain(ub, rb, uc, rc)

        self.assertEqual(return_value, beta)

    def test_calculate_beta_wrong_types_string(self):
        ub = '7'
        uc = '3'
        rb = '1000'
        rc = '5000'
        with self.assertRaises(TypeError): self.dh.calculate_current_gain(ub, rb, uc, rc)

    def test_calculate_beta_wrong_type_lists(self):
        ub = [1, 2]
        uc = 3
        rb = 5000
        rc = 10000
        with self.assertRaises(TypeError): self.dh.calculate_current_gain(ub, rb, uc, rc)

    def test_calculate_beta_wrong_type_all_lists(self):
        ub = [1, 2]
        uc = [3,4]
        rb = [5000, 6000]
        rc = [10000, 7000]
        with self.assertRaises(TypeError): self.dh.calculate_current_gain(ub, rb, uc, rc)

    def test_calculate_beta_tuples(self):
        ub = (1, 2)
        uc = (3, 4)
        rb = (5000, 6000)
        rc = (10000, 7000)
        with self.assertRaises(TypeError): self.dh.calculate_current_gain(ub, rb, uc, rc)


if __name__ == '__main__':
    unittest.main()
