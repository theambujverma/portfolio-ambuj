from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class ContactFormTests(TestCase):
    def test_contact_form_shows_success_message(self):
        response = self.client.post(
            reverse('contact'),
            {
                'name': 'Aman',
                'email': 'aman@example.com',
                'message': 'Hello from test',
            },
            follow=True,
        )

        self.assertContains(response, 'Your message has been sent')


class ProfileSettingsTests(TestCase):
    def test_profile_settings_update_username_password_and_photo(self):
        User = get_user_model()
        user = User.objects.create_user(username='olduser', password='oldpass')
        self.client.force_login(user)

        photo = SimpleUploadedFile(
            'avatar.jpg',
            b'fake-image-bytes',
            content_type='image/jpeg',
        )

        response = self.client.post(
            reverse('update_profile'),
            {
                'username': 'newuser',
                'new_password': 'StrongPass123!',
                'profile_photo': photo,
            },
            follow=True,
        )

        user.refresh_from_db()
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertTrue(user.profile.photo)
        self.assertContains(response, 'Profile updated successfully')
