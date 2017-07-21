from unittest import TestCase
from model import connect_to_db, db, User, Favorite, Dog, Shelter, Breed, example_data
from server import app
from flask import session



class FlaskTestsBasic(TestCase):

    def setUp(self):
      """Stuff to do before every test."""

      self.client = app.test_client()
      app.config['TESTING'] = True

class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        # import pdb
        # pdb.set_trace()

        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_login(self):
        result = self.client.post("/login",
                                  data={"email": "abby@gmail.com",
                                        "password": "abc123"},
                                  follow_redirects=True)
        self.assertIn("Logged in", result.data)

class FlaskTestsLoggedIn(TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        # import pdb
        # pdb.set_trace()

        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_profile_page(self):
        """Tests only logged in user has access to proile."""

        result = self.client.get('users/1')
        self.assertIn("First name:", result.data)



if __name__ == "__main__":

    import unittest
    unittest.main()