import unittest
from flask import current_app
from app import create_app


class Test(unittest.TestCase):
    def setUp(self):
        self.app, self.db = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()


    def test_environ_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])


    def test_app_is_existing(self):
        self.assertFalse(current_app is None)


if __name__ == "__main__":
    t = Test()
    t.setUp()