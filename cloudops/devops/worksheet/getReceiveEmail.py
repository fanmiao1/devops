from .models import ReceiveEmail

def get_receive_email():
    try:
        email_obj = ReceiveEmail.objects.get(email_id = 1)
        email = email_obj.email
        email_password = email_obj.email_password
    except:
        email = 'itsupport@aukeys.com'
        email_password = 'Ops@aukey#!123'
    receive_email = {
        'email': email,
        'email_password': email_password
    }
    return receive_email