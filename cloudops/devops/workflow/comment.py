# -*- coding: utf-8 -*-
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import datetime


class BuildComment(object):

    def __init__(self):
        pass

    def project_apply_comment(id,content,user_id):
        project_apply_comment = ProjectApplyComment()
        project_apply_comment.project_id = id
        project_apply_comment.content = content
        project_apply_comment.user_id = user_id
        project_apply_comment.datetime = datetime.datetime.now()
        project_apply_comment.save()

    def project_member_apply_comment(id,content,user_id):
        project_apply_comment = ProjectMemberApplyComment()
        project_apply_comment.project_userflow_id = id
        project_apply_comment.content = content
        project_apply_comment.user_id = user_id
        project_apply_comment.datetime = datetime.datetime.now()
        project_apply_comment.save()

    def project_user_apply_comment(id,content,user_id):
        project_apply_comment = ProjectUserApplyComment()
        project_apply_comment.user_apply_flow_id = id
        project_apply_comment.content = content
        project_apply_comment.user_id = user_id
        project_apply_comment.datetime = datetime.datetime.now()
        project_apply_comment.save()

    def project_user_authority_apply_comment(id, content, user_id):
        project_apply_comment = ProjectUserAuthorityApplyComment()
        project_apply_comment.authority_flow_id = id
        project_apply_comment.content = content
        project_apply_comment.user_id = user_id
        project_apply_comment.datetime = datetime.datetime.now()
        project_apply_comment.save()

    def project_release_apply_comment(id, content, user_id):
        project_apply_comment = ProjectReleaseApplyComment()
        project_apply_comment.project_releaseflow_id = id
        project_apply_comment.content = content
        project_apply_comment.user_id = user_id
        project_apply_comment.datetime = datetime.datetime.now()
        project_apply_comment.save()

    def cron_apply_comment(id, content, user_id):
        project_apply_comment = CronApplyComment()
        project_apply_comment.cronflow_id = id
        project_apply_comment.content = content
        project_apply_comment.user_id = user_id
        project_apply_comment.datetime = datetime.datetime.now()
        project_apply_comment.save()


@login_required
def delete_project_apply_comment(request,id):
    comment = ProjectApplyComment.objects.get(id=id)
    if request.user.id == comment.user.id:
        ProjectApplyComment.objects.filter(id=id).delete()
        messages.add_message(request,messages.SUCCESS,'删除成功！')
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})

@login_required
def delete_project_member_apply_comment(request,id):
    comment = ProjectMemberApplyComment.objects.get(id=id)
    if request.user == comment.user:
        ProjectMemberApplyComment.objects.filter(id=id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功！')
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})

@login_required
def delete_project_user_apply_comment(request,id):
    comment = ProjectUserApplyComment.objects.get(id=id)
    if request.user == comment.user:
        ProjectUserApplyComment.objects.filter(id=id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功！')
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})

@login_required
def delete_project_user_authority_apply_comment(request,id):
    comment = ProjectUserAuthorityApplyComment.objects.get(id=id)
    if request.user == comment.user:
        ProjectUserAuthorityApplyComment.objects.filter(id=id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功！')
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})

@login_required
def delete_project_release_apply_comment(request,id):
    comment = ProjectReleaseApplyComment.objects.get(id=id)
    if request.user == comment.user:
        ProjectReleaseApplyComment.objects.filter(id=id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功！')
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})

@login_required
def delete_cron_apply_comment(request,id):
    comment = CronApplyComment.objects.get(id=id)
    if request.user == comment.user:
        CronApplyComment.objects.filter(id=id).delete()
        messages.add_message(request, messages.SUCCESS, '删除成功！')
        return JsonResponse({'result':'true'})
    else:
        return JsonResponse({'result':'false'})