import ipaddress
from django import template

register = template.Library()


@register.filter(name='int2ip')
def int2ip(value):
    return str(ipaddress.ip_address(value))


@register.filter(name='ip2int')
def ip2int(value):
    return int(ipaddress.ip_address(value))

