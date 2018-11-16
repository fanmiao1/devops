# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/2
@  author  : Xieyz
@  software: PyCharm
"""
import datetime
from django.contrib.contenttypes.models import ContentType

from opscenter.models import RevisionLogs

def change(choice = None):
    def out_r(fun):
        def wapper(self, request, *args, **kwargs):
            user = request.user
            fields = self.get_object()._meta.fields
            app_label = self.get_object()._meta.app_label
            model_name = self.get_object()._meta.object_name
            content_type = ContentType.objects.only('id').get(app_label=app_label, model=model_name)
            content = []
            for i in fields:
                _name = i.name
                try: field_key = eval("self.get_object().{field}.id".format(field=_name))
                except: field_key = eval("self.get_object().{field}".format(field=_name))
                new_field_key = request.POST.get(i.name, '9*#**#*9')
                if new_field_key == '9*#**#*9': continue
                if isinstance(field_key, int):
                    try: new_field_key = int(new_field_key)
                    except: continue
                if isinstance(field_key, datetime.date):
                    field_key = field_key.strftime("%Y-%m-%d")
                if isinstance(field_key, datetime.datetime):
                    field_key = field_key.strftime("%Y-%m-%d %H:%M:%S")
                if field_key != new_field_key:
                    try: f_name = i.verbose_name
                    except: f_name = i.name
                    if field_key or new_field_key:
                        if choice:
                            if _name in choice.keys():
                                i_choice = eval("self.get_object().{CHOICES}".format(CHOICES=choice[_name]))
                                for v in i_choice:
                                    if v[0] == field_key:
                                        field_key = v[1]
                                    if v[0] == new_field_key:
                                        new_field_key = v[1]
                        content.append({i.verbose_name: {'old': field_key, 'new': new_field_key}})
            if content:
                RevisionLogs.objects.create(
                    content_type=content_type,
                    content=content,
                    object_id=self.get_object().id,
                    user=user
                )
            return fun(self, request, *args,**kwargs)
        return wapper
    return out_r
