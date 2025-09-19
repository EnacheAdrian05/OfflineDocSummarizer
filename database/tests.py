import unittest
import os
import tempfile
from db import (
    create_table,
    insert_document,
    find_by_hash,
    update_summary,
    file_hash,
)

class TestDocumentDB(unittest.TestCase):
    def setUp(self):
        db_file = os.path.join(os.path.dirname(__file__), "documents.db")
        if os.path.exists(db_file):
            os.remove(db_file)
        create_table()

        self.tmp1 = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False)
        self.tmp2 = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False)
        self.tmp_empty = tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False)
        self.tmp_invalid = tempfile.NamedTemporaryFile(mode='w+', suffix='.bin', delete=False)
        self.tmp_invalid.close()

        self.tmp1.write("Hello World  ")
        self.tmp1.close()

        self.tmp2.write("  hello   world")
        self.tmp2.close()

        self.tmp_empty.close()

    def tearDown(self):
        for f in [self.tmp1.name, self.tmp2.name, self.tmp_empty.name, self.tmp_invalid.name]:
            if os.path.exists(f):
                os.unlink(f)

    def test_insert_and_find(self):
        self.assertTrue(insert_document(self.tmp1.name))
        
        h1 = file_hash(self.tmp1.name)
        result = find_by_hash(h1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], h1)  
        self.assertEqual(result[1], os.path.abspath(self.tmp1.name))  
        self.assertIsNone(result[2])

    def test_duplicate_insert_updates_path(self):
        self.assertTrue(insert_document(self.tmp1.name))
        self.assertFalse(insert_document(self.tmp2.name))
        
        h = file_hash(self.tmp2.name)
        result = find_by_hash(h)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], h)
        self.assertEqual(result[1], os.path.abspath(self.tmp2.name))

    def test_summary_update(self):
        self.assertTrue(insert_document(self.tmp1.name))
        h = file_hash(self.tmp1.name)

        fake_hash = "deadbeef" * 8
        self.assertIsNone(update_summary(fake_hash, "Summary"))

        self.assertTrue(update_summary(h, "First summary"))
        result = find_by_hash(h)
        self.assertEqual(result[2], "First summary")

        self.assertIsNone(update_summary(h, "Second summary"))
        result = find_by_hash(h)
        self.assertEqual(result[2], "First summary")

    def test_empty_file(self):
        self.assertFalse(insert_document(self.tmp_empty.name))
        h = file_hash(self.tmp_empty.name)
        result = find_by_hash(h) if h else None
        self.assertIsNone(result)

    def test_unsupported_extension(self):
        self.assertIsNone(file_hash(self.tmp_invalid.name))


if __name__ == '__main__':
    unittest.main()
