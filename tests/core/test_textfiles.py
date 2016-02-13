from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from core.models import TextFile
from django.core.urlresolvers import reverse
from urlparse import urlparse
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.conf import settings
import json

from django.http import HttpResponseRedirect
"""
class TokenTest(APITestCase):

    def test_user_creations(self):
        data= {'username': 'test@test.com', 'password': 'test'}
        response = self.client.post(reverse('register'), data )
        self.assertEqual(response.status_code, 201)


        user = User.objects.filter(username='test@test.com')[0]

        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        print token

        response = self.client.post(reverse('textfile-list'), data)
        self.assertEqual(response.status_code,220)
"""

class FileUploadTests(APITestCase):

    def setUp(self):
        self.tearDown()
        data= {'username': 'test@test.com', 'password': 'test'}
        response = self.client.post(reverse('register'), data )
        self.assertEqual(response.status_code, 201)


        self.user = User.objects.filter(username='test@test.com')[0]

        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def tearDown(self):
        try:
            u = User.objects.get_by_natural_key('test')
            u.delete()

        except Exception as e:
            pass
        TextFile.objects.all().delete()

    def _create_test_file(self, path):
        f = open(path, 'w')
        f.write('test123\n')
        f.close()
        f = open(path, 'rb')
        return {'file': f}
    """
    def test_upload_file(self):
        url = reverse('textfile-list')
        data = self._create_test_file('/tmp/test_upload')

        # assert authenticated user can upload file

        client = APIClient()
        token = Token.objects.get(user__username=self.user.username)
        client = APIClient()
        client.force_authenticate(user=self.user, token=None)


        response = client.post(url, data, format='multipart')
        print response

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('created', response.data)
        self.assertTrue(urlparse(
            response.data['file']).path.startswith(settings.MEDIA_URL))
        self.assertEqual(response.data['owner'],
                       User.objects.get_by_natural_key('test').id)
        self.assertIn('created', response.data)

        # assert unauthenticated user can not upload file
        client.logout()
        response = client.post(url, data, format='multipart')
        #self.assertEqual(response.status_code, 401)
        """