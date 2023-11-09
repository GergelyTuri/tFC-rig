import os
import unittest

from py_arduino_serial import main


class TestPyArduinoSerial(unittest.TestCase):
    def test_main(self):
        # Test if the function runs without errors
        main()

        # Test if the file was created
        mouse_id = "test_mouse"
        current_date_time = datetime.now()
        formatted_date_time = current_date_time.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"{mouse_id}_{formatted_date_time}.json"
        self.assertTrue(os.path.exists(file_path))

        # Test if the file is not empty
        with open(file_path, "r") as f:
            data = f.read()
            self.assertNotEqual(data, "")
