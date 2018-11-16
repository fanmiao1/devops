from django.contrib.auth.models import User
from workflow.get_name_by_id import get_name_by_id

def get_all_user():
    result = []
    try:
        obj = User.objects.all().filter(is_staff=1, is_active=1)
        for i in obj:
            result.append({'value': i.id, 'name': get_name_by_id.get_name(i.id)})
    except:
        result = [{'value': '' ,'name': '无'}]
    return result