from django.contrib.auth import get_user_model
from django.test import TestCase

from user.serializers import UserSerializer

User = get_user_model()


class UserSerializerTests(TestCase):
    def setUp(self):
        self.valid_payload = {
            "email": "testu@u.com",
            "password": "password123"
        }
        self.user = User.objects.create_user(**self.valid_payload)
        User.objects.filter(email=self.valid_payload["email"]).delete()

    def test_create_user(self):
        serializer = UserSerializer(data=self.valid_payload)
        user = serializer.create(validated_data=self.valid_payload)
        self.assertEqual(user.email, self.valid_payload["email"])
        self.assertTrue(user.check_password(self.valid_payload["password"]))

    def test_create_user_with_short_password(self):
        payload = {
            "email": "testu@u.com",
            "password": "123"
        }
        serializer = UserSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_update_user_password(self):
        new_password = "new_password123"
        payload = {
            "email": "testu@u.com",
            "password": new_password
        }
        serializer = UserSerializer(instance=self.user, data=payload, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(new_password))

    def test_update_user_without_password(self):
        payload = {
            "email": "testu@u.com",
        }
        serializer = UserSerializer(instance=self.user, data=payload, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(self.valid_payload["password"]))
