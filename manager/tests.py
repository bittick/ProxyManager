from django.test import TestCase
from .models import ExtensionUser, ConfirmationCode


class ApiUserTestCase(TestCase):
    jwt_token = None
    user_data = {
        "username": "jomka",
        "password": "jopa123",
        "email": "romka@mail.ru"
    }

    def test_create_user(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        self.jwt_token = r.json()
        user_model = ExtensionUser.objects.get(username=self.user_data['username'])
        code = ConfirmationCode.objects.get(user_link=user_model).code
        r = self.client.post('/api/ver_code', headers=self.jwt_token, data={'code': code})
        print(r.data)
        self.assertEquals(200, r.status_code)
        user_model = ExtensionUser.objects.get(username=self.user_data['username'])
        self.assertEquals(True, user_model.is_active)

    def test_login_user(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        user_model = ExtensionUser.objects.get(username=self.user_data['username'])
        r = self.client.post('/api/auth', data={'username': self.user_data['username'],
                                                'password': self.user_data['password']})
        self.assertEquals(200, r.status_code)
        self.assertEquals(r.json().get('Auth'), user_model.jwt_access_token)

    # def test_recover(self):
    #     r = self.client.post('/api/reg', data=self.user_data)
    #     self.assertEquals(201, r.status_code)
    #     self.jwt_token = r.json()
    #     user_model = ExtensionUser.objects.get(username=self.user_data['username'])
    #     code = ConfirmationCode.objects.get(user_link=user_model).code
    #     r = self.client.post('/api/ver_code', headers=self.jwt_token, data={'code': code})
    #     print(r.data)
    #     self.assertEquals(200, r.status_code)
    #     user_model = ExtensionUser.objects.get(username=self.user_data['username'])
    #     self.assertEquals(True, user_model.is_active)
    #     r = self.client.post('api/recover', data={
    #         'email': self.user_data['email'],
    #     })
    #     self.assertEquals(200, r.status_code)
    #     self.assertEquals(user_model.)
