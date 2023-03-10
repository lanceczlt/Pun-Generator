import unittest
import os
import json
from io import StringIO
from contextlib import redirect_stdout
from my_script import process_files  # replace with the actual name of your script/function


class TestProcessFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = './test_data/'
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        os.rmdir(self.test_dir)
        
    def test_csv_file(self):
        csv_data = 'Name, Age\nAlice, 30\nBob, 25\nCharlie, 40\n'
        with open(os.path.join(self.test_dir, 'test.csv'), 'w') as f:
            f.write(csv_data)
            
        expected_output = {
            "type": "test",
            "phrase(s?)": ["Alice", "Bob", "Charlie"],
            "source": {}
        }
        
        with StringIO() as buf, redirect_stdout(buf):
            process_files(self.test_dir)
            actual_output = json.loads(buf.getvalue())
        
        self.assertEqual(len(actual_output), 1)
        self.assertDictEqual(actual_output[0], expected_output)
        
    def test_txt_file(self):
        txt_data = 'This is line 1.\nThis is line 2.\nThis is line 3.\n'
        with open(os.path.join(self.test_dir, 'test.txt'), 'w') as f:
            f.write(txt_data)
            
        expected_output = {
            "type": "test",
            "phrase(s?)": ["This is line 1.", "This is line 2.", "This is line 3."],
            "source": {}
        }
        
        with StringIO() as buf, redirect_stdout(buf):
            process_files(self.test_dir)
            actual_output = json.loads(buf.getvalue())
        
        self.assertEqual(len(actual_output), 1)
        self.assertDictEqual(actual_output[0], expected_output)
        
    def test_multiple_files(self):
        csv_data = 'Name, Age\nAlice, 30\nBob, 25\nCharlie, 40\n'
        txt_data = 'This is line 1.\nThis is line 2.\nThis is line 3.\n'
        
        with open(os.path.join(self.test_dir, 'test.csv'), 'w') as f:
            f.write(csv_data)
        with open(os.path.join(self.test_dir, 'test.txt'), 'w') as f:
            f.write(txt_data)
            
        expected_output = [
            {
                "type": "test",
                "phrase(s?)": ["Alice", "Bob", "Charlie"],
                "source": {}
            },
            {
                "type": "test",
                "phrase(s?)": ["This is line 1.", "This is line 2.", "This is line 3."],
                "source": {}
            }
        ]
        
        with StringIO() as buf, redirect_stdout(buf):
            process_files(self.test_dir)
            actual_output = json.loads(buf.getvalue())
        
        self.assertEqual(len(actual_output), 2)
        self.assertDictEqual(actual_output[0], expected_output[0])
        self.assertDictEqual(actual_output[1], expected_output[1])
        
    def test_no_files(self):
        with StringIO() as buf, redirect_stdout(buf):
            process_files(self.test_dir)
            actual_output = json.loads(buf.getvalue())
        
        self.assertEqual(len(actual_output), 0)


if __name__ == '__main__':
    unittest.main()
