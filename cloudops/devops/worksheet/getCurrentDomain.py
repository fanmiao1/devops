from .models import CurrentDomain,WechatApp

def get_current_domain():
    try:
        current_domain = CurrentDomain.objects.only('domain').get(domain_id = 1).domain
    except:
        current_domain = 'devops.aukeyit.com'
    return current_domain