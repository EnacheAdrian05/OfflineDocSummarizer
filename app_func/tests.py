import unittest
import tempfile
from pathlib import Path
from gen_summary import read_file, generate_summary

class TestGenSummary(unittest.TestCase):
    def test_read_file_txt(self):
        with tempfile.NamedTemporaryFile('w+', suffix='.txt', delete=False) as tmp:
            tmp.write("Hello world")
            tmp.flush()
            self.assertEqual(read_file(tmp.name), "Hello world")
        Path(tmp.name).unlink()

    def test_read_file_txt_empty(self):
        with tempfile.NamedTemporaryFile('w+', suffix='.txt', delete=False) as tmp:
            tmp.flush()
            self.assertIsNone(read_file(tmp.name))
        Path(tmp.name).unlink()

    def test_read_file_unknown_ext(self):
        with tempfile.NamedTemporaryFile('w+', suffix='.unknown', delete=False) as tmp:
            tmp.write("text")
            tmp.flush()
            self.assertIsNone(read_file(tmp.name))
        Path(tmp.name).unlink()

    def test_generate_summary_short_text(self):
        text = "This is a simple sentence. " * 10
        summary = generate_summary(text)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)

    def test_generate_summary_long_text(self):
        text = "This is a simple sentence. " * 2000
        summary = generate_summary(text)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)

if __name__ == '__main__':
    unittest.main()
