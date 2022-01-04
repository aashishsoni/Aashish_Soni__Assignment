"""
Products resolution tests
"""
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.models import UserProfile
from faker import Faker
import random

User = get_user_model()

def generate_password():
    """ this function used for genrate unique sela key"""
    code = ''.join([str(random.randint(0, 999)).zfill(4) for _ in range(2)])
    return code

class UserModelTest(APITestCase):
    """
    Tests the accounts database model
    """

    @classmethod
    def setUpTestData(cls):
        """
        set up the user table, user details table, for use in multiple tests
        """
        fake = Faker()

        _u1 = User.objects.create_user(email='vikram.kumar@yopmail.com', first_name=fake.first_name(),
        last_name=fake.last_name(), is_active=True, password='sipl@1234')

        _u2 = User.objects.create_user(email=fake.email(), first_name=fake.first_name(),
        last_name=fake.last_name(), is_active=True, password=generate_password())
        
        _u3 = User.objects.create_user(email=fake.email(), first_name=fake.first_name(), 
        last_name=fake.last_name(), is_active=True, password=generate_password())
        
        _u4 = User.objects.create_user(email=fake.email(), first_name=fake.first_name(), 
        last_name=fake.last_name(), is_active=True, password=generate_password())
        
        UserProfile.objects.create(user_id=_u1.id)

        UserProfile.objects.create(user_id=_u2.id)

        UserProfile.objects.create(user_id=_u3.id)

        UserProfile.objects.create(user_id=_u4.id)
        
    def test_user_login(self):
        """
        test user login API
        """
        data = {"email": "vikram.kumar@yopmail.com", "password":'sipl@1234'}
        response2 = self.client.post("api/v1/login/", data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_user_profile_get(self):
        """
            this function used for get user profile
        """
        user = User.objects.get(email="vikram.kumar@yopmail.com")
        response2 = self.client.get("/en/api/accounts/users/" + user.id + "/")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_countries_get(self):
        """
            this function for get countries get
        """
        user = User.objects.get(email="vikram.kumar@yopmail.com")
        response2 = self.client.get("/en/api/accounts/countries/")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)