from routers.register.auth import hash_password, verify_password
import unittest
import sys
import os

# Tambahkan path backend ke sys agar bisa impor modul
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'backend', 'routers')))


class TestPasswordUtils(unittest.TestCase):

    def test_hash_should_not_equal_plain(self):
        plain = "rahasia123"
        hashed = hash_password(plain)
        self.assertNotEqual(plain, hashed)
        self.assertTrue(hashed.startswith("$2b$"))  # bcrypt prefix

    def test_verify_correct_password(self):
        plain = "epicare"
        hashed = hash_password(plain)
        self.assertTrue(verify_password(plain, hashed))

    def test_verify_wrong_password(self):
        hashed = hash_password("epicare123")
        self.assertFalse(verify_password("salah", hashed))


if __name__ == '__main__':
    unittest.main()
