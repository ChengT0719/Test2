from app.models import User
import unittest


class ModelsUserTestCase(unittest.TestCase):
    def test_get_password(self):
        u = User(password="13915214820")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_setter(self):
        u = User(password="13915214820")
        self.assertTrue(u.password_hash is not None)

    def test_check_password(self):
        u = User(password="13915214820")
        self.assertTrue(u.check_password("13915214820"))
        self.assertFalse(u.check_password("1391521482"))

    def test_check_salts_are_random(self):
        u = User(password="13915214820")
        u2 = User(password="139152148201")
        self.assertFalse(u.password_hash == u2.password_hash)


if __name__ == "__main__":
    unittest.main()