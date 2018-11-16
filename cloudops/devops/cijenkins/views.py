from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
import json
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import datetime
from .jenkinsAPI import *
from cijenkins.models import ModuleNameInfo
import time
from django.contrib import messages
from .forms import *
from .getBuildHistory import get_buildhistory
from .getConfigFile import getconfigfile
from devops.settings import MEDIA_ROOT
from usercenter.permission import check_permission
import re
import os


# Create your views here.
class DateEncoder(json.JSONEncoder):
    '''
    重写构造json类，遇到日期特殊处理，其余的用内置
    '''
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
             return json.JSONEncoder.default(self, obj)

@login_required
@check_permission
def job_manage_views(request,jenkins_env):
    if request.method == "POST":
        pageSize = request.POST.get('pageSize')  # 如何manufactoryy每页项目
        pageNumber = request.POST.get('pageNumber')
        offset = request.POST.get('offset')  # API中共有多少页
        sort_column = request.POST.get('sort')  # 该列需要排序
        order = request.POST.get('order')  # 升序或降序

        search = request.POST.get('search')
        if search:
            search = '%s' % (search)
            search = search.strip()
            all_list = getLogin(jenkins_env).get_job_info_regex(search)
            all_list_count = len(all_list)
        else:
            all_list = getJobsList(jenkins_env)
            all_list_count = getLogin(jenkins_env).jobs_count()
        if not offset:
            offset = 0
        if not pageNumber:
            pageNumber = 1
            pageSize = all_list_count
        if not pageSize:
            pageSize = 20  # 默认是每页20行的内容，与前端默认行数一致
        pageinator = Paginator(all_list, pageSize)  # 开始做分页
        page = int(int(offset) / int(pageSize) + 1)
        response_data = {'total': all_list_count, 'rows': []}
        # jenkins_env = jenkins_env
        for list in pageinator.page(pageNumber):
            description = getLogin(jenkins_env).get_job_info(list['name'])['description']
            last_sucess_build = getLogin(jenkins_env).get_job_info(list['name'])['lastCompletedBuild']
            last_sucess_number = last_sucess_build['number'] if last_sucess_build else 0
            if last_sucess_number:
                last_sucess_time = getLogin(jenkins_env).get_build_info(list['name'], last_sucess_number)['timestamp']
                time_local_sucess = time.localtime(last_sucess_time/1000)
                convert_time_sucess = time.strftime("%Y-%m-%d %H:%M:%S", time_local_sucess)
            else:
                convert_time_sucess = None

            last_false_build = getLogin(jenkins_env).get_job_info(list['name'])['lastFailedBuild']
            last_false_number = last_false_build['number'] if last_false_build else 0

            if last_false_number != 0:
                last_false_time = getLogin(jenkins_env).get_build_info(list['name'], last_false_number)['timestamp']
                time_local_false = time.localtime(last_false_time / 1000)
                convert_time_false = time.strftime("%Y-%m-%d %H:%M:%S", time_local_false)
            else:
                convert_time_false = None

            number_durate = last_sucess_build['number'] if last_sucess_build else 0
            if number_durate != 0:
                duration = getLogin(jenkins_env).get_build_info(list['name'], number_durate)['duration']
                time_local_durate = time.localtime(duration/1000)
                convert_time_durate = time.strftime("%M:%S", time_local_durate)
            else:
                convert_time_durate = None

            response_data['rows'].append({
                "job_name": list['name'] ,
                "statu": list['color'],
                "last_sucess_time": str(convert_time_sucess) + ' , ' + '构建号 : ' + str(last_sucess_number),
                "last_false_time": str(convert_time_false) + ' , ' + '构建号 : ' + str(last_false_number),
                "description": description[0:25] + '...' if description else "什么都没写!快联系周飞加上吧!",
                "duration": convert_time_durate
            })

        return HttpResponse(json.dumps(response_data, cls=DateEncoder))
    return render(request, 'cijenkins/job_manage.html', {'jenkins_env': jenkins_env})

@login_required
@check_permission
def job_details_views(request, jenkins_env, job_name):
    try:
        onbuild = buildStatus(jenkins_env,job_name)
        lastbuild = getLogin(jenkins_env).get_job_info(job_name)['lastBuild']['number']
        changes = ''
        ##添加修改记录内容
        change = getLogin(jenkins_env).get_build_info(job_name, int(lastbuild))['changeSet']['items']
        for l in change:
            if len(l) > 0:
                changes += str(l['revision']) + '.' + str(l['msg']) + ' － ' + str(l['user']) + '<br>'  # 信息叠加并自动换行
    except:
        onbuild = 'False'
        lastbuild = '0'
        changes = 'notbuild'

    if request.method == "GET":
        status = getLogin(jenkins_env).get_job_info(job_name)['color']
        descrite = getLogin(jenkins_env).get_job_info(job_name)['description']
        try:
            # buildresult = buildResult(jenkins_env, job_name)
            deploy_name = ModuleNameInfo.objects.get(module_name=job_name,build_number=lastbuild,jenkins_env=jenkins_env)
            login_user = deploy_name.build_user
        except:
            # buildresult = ''
            login_user = ''

        time_dict = get_buildhistory(jenkins_env,job_name)

        jobname_detail = {
            "jenkins_env": jenkins_env,
            "job_name": job_name if job_name else "",
            "description": descrite if descrite else "什么都没写!快联系周飞加上吧!",
            "lastbuild": str(lastbuild) if str(lastbuild) else "",
            # "status": str(status) + ' , ' + buildresult if str(status) + ' , ' + buildresult else "",
            "status": str(status) if str(status) else "",
            "onbuild": onbuild if onbuild else "",
            "changes": changes if changes else "没有变更记录.",
            "deployuser": login_user if login_user else "",
            "time_date": time_dict,
        }
    else:
        jobname_detail = {}
        result = {'onbuild':str(onbuild)} #用于ajax检测api接口返回信息并显示相应按钮
        return JsonResponse({'result': result})
    return render(request, 'cijenkins/job_details.html', jobname_detail)

@login_required
@check_permission
def job_deploy_views(request, jenkins_env, job_name):
    if request.method == "GET":
        deploy_env = 'deploy'
        deploy_name = request.user.id
        next_build = getLogin(jenkins_env).get_job_info(job_name)['nextBuildNumber']
        build_status = buildStatus(jenkins_env,job_name)
        if build_status == False:
            try:
                check_build = ModuleNameInfo.objects.get(module_name=job_name,build_number=next_build,jenkins_env=jenkins_env)
            except ModuleNameInfo.DoesNotExist:
                update_deploy_record = ModuleNameInfo.objects.create(module_name=job_name, build_number=next_build,
                                                                 build_user_id=deploy_name,build_status=0,jenkins_env=jenkins_env)
            check_build = ModuleNameInfo.objects.get(module_name=job_name,build_number=next_build,jenkins_env=jenkins_env)
            if check_build.build_status == 0:
                update_build_sql = ModuleNameInfo.objects.filter(module_name=job_name,build_number=next_build,jenkins_env=jenkins_env).update(build_status=1)
                # buildjob = buildJob(jenkins_env, job_name)
                buildjob = buildJobParam(jenkins_env,job_name,deploy_env=deploy_env,version=0)
            else:
                messages.add_message(request, messages.ERROR, '正在构建中，请稍候再试！')
                return HttpResponseRedirect(reverse('job_details', args=[jenkins_env,job_name]))
        else:
            messages.add_message(request,messages.ERROR,'正在构建中，请稍候再试！')
            return HttpResponseRedirect(reverse('job_details', args=[jenkins_env,job_name]))
    else:
        pass
    return HttpResponseRedirect(reverse('job_details',args=[jenkins_env,job_name]))

@login_required
@check_permission
def cancel_build_views(request, jenkins_env, job_name):
    buildstatus = buildStatus(jenkins_env,job_name)
    lastbuild_id = getLogin(jenkins_env).get_job_info(job_name)['lastBuild']['number']

    if buildstatus == True:
        cancel_queue = getLogin(jenkins_env).stop_build(job_name, lastbuild_id)
    else:
        messages.add_message(request, messages.ERROR, '构建已完成，无法取消！')
        return HttpResponseRedirect(reverse('job_details', args=[jenkins_env,job_name]))
    return HttpResponseRedirect(reverse('job_details',args=[jenkins_env,job_name]))

@login_required
@check_permission
def console_output_views(request, jenkins_env,job_name,num_id):
    console_output = consoleOutput(jenkins_env,job_name,num_id)
    build_status = buildStatus(jenkins_env, job_name)
    if request.method == 'POST':
        return JsonResponse({'console_output': console_output})
    return render(request,'cijenkins/console.html',{'console_output':console_output,
                                                    'jenkins_env':jenkins_env,'job_name':job_name,'num_id':num_id,
                                                    'build_status':build_status})

@login_required
@check_permission
def job_rollback_views(request,jenkins_env,job_name):
    time_date = get_buildhistory(jenkins_env,job_name)
    rollback_version_form = RollBackVersionForm()
    return render(request,'cijenkins/job_rollback.html',{"rollback_version_form": rollback_version_form,
                                                         "job_name": job_name,"time_date": time_date,"jenkins_env": jenkins_env})
@login_required
@check_permission
def rollback_version_views(request,jenkins_env,job_name):
    #form表单POST传参
    if request.method == "POST":
        rollback_version_form = RollBackVersionForm(request.POST)
        if rollback_version_form.is_valid():
            deploy_env = request.POST.get('deploy_env')
            version = request.POST.get('version')
            deploy_name = request.user.id
            next_build = getLogin(jenkins_env).get_job_info(job_name)['nextBuildNumber']
            build_status = buildStatus(jenkins_env,job_name)
            #检测版本号是否存在并做异常处理
            try:
                check_version = getLogin(jenkins_env).get_build_info(job_name,int(version))
            except:
                messages.add_message(request,messages.ERROR,'回滚版本号不存在，请确认后重试！')
                return render(request,'cijenkins/job_rollback.html', {"rollback_version_form": rollback_version_form,
                                                                      "jenkins_env": jenkins_env,"job_name": job_name})
            # 检测构建状态并更新数据信息
            if build_status == False:
                try:
                    check_build = ModuleNameInfo.objects.get(module_name=job_name, build_number=next_build)
                except ModuleNameInfo.DoesNotExist:
                    update_deploy_record = ModuleNameInfo.objects.create(module_name=job_name,
                                                                             build_number=next_build,
                                                                             build_user_id=deploy_name, jenkins_env=jenkins_env,
                                                                            build_status=0)
                check_build = ModuleNameInfo.objects.get(module_name=job_name, jenkins_env=jenkins_env, build_number=next_build)
                if check_build.build_status == 0:
                    update_build_sql = ModuleNameInfo.objects.filter(module_name=job_name,
                                                                         build_number=next_build, jenkins_env=jenkins_env).update(build_status=1)
                    rollback_version = buildJobParam(jenkins_env,job_name,deploy_env,version)
                    messages.add_message(request, messages.SUCCESS, '执行成功，将进行版本回滚操作！')
                    return HttpResponseRedirect(reverse('job_details',args=[jenkins_env,job_name]))
                else:
                    messages.add_message(request, messages.ERROR, '正在构建中，请稍候再试！')
                    return render(request, 'cijenkins/job_rollback.html',
                                  {"rollback_version_form": rollback_version_form,
                                   "jenkins_env": jenkins_env,"job_name": job_name})
            else:
                messages.add_message(request, messages.ERROR, '正在构建中，请稍候再试！')
                return render(request, 'cijenkins/job_rollback.html',
                              {"rollback_version_form": rollback_version_form,
                               "jenkins_env": jenkins_env, "job_name": job_name})
            return render(request, 'cijenkins/job_rollback.html',{"rollback_version_form": rollback_version_form,
                                                                  "jenkins_env": jenkins_env, "job_name": job_name})
        else:
            messages.add_message(request, messages.ERROR, '回滚版本号不能为空！')
            return render(request, 'cijenkins/job_rollback.html', {"rollback_version_form": rollback_version_form,
                                                                   "jenkins_env": jenkins_env, "job_name": job_name})
    else:
        rollback_version_form = RollBackVersionForm()
    return render(request, 'cijenkins/job_rollback.html', {"rollback_version_form": rollback_version_form,
                                                           "jenkins_env": jenkins_env, "job_name": job_name})

@login_required
@check_permission
def job_configure_views(request,jenkins_env,job_name):
    time_date = get_buildhistory(jenkins_env,job_name)
    svn_url = getconfigfile(jenkins_env,job_name)
    job_configure_form = ReconfigJobForm(
        initial={
            "repository_url":svn_url
        }
    )
    return render(request,'cijenkins/job_configure.html',{"job_configure_form": job_configure_form,
                                                         "job_name": job_name,"time_date": time_date,"jenkins_env": jenkins_env})
@login_required
@check_permission
def job_reconfig_views(request,jenkins_env,job_name):
    # form表单POST传参
    if request.method == "POST":
        job_configure_form = ReconfigJobForm(request.POST)
        if job_configure_form.is_valid():
            repository_url = request.POST.get('repository_url')
            new_repository_url = request.POST.get('new_repository_url')
            file_path = MEDIA_ROOT + '/tmp/' + job_name + "/" + "config.xml"
            replace_config = getLogin(jenkins_env).get_job_config(job_name).replace(repository_url,new_repository_url)
            if os.path.exists(file_path):
                os.remove(file_path)
                job_reconfig = getLogin(jenkins_env).reconfig_job(job_name,replace_config)
                messages.add_message(request, messages.SUCCESS, '修改配置成功！')
                return HttpResponseRedirect(reverse('job_details', args=[jenkins_env, job_name]))
            else:
                messages.add_message(request, messages.ERROR, '文件不存在，请检查后再试！')
                return render(request,'cijenkins/job_configure.html',locals())
    else:
        job_configure_form = ReconfigJobForm()
    return render(request, 'cijenkins/job_configure.html', {"job_configure_form": job_configure_form,
                                                           "jenkins_env": jenkins_env, "job_name": job_name})
