from django.test import TestCase
from django.contrib.auth import get_user_model


class TestManagers(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='test@test.com', password='test')
        assert user.email == 'test@test.com'
