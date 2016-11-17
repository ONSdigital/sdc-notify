import requests
from json import loads, dumps
from decoder import get_json
import unittest
from app import app
from jose import jwt
from jwt import encode, JWT_ALGORITHM
from app import recreate_database
from app import create_organisations
from app import create_associations

login_url = "https://sdc-login-user.herokuapp.com/login"

# Email address options
email = "florence.nightingale@example.com"
# email = "chief.boyce@example.com"
# email = "fireman.sam@example.com"
# email = "rob.dabank@example.com"
password = "password"

ok = 200
unauthorized = 401

valid_token = None


class ComponentTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_should_do_something(self):

        # Given

        # When

        # Then


if __name__ == '__main__':

    # Create database
    recreate_database()
    organisations = create_organisations()
    create_associations(organisations)

    unittest.main()

