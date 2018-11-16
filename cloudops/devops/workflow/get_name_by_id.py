# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.forms.models import model_to_dict


class get_name_by_id(object):

    def get_name(id):
        user_obj = User.objects.get(id=id)
        last_name = user_obj.last_name if user_obj.last_name else ""
        first_name = user_obj.first_name if user_obj.first_name else ""

        name = str(last_name) + str(first_name)
        if not name:
            name = str(user_obj.username if user_obj.username else "")
        return name
