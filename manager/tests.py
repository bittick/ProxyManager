from django.test import TestCase
from .models import AppUser, ConfirmationCode


class ApiUserTestCase(TestCase):
    jwt_token = None
    user_data = {
        "username": "jomka",
        "password": "jopa123123",
        "email": "romka@mail.ru"
    }

    def test_create_user(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        self.jwt_token = r.json()
        user_model = AppUser.objects.get(username=self.user_data['username'])
        code = ConfirmationCode.objects.get(user_link=user_model).code
        r = self.client.post('/api/ver_code', headers=self.jwt_token, data={'code': code})
        self.assertEquals(200, r.status_code)
        user_model = AppUser.objects.get(username=self.user_data['username'])
        self.assertEquals(True, user_model.is_active)

    def test_login_user(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        user_model = AppUser.objects.get(username=self.user_data['username'])
        r = self.client.post('/api/auth', data={'username': self.user_data['username'],
                                                'password': self.user_data['password']})
        self.assertEquals(200, r.status_code)
        self.assertEquals(r.json().get('Auth'), user_model.jwt_access_token)

    def test_recover(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        self.jwt_token = r.json()
        user_model = AppUser.objects.get(username=self.user_data['username'])
        code = ConfirmationCode.objects.get(user_link=user_model).code
        r = self.client.post('/api/ver_code', headers=self.jwt_token, data={'code': code})
        self.assertEquals(200, r.status_code)
        user_model = AppUser.objects.get(username=self.user_data['username'])
        self.assertEquals(True, user_model.is_active)
        r = self.client.post('/api/start_recover', data={
            'email': self.user_data['email'],
        })
        self.assertEquals(200, r.status_code)
        code = ConfirmationCode.objects.get(user_link=user_model, type='recovery').code
        r = self.client.post('/api/finish_recover', data={
            'email': self.user_data['email'],
            'code': code,
        })
        self.assertEquals(200, r.status_code)
        self.assertEquals(r.json()['Auth'], user_model.jwt_access_token)

    def test_password_change(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        self.jwt_token = r.json()
        user_model = AppUser.objects.get(username=self.user_data['username'])
        code = ConfirmationCode.objects.get(user_link=user_model).code
        r = self.client.post('/api/ver_code', headers=self.jwt_token, data={'code': code})
        self.assertEquals(200, r.status_code)
        user_model = AppUser.objects.get(username=self.user_data['username'])
        self.assertEquals(True, user_model.is_active)
        body = {"new_password1": "bebra1123", "new_password2": "bebra1123"}
        r = self.client.post('/api/change_password', headers=self.jwt_token, data=body)
        self.assertEquals(200, r.status_code)
        new_token = r.json()['Auth']
        self.assertEquals(new_token != self.jwt_token['Auth'], True)
        r = self.client.post('/api/auth', data={'username': self.user_data['username'],
                                                'password': 'bebra1123'})
        self.assertEquals(200, r.status_code)

    def test_uniq_email(self):
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(201, r.status_code)
        self.jwt_token = r.json()
        user_model = AppUser.objects.get(username=self.user_data['username'])
        code = ConfirmationCode.objects.get(user_link=user_model).code
        r = self.client.post('/api/ver_code', headers=self.jwt_token, data={'code': code})
        self.assertEquals(200, r.status_code)
        user_model = AppUser.objects.get(username=self.user_data['username'])
        self.assertEquals(True, user_model.is_active)
        r = self.client.post('/api/reg', data=self.user_data)
        self.assertEquals(r.status_code, 400)
