import os
from celery import Celery
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProxyManager.settings')

app = Celery('celery_manager')
app.conf.timezone = 'Europe/Moscow'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task
def send_confirm_code_on_email(user_email, code):
    msg = MIMEMultipart()
    msg['Subject'] = 'Ваш код подтверждения'
    msg.attach(MIMEText(f'Код подтверждения: \n{str(code)}', 'plain', 'utf-8'))
    msg['From'] = 'dev.skillpay@gmail.com'
    msg['To'] = user_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login('dev.skillpay@gmail.com', 'mjvvjfvyofbxlbun')
    server.send_message(msg)
    server.quit()
    return True


@app.task
def send_recovery_code_on_email(user_email, code):
    msg = MIMEMultipart()
    msg['Subject'] = 'Ваш код для восстановления аккаунта'
    msg.attach(MIMEText(f'Код востановления: \n{str(code)}', 'plain', 'utf-8'))
    msg['From'] = 'dev.skillpay@gmail.com'
    msg['To'] = user_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login('dev.skillpay@gmail.com', 'mjvvjfvyofbxlbun')
    server.send_message(msg)
    server.quit()
    return True
