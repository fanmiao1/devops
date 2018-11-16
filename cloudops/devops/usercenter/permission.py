from django.shortcuts import render
from .models import Permission
from django.contrib import messages
from django.contrib.auth.models import Permission as auth_permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.urls import resolve   # 此方法可以将url地址转换成url的name

def perm_check(request, *args, **kwargs):
    try:
        url_obj = resolve(request.path_info)
        url_method, url_args = request.method, request.GET
        if url_method == 'GET':
            url_method_num = 1
        elif url_method == 'POST':
            url_method_num = 2
        url_name = Permission.objects.only('name').get(url=url_obj.url_name, per_method=url_method_num).name
        app_label = ContentType.objects.only('app_label').get(
            id=auth_permission.objects.only('content_type_id').get(codename=url_name).content_type_id).app_label
        perm_name = ''
        # 权限必须和urlname配合使得
        if url_name:
            # 获取请求方法，和请求参数

            url_args_list = []
            # 将各个参数的值用逗号隔开组成字符串，因为数据库中是这样存的
            for i in url_obj.kwargs:
                url_args_list.append(str(url_obj.kwargs[i]))
            # url_args_list = ','.join(url_args_list)
            # 操作数据库

            get_perm = Permission.objects.filter(Q(url=url_obj.url_name), Q(per_method=url_method_num))
            if get_perm:
                for i in get_perm:
                    perm_name = i.name
                    # perm_str = 'usercenter.%s' % perm_name
                    perm_str = app_label + '.' + perm_name
                    if i.argument_list:
                        if url_args_list:
                            judge = 1
                            for v in range(len(i.argument_list.split(','))):
                                try:
                                    if i.argument_list.split(',')[v] == url_args_list[v]:
                                        continue
                                    else:
                                        judge = 0
                                        print('用户:' + str(request.user) + '通过' + str(url_method) + '访问url:' + str(
                                            url_name) + '被拒绝.1')
                                        return False
                                except:
                                    print('用户:' + str(request.user) + '通过' + str(url_method) + '访问url:' + str(url_name) + '被拒绝.2')
                                    return False
                            if judge == 1:
                                return True
                            else:
                                print('用户:' + str(request.user) + '通过' + str(url_method) + '访问url:' + str(
                                    url_name) + '被拒绝.3')
                                return False
                        else:
                            print('用户:' + str(request.user) + '通过' + str(url_method) + '访问url:' + str(
                                url_name) + '被拒绝.4')
                            return False
                    else:
                        if request.user.has_perm(perm_str):
                            return True
                else:
                    print('用户:' + str(request.user) + '通过' + str(url_method) + '访问url:' + str(url_name) + '被拒绝.5')
                    return False
            else:
                print('用户:'+str(request.user) + '通过' + str(url_method) + '访问url:' + str(url_name) + '被拒绝.6')
                return False
        else:
            return False   # 没有权限设置，默认不放过
    except Exception as e:
        print ('Error：【{e}】'.format(e=str(e)))

def check_permission(fun):    # 定义一个装饰器，在views中应用
    def wapper(request, *args, **kwargs):
        if perm_check(request, *args, **kwargs):  # 调用上面的权限验证方法
            return fun(request, *args, **kwargs)
        messages.add_message(request, messages.ERROR, '很抱歉，没有权限进行此操作！')
        request.session['from'] = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(request.session['from'])
        # return render(request, 'head.html', locals())
    return wapper

from rest_framework.response import Response
def check_object_perm(codename):    # 定义一个装饰器，在views中应用
    def out_r(fun):
        def wapper(self, request, *args, **kwargs):
            user = request.user
            if not user.has_perm(codename):
                return Response(u'没有权限进行此操作！')
            else:
                return fun(self, request, *args,**kwargs)
        return wapper
    return out_r
