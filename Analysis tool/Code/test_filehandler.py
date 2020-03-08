import unittest
from filehandler import FileHandler


class FileHandlerTest(unittest.TestCase):

    def setUp(self):
        self.fh = FileHandler()

    def test_readRaw_with_existing_file(self):
        self.assertEqual(self.fh.readRaw("../test_files/test.txt"), "test\ntest\ntest")
    
    def test_readRaw_file_not_found(self):
        with self.assertRaises(FileNotFoundError): self.fh.readRaw("awoenf aiwebfu aiwefia ij")

    def test_readRaw_format_not_string(self):
        with self.assertRaises(TypeError): self.fh.readRaw(123)
        with self.assertRaises(TypeError): self.fh.readRaw((123,123))
        with self.assertRaises(TypeError): self.fh.readRaw(12.3)
        with self.assertRaises(TypeError): self.fh.readRaw(5e-123)
        with self.assertRaises(TypeError): self.fh.readRaw(123+3j)
        with self.assertRaises(TypeError): self.fh.readRaw([123,123,123])
        with self.assertRaises(TypeError): self.fh.readRaw({'k': 123})
        with self.assertRaises(TypeError): self.fh.readRaw(True)

    def test_read_CSV_with_existing_file(self):
        self.assertEqual(self.fh.readCSV("../test_files/LUT test.csv"), [['Deg C', 'mV'],['-50', '1955'], ['-49', '1949'], ['-48', '1942']])
        self.assertEqual(self.fh.readCSV("../test_files/LUT test no header.csv",'int', False), [[-50, 1955], [-49, 1949], [-48, 1942]])

    def test_read_CSV_file_not_found(self):
        with self.assertRaises(FileNotFoundError): self.fh.readCSV("awoenf aiwebfu aiwefia ij")

    def test_read_CSV_format_not_string(self):
        with self.assertRaises(TypeError): self.fh.readCSV(123)
        with self.assertRaises(TypeError): self.fh.readCSV((123,123))
        with self.assertRaises(TypeError): self.fh.readCSV(12.3)
        with self.assertRaises(TypeError): self.fh.readCSV(5e-123)
        with self.assertRaises(TypeError): self.fh.readCSV(123+3j)
        with self.assertRaises(TypeError): self.fh.readCSV([123,123,123])
        with self.assertRaises(TypeError): self.fh.readCSV({'k': 123})
        with self.assertRaises(TypeError): self.fh.readCSV(True)

    def test_read_CSV_header_false_when_header_exists(self):
        with self.assertRaises(ValueError): self.fh.readCSV('../test_files/LMT85_LookUpTableCSV.csv', 'int', False)
        with self.assertRaises(ValueError): self.fh.readCSV('../test_files/LMT85_LookUpTableCSV.csv', 'float', False)

    def test_read_CSV_wrong_data_format(self):
        with self.assertRaises(TypeError): self.fh.readCSV('../test_files/LMT85_LookUpTableCSV.csv', 'w')
        with self.assertRaises(TypeError): self.fh.readCSV('../test_files/LMT85_LookUpTableCSV.csv', 2)
        with self.assertRaises(TypeError): self.fh.readCSV('../test_files/LMT85_LookUpTableCSV.csv', (1,2))
        with self.assertRaises(TypeError): self.fh.readCSV('../test_files/LMT85_LookUpTableCSV.csv', {'k': 123})

    def test_read_CSV_hex(self):
        """Checks if it is possible to read Hex values.
        This test only works with hex values or integers, since those are treated the same.

        Note that the function FileHandler.readCSV() is not supposed to convert between data formats, making this test
        a bit unnecessary. The usual header "time" can not be present since it is not a number and readCSV() does not allow
        for mixing data formats. This is why DataAnalysis takes care of parsing the CSV. A separate test can be found for
        parsing in test_DataAnalysis.py"""
        expected_list = [
            ["sic ube", "sic uc", "sic ub", "sic temp", "si ube", "si ub", "si uc", "si temp"],
            [2, 9, 3, 1176, 1, 9, 4, 1423],
            [2, 1, 15, 659, 1, 3, 10, 579]
        ]
        returned_list = self.fh.readCSV("../test_files/test_data_hex.csv", 'hex', True, ',')
        self.assertEqual(expected_list, returned_list)


if __name__ == '__main__':
    unittest.main()
