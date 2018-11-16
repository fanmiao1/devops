import requests,sys

from django.contrib.auth.models import User

from .models import Message
from workflow.models import *
from database.models import *
from worksheet.models import *
from workflow.get_name_by_id import get_name_by_id
from django.utils import timezone
from worksheet.wechatApi import GetUserIdByEmail
from devops.settings import DOMAIN, EMAIL_API
from worksheet.getCurrentDomain import get_current_domain

def send_wechat_msg(body):
    requests.post('127.0.0.1:8011/api/v1/msg/wechat', json=body)

def build_message(*args,**kwargs):
    message_title = ''
    message_content = ''
    message_url = ''
    message_user = ''
    if kwargs['message_title']:
        message_title = kwargs['message_title']
    if kwargs['message_content']:
        message_content = kwargs['message_content']
    if kwargs['message_url']:
        message_url = kwargs['message_url']
    if kwargs['message_user']:
        message_user = kwargs['message_user']
    try:
        if kwargs['type']:
            type = kwargs['type']
        else:
            type = 'default'
    except:
        type = 'default'
    time = timezone.now()
    status = 0

    email = User.objects.get(id=message_user).email
    # wechat_body = {
    #     'touser': GetUserIdByEmail(email=email, department_id=346).getUserId(),
    #     'msgtype': 'textcard',
    #     'textcard': {
    #         'title': '消息通知',
    #         'description': '<div>xxxx</div> ',
    #         'url': message_url,
    #         'btntxt': '详情'
    #     }
    # }
    body_model = '''
<tbody>
<tr>
    <td>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600"
               style="border: none; border-collapse: collapse;">
            <tbody>
            <tr>
                <td style="padding: 10px 0; border: none; vertical-align: middle;"><strong style="font-size: 16px">深圳市傲基电子商务股份有限公司</strong>
                </td>
            </tr>
            </tbody>
        </table>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600"
               style="border-collapse: collapse; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
            <tbody>
            <tr>
                <td>
                    <table cellpadding="0" cellspacing="0" width="600" style="border: none; border-collapse: collapse;">
                        <tbody>
                        <tr>
                            <td style="padding: 10px; background-color: #F8FAFE; border: none; font-size: 14px; font-weight: 500; border-bottom: 1px solid #e5e5e5;">
                                <a href="model_url"
                                   style="color: #333; text-decoration: underline;" target="_blank">model_title</a>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; border: none;">
                    <fieldset style="border: 1px solid #e5e5e5">
                        <legend style="color: #114f8e">描述</legend>
                        <div style="padding:5px;"><p class="MsoNormal" style="text-indent:21pt;"><span
                                style="font-family:'幼圆';">model_content</span></p>
                            <ul>
                                <li><a href="model_url" target="_blank"
                                                 rel="noreferrer noopener">查看详情</a>
                                </li>
                            </ul>
                        </div>
                    </fieldset>
                </td>
            </tr>
            <tr>
            </tr>
            </tbody>
        </table>
    </td>
</tr>
</tbody>
    '''
    domain_cu = get_current_domain()
    if domain_cu != 'devops.aukeyit.com':
        test_list = ['xiaopengfei@aukeys.com','xieyuzheng@aukeys.com',
                     'zhangzhiping@aukeys.com','devops@aukeys.com','qingyuwen@aukeys.com']
        if email not in test_list:
            return False

    filter_list = ['joey@aukeys.com']
    if email in filter_list:
        return False

    if domain_cu == 'devops.aukeyit.com':
        is_valid = True if GetUserIdByEmail(email=email, department_id=321, fetch_child=1).getUserId() else False
    else:
        is_valid = True
    if is_valid:
        email_body = {
            'to': [email],
            'cc': [],
            'subject': '运维平台消息通知',
            'type': 'text/html',
            'body': body_model.replace('model_title', message_title).replace('model_content', message_content)
                .replace('model_url', 'http://'+get_current_domain()+message_url)
        }
        try:
            requests.post(EMAIL_API, json=email_body)
        except Exception as _:
            pass

    add_message = Message()
    add_message.title = message_title
    add_message.content = message_content
    add_message.url = message_url
    add_message.time = time
    add_message.type = type
    add_message.user_id = int(message_user)
    add_message.status = status
    add_message.save()


class send_message(object):
    '''

    调用方法:
    必须带两个参数,action(动作),detail_id(表id);
    从第一个审批人/部门审批后,通知下一位审批人/部门审批, 需追加一个参数adopt = '通过'/'不通过', 最后一个审批人/部门审批后,不需要加adopt参数;
    若adopt='通过', 需再追加一个参数sector(审批部门)，如sector = '采购部'.

    例1(申请后，自动通知第一位审批人/部门审批,只需要2个参数):
    send_message(action = '项目创建', detail_id = 'id')

    例2(审批不通过,需要带上参数adopt='不通过',不需要sector参数):
    send_message(action = '项目创建审批', detail_id = 'id', adopt = '不通过')

    例3(审批通过,如果存在后续人/部门审批,需要adopt='通过'和sector参数):
    send_message(action = '项目创建审批', detail_id = 'id', adopt = '通过', sector = '采购部')

    例4(最后一个审批人/部门审批完成(不存在后续人/部门审批)):
    send_message(action = '项目创建审批通过', detail_id = 'id')

    '''
    def __init__(self,**kwargs):
        self.detail_id = kwargs['detail_id']

        if kwargs['action'] == '项目创建':
            send_message.project_create(self)
        elif kwargs['action'] == '项目创建审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.project_create_approval(self)
        elif kwargs['action'] == '项目创建审批通过':
            send_message.project_create_adopted(self)
        elif kwargs['action'] == '项目成员申请':
            send_message.project_member_apply(self)
        elif kwargs['action'] == '项目成员申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.project_member_apply_approval(self)
        elif kwargs['action'] == '项目成员申请审批通过':
            send_message.project_member_apply_adopted(self)
        elif kwargs['action'] == '计划任务申请':
            send_message.cron_apply(self)
        elif kwargs['action'] == '计划任务申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.cron_apply_approval(self)
        elif kwargs['action'] == '计划任务申请审批通过':
            send_message.cron_apply_approval_adopted(self)
        elif kwargs['action'] == '添加计划任务完成':
            send_message.cron_increase(self)
        elif kwargs['action'] == '项目变更申请':
            send_message.project_release_apply(self)
        elif kwargs['action'] == '项目变更申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.project_release_apply_approval(self)
        elif kwargs['action'] == '项目变更申请审批通过':
            send_message.project_release_apply_approval_adopted(self)
        elif kwargs['action'] == '项目变更执行完成':
            send_message.project_release_success(self)
        elif kwargs['action'] == '项目用户变更申请':
            send_message.project_user_release_apply(self)
        elif kwargs['action'] == '项目用户变更申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.project_user_release_apply_approval(self)
        elif kwargs['action'] == '项目用户变更申请审批通过':
            send_message.project_user_release_apply_approval_adopted(self)
        elif kwargs['action'] == '项目用户变更完成':
            send_message.project_user_release_success(self)
        elif kwargs['action'] == '项目用户权限变更申请':
            send_message.project_user_authority_release_apply(self)
        elif kwargs['action'] == '项目用户权限变更申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.project_user_authority_release_apply_approval(self)
        elif kwargs['action'] == '项目用户权限变更申请审批通过':
            send_message.project_user_authority_release_apply_approval_adopted(self)
        elif kwargs['action'] == '项目用户权限变更完成':
            send_message.project_user_authority_release_success(self)
        elif kwargs['action'] == '数据库变更申请':
            send_message.database_release_apply(self)
        elif kwargs['action'] == '数据库变更申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.database_release_apply_approval(self)
        elif kwargs['action'] == '数据库变更申请审批通过':
            send_message.database_release_apply_approval_adopted(self)
        elif kwargs['action'] == '数据库变更执行成功':
            send_message.database_release_success(self)
        elif kwargs['action'] == '数据库变更执行失败':
            send_message.database_release_failed(self)
        elif kwargs['action'] == '数据预警SQL申请':
            send_message.sqlalert_apply(self)
        elif kwargs['action'] == '数据预警SQL申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.sqlalert_approval(self)
        elif kwargs['action'] == '数据预警SQL申请审批通过':
            send_message.sqlalert_approval_adopted(self)
        elif kwargs['action'] == '数据预警SQL已启用':
            send_message.sqlalert_enable(self)
        elif kwargs['action'] == '数据预警SQL已停用':
            send_message.sqlalert_disable(self)
        elif kwargs['action'] == '预警SQL数据报警':
            send_message.sqlalert_alarm(self)
        elif kwargs['action'] == '预警SQL删除操作':
            send_message.sqlalert_remove(self)
        elif kwargs['action'] == '数据迁移申请':
            send_message.migration_apply(self)
        elif kwargs['action'] == '数据迁移申请审批':
            self.adopt = kwargs['adopt']
            if self.adopt == '通过':
                self.sector = kwargs['sector']
            send_message.migration_approval(self)
        elif kwargs['action'] == '数据迁移申请审批通过':
            send_message.migration_approval_adopted(self)
        elif kwargs['action'] == '数据迁移执行成功':
            send_message.migration_success(self)
        elif kwargs['action'] == '数据迁移执行失败':
            send_message.migration_failed(self)

    '''项目创建'''
    def project_create(self):
        applicant = project.objects.only('applicant').get(id=self.detail_id).applicant
        project_manager_id = project.objects.only('project_manager').get(id=self.detail_id).project_manager.id
        build_message(
            **{'message_title': '申请「项目创建」成功',
               'message_content': '申请「项目创建」成功',
               'message_url': '/flow/project_manage/project_details/' + str(self.detail_id),
               'message_user': applicant.id
            }
        )

        build_message(
            **{'message_title': '有一条「项目创建」工作流需要您审批',
               'message_content': get_name_by_id.get_name(applicant.id) + '申请了「项目创建」, 下一步(项目经理审批)需要您去审批！',
               'message_url': '/flow/project_manage/project_details/' + str(self.detail_id),
               'message_user': project_manager_id,
               'type': '审批'

            }
        )


    def project_create_approval(self):
        applicant = project.objects.only('applicant').get(id=self.detail_id).applicant
        if self.adopt == '通过':
            userList = Group.objects.get(name=self.sector).user_set.all()
            for sector_user_id in userList:
                build_message(
                    **{'message_title': '有一条「项目创建」工作流需要您审批',
                       'message_content': get_name_by_id.get_name(applicant.id) + '申请了「项目创建」工作流, 下一步('+ self.sector +'审批)需要您去审批！',
                       'message_url': '/flow/project_manage/project_details/' + str(self.detail_id),
                       'message_user': sector_user_id.id,
                        'type': '审批'
                    }
                )
        elif self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「项目创建」审批不通过',
                   'message_content': '您申请的「项目创建」审批不通过',
                   'message_url': '/flow/project_manage/project_details/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )


    def project_create_adopted(self):
        applicant = project.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「项目创建」已经审批通过',
               'message_content': '您申请的「项目创建」已经审批通过',
               'message_url': '/flow/project_manage/project_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )


    '''项目成员申请'''
    def project_member_apply(self):
        applicant = project_userflow.objects.only('applicant').get(id=self.detail_id).applicant
        project_manager_id = project_userflow.objects.only('project').get(
            id=self.detail_id).project.project_manager.id

        build_message(
            **{'message_title': '申请「项目成员变更」成功',
               'message_content': '申请「项目成员变更」成功',
               'message_url': '/flow/project_member_manage/details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条申请「项目成员变更」工作流需要您审批',
               'message_content': get_name_by_id.get_name(applicant.id) + '申请了「项目成员变更」, (项目经理审批)需要您去审批！',
               'message_url': '/flow/project_member_manage/details/' + str(self.detail_id),
               'message_user': project_manager_id,
               'type': '审批'
               }
        )


    def project_member_apply_approval(self):
        applicant = project_userflow.objects.only('applicant').get(id=self.detail_id).applicant
        if self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请「项目成员变更」审批不通过',
                   'message_content': '您申请「项目成员变更」审批不通过',
                   'message_url': '/flow/project_member_manage/details/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )


    def project_member_apply_adopted(self):
        applicant = project_userflow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请「项目成员变更」已经审批通过',
               'message_content': '您申请「项目成员变更」已经审批通过',
               'message_url': '/flow/project_member_manage/details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )


    '''计划任务申请'''
    def cron_apply(self):
        applicant = cronflow.objects.only('applicant').get(id=self.detail_id).applicant
        project_manager_id = cronflow.objects.only('project').get(id=self.detail_id).project.project_manager.id

        build_message(
            **{'message_title': '申请「计划任务变更」成功',
               'message_content': '申请「计划任务变更」成功',
               'message_url': '/flow/cronflow_manage/cronflow_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条申请「计划任务变更」工作流需要您审批',
               'message_content': get_name_by_id.get_name(applicant.id) + '申请了「计划任务变更」, (项目经理审批)需要您去审批！',
               'message_url': '/flow/cronflow_manage/cronflow_details/' + str(self.detail_id),
               'message_user': project_manager_id,
               'type': '审批'
               }
        )


    def cron_apply_approval(self):
        applicant = cronflow.objects.only('applicant').get(id=self.detail_id).applicant
        if self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「计划任务变更」审批不通过',
                   'message_content': '您申请的「计划任务变更」审批不通过',
                   'message_url': '/flow/cronflow_manage/cronflow_details/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )


    def cron_apply_approval_adopted(self):
        applicant = cronflow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「计划任务变更」已经审批通过',
               'message_content': '您申请的「计划任务变更」已经审批通过',
               'message_url': '/flow/cronflow_manage/cronflow_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )
        try:
            project_id = cronflow.objects.only('project').get(id=self.detail_id).project_id
            appoint_user_list = project_group.objects.filter(project_id=project_id,user_type__name='运维人员').values_list('user_id',flat=True)
            for sector_user_id in appoint_user_list:
                build_message(
                    **{'message_title': '有一条「计划任务变更」工作流需要您执行',
                       'message_content': get_name_by_id.get_name(applicant.id) +
                                          '申请了「计划任务变更」, 项目经理审批已经通过, 下一步需要您执行！',
                       'message_url': '/flow/cronflow_manage/cronflow_details/' + str(self.detail_id),
                       'message_user': sector_user_id,
                       'type': '执行'
                   }
                )
        except:
            pass


    def cron_increase(self):
        applicant = cronflow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「计划任务变更」已经添加成功',
               'message_content': '您申请的「计划任务变更」已经添加成功',
               'message_url': '/flow/cronflow_manage/cronflow_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )


    '''项目变更申请'''
    def project_release_apply(self):
        applicant = project_releaseflow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '申请「项目变更」成功',
               'message_content': '申请「项目变更」成功',
               'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )
        try:
            project_id = project_releaseflow.objects.only('project').get(id=self.detail_id).project_id
            appoint_user_list = project_group.objects.filter(project_id=project_id,user_type__name='测试人员').values_list('user_id',flat=True)
            for sector_user_id in appoint_user_list:
                build_message(
                    **{'message_title': '有一条「项目变更」工作流需要您测试审批',
                       'message_content': get_name_by_id.get_name(applicant.id) + '申请了「项目变更」工作流, 下一步(测试审批)需要您去审批！',
                       'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
                       'message_user': sector_user_id,
                       'type': '审批'
                       }
                )
        except:
            pass


    def project_release_apply_approval(self):
        applicant = project_releaseflow.objects.only('applicant').get(id=self.detail_id).applicant
        if self.adopt == '通过':
            project_manager_id = project_releaseflow.objects.only('project').get(
                id=self.detail_id).project.project_manager.id
            build_message(
                **{'message_title': '有一条「项目变更」工作流需要您审批',
                   'message_content': get_name_by_id.get_name(applicant.id) + '申请了「项目变更」, 下一步(项目经理审批)需要您去审批！',
                   'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
                   'message_user': project_manager_id,
                   'type': '审批'
                   }
            )
        elif self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「项目变更」审批不通过',
                   'message_content': '您申请的「项目变更」审批不通过',
                   'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )


    def project_release_apply_approval_adopted(self):
        applicant = project_releaseflow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「项目变更」已经审批通过, 等待执行变更',
               'message_content': '您申请的「项目变更」已经审批通过, 等待执行变更',
               'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )
        try:
            project_id = project_releaseflow.objects.only('project').get(id=self.detail_id).project_id
            appoint_user_list = project_group.objects.filter(project_id=project_id,user_type__name='运维人员').values_list('user_id',flat=True)
            for sector_user_id in appoint_user_list:
                build_message(
                    **{'message_title': '「项目变更」等待您执行变更',
                       'message_content': get_name_by_id.get_name(applicant.id) +
                                          '申请了「项目变更」, 测试审批和项目经理审批已经通过, 下一步(执行)需要您执行变更！',
                       'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
                       'message_user': sector_user_id,
                       'type': '执行'
                       }
                )
        except:
            pass


    def project_release_success(self):
        applicant = project_releaseflow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「项目变更」已经发布完成',
               'message_content': '您申请的「项目变更」已经发布完成',
               'message_url': '/flow/releaseflow_manage/releaseflow_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )


    '''项目用户变更申请'''
    def project_user_release_apply(self):
        applicant = ProjectUserApplyFlow.objects.only('submitter').get(id=self.detail_id).submitter
        depart_director_id = ProjectUserApplyFlow.objects.only('department').get(
            id=self.detail_id).department.depart_director_id

        build_message(
            **{'message_title': '申请「业务用户变更」成功',
               'message_content': '申请「业务用户变更」成功',
               'message_url': '/flow/user_apply_list/user_apply_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条申请「业务用户变更」工作流需要您审批',
               'message_content': get_name_by_id.get_name(applicant.id) + '申请了「业务用户变更」, (部门负责人审批)需要您去审批！',
               'message_url': '/flow/user_apply_list/user_apply_details/' + str(self.detail_id),
               'message_user': depart_director_id,
               'type': '审批'
               }
        )


    def project_user_release_apply_approval(self):
        applicant = ProjectUserApplyFlow.objects.only('submitter').get(id=self.detail_id).submitter
        if self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「业务用户变更」审批不通过',
                   'message_content': '您申请的「业务用户变更」审批不通过',
                   'message_url': '/flow/user_apply_list/user_apply_details/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )


    def project_user_release_apply_approval_adopted(self):
        applicant = ProjectUserApplyFlow.objects.only('submitter').get(id=self.detail_id).submitter
        build_message(
            **{'message_title': '您申请的「业务用户变更」已经审批通过',
               'message_content': '您申请的「业务用户变更」已经审批通过',
               'message_url': '/flow/user_apply_list/user_apply_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )
        try:
            project_id = ProjectUserApplyFlow.objects.only('project').get(id=self.detail_id).project_id
            appoint_user_list = project_group.objects.filter(project_id=project_id,user_type__name='运维人员').values_list('user_id',flat=True)
            for sector_user_id in appoint_user_list:
                build_message(
                    **{'message_title': '有一条「业务用户变更」需要您执行',
                       'message_content': get_name_by_id.get_name(applicant.id) +
                                          '申请了「业务用户变更」, 部门负责人审批已经通过, 下一步需要您执行！',
                       'message_url': '/flow/user_apply_list/user_apply_details/' + str(self.detail_id),
                       'message_user': sector_user_id,
                        'type': '执行'
                   }
                )
        except:
            pass

    def project_user_release_success(self):
        applicant = ProjectUserApplyFlow.objects.only('submitter').get(id=self.detail_id).submitter
        build_message(
            **{'message_title': '您申请的「业务用户变更」已经变更完成',
               'message_content': '您申请的「业务用户变更」已经变更完成',
               'message_url': '/flow/user_apply_list/user_apply_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

    '''项目用户权限变更申请'''
    def project_user_authority_release_apply(self):
        applicant = authority_flow.objects.only('applicant').get(id=self.detail_id).applicant
        depart_director_id = authority_flow.objects.only('department').get(
            id=self.detail_id).department.depart_director_id

        build_message(
            **{'message_title': '申请「业务用户权限变更」成功',
               'message_content': '申请「业务用户权限变更」成功',
               'message_url': '/flow/project_authority_manage/project_authority_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条申请「业务用户权限变更」工作流需要您审批',
               'message_content': get_name_by_id.get_name(applicant.id) + '申请了业务用户权限变更, (部门负责人审批)需要您去审批！',
               'message_url': '/flow/project_authority_manage/project_authority_details/' + str(self.detail_id),
               'message_user': depart_director_id,
               'type': '审批'
               }
        )

    def project_user_authority_release_apply_approval(self):
        applicant = authority_flow.objects.only('applicant').get(id=self.detail_id).applicant
        if self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「业务用户权限变更」审批不通过',
                   'message_content': '您申请的「业务用户权限变更」审批不通过',
                   'message_url': '/flow/project_authority_manage/project_authority_details/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )

    def project_user_authority_release_apply_approval_adopted(self):
        applicant = authority_flow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「业务用户权限变更」已经审批通过',
               'message_content': '您申请的「业务用户权限变更」已经审批通过',
               'message_url': '/flow/project_authority_manage/project_authority_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )
        try:
            project_id = authority_flow.objects.only('project').get(id=self.detail_id).project_id
            appoint_user_list = project_group.objects.filter(project_id=project_id,user_type__name='运维人员').values_list('user_id',flat=True)
            for sector_user_id in appoint_user_list:
                build_message(
                    **{'message_title': '有一条「业务用户权限变更」需要您执行',
                       'message_content': get_name_by_id.get_name(applicant.id) +
                                          '申请了「业务用户权限变更」, 部门负责人审批已经通过, 下一步需要您执行！',
                       'message_url': '/flow/project_authority_manage/project_authority_details/' + str(self.detail_id),
                       'message_user': sector_user_id,
                       'type': '执行'
                   }
                )
        except:
            pass

    def project_user_authority_release_success(self):
        applicant = authority_flow.objects.only('applicant').get(id=self.detail_id).applicant
        build_message(
            **{'message_title': '您申请的「业务用户权限变更」已经执行完成',
               'message_content': '您申请的「业务用户权限变更」已经执行完成',
               'message_url': '/flow/project_authority_manage/project_authority_details/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

    '''数据库变更申请'''

    def database_release_apply(self):
        applicant = Application.objects.only('appliant').get(id=self.detail_id).appliant
        project_manager_id = Application.objects.only('project').get(id=self.detail_id).project.project_manager.id
        build_message(
            **{'message_title': '申请「数据库变更」成功',
               'message_content': '申请「数据库变更」成功',
               'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条「数据库变更」申请需要您审批',
               'message_content': get_name_by_id.get_name(applicant.id) + '申请了「数据库变更」, 下一步(项目经理审批)需要您去审批！',
               'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
               'message_user': project_manager_id,
               'type': '审批'
               }
        )

    def database_release_apply_approval(self):
        applicant = Application.objects.only('appliant').get(id=self.detail_id).appliant
        if self.adopt == '通过':
            userList = Group.objects.get(name=self.sector).user_set.all()
            for sector_user_id in userList:
                build_message(
                    **{'message_title': '有一条「数据库变更」申请需要您审批',
                       'message_content': get_name_by_id.get_name(
                           applicant.id) + '申请了「数据库变更」, 下一步(' + self.sector + '审批)需要您去审批！',
                       'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
                       'message_user': sector_user_id.id,
                       'type': '审批'
                       }
                )
        elif self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「数据库变更」审批不通过',
                   'message_content': '您申请的「数据库变更」审批不通过',
                   'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
                   'message_user': applicant.id
                   }
            )

    def database_release_apply_approval_adopted(self):
        applicant = Application.objects.only('appliant').get(id=self.detail_id).appliant
        build_message(
            **{'message_title': '您申请的「数据库变更」已经审批通过',
               'message_content': '您申请的「数据库变更」已经审批通过',
               'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

    def database_release_success(self):
        applicant = Application.objects.only('appliant').get(id=self.detail_id).appliant
        build_message(
            **{'message_title': '您申请的「数据库变更」已经执行成功',
               'message_content': '您申请的「数据库变更」已经执行成功',
               'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

    def database_release_failed(self):
        applicant = Application.objects.only('appliant').get(id=self.detail_id).appliant
        build_message(
            **{'message_title': '您申请的「数据库变更」执行失败了',
               'message_content': '您申请的「数据库变更」执行失败了',
               'message_url': '/database/instance/release_flow/release_detail/' + str(self.detail_id),
               'message_user': applicant.id
               }
        )

    '''数据预警SQL申请'''

    def sqlalert_apply(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        project_manager_id = SQLAlert.objects.only('project').get(id=self.detail_id).project.project_manager.id
        build_message(
            **{'message_title': '申请「数据预警SQL」成功',
               'message_content': '申请「' + sql_alert.title + '」成功',
               'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
               'message_user': sql_alert.applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条「数据预警SQL」申请需要您审批',
               'message_content': get_name_by_id.get_name(sql_alert.applicant.id) + '申请了「' + sql_alert.title + '」, 下一步(项目经理审批)需要您去审批！',
               'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
               'message_user': project_manager_id,
               'type': '审批'
               }
        )

    def sqlalert_approval(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        if self.adopt == '通过':
            userList = Group.objects.get(name=self.sector).user_set.all()
            for sector_user_id in userList:
                build_message(
                    **{'message_title': '有一条「数据预警SQL」申请需要您审批',
                       'message_content': get_name_by_id.get_name(
                           sql_alert.applicant.id) + '申请了「' + sql_alert.title + '」, 下一步(' + self.sector + '审批)需要您去审批！',
                       'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
                       'message_user': sector_user_id.id,
                       'type': '审批'
                       }
                )
        elif self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「数据预警SQL」审批不通过',
                   'message_content': '您申请的「' + sql_alert.title + '」审批不通过',
                   'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
                   'message_user': sql_alert.applicant.id
                   }
            )

    def sqlalert_approval_adopted(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        build_message(
            **{'message_title': '您申请的「数据预警SQL」已经审批通过',
               'message_content': '您申请的「' + sql_alert.title + '」已经审批通过',
               'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
               'message_user': sql_alert.applicant.id
               }
        )

    def sqlalert_enable(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        email_id = [sql_alert.applicant.id]
        email_id.extend(project_group.objects.filter(project=sql_alert.project,
                                                     user_type=Group.objects.get(
                                                         name='项目经理')).values_list('user_id', flat=True))

        email_id.extend(list(map(int, sql_alert.carbon_copy.split(','))) if sql_alert.carbon_copy else '')

        for cc_id in list(set(email_id)):
            build_message(
                **{'message_title': '「数据预警SQL」启用消息',
                   'message_content': '「' + sql_alert.title + '」已启用',
                   'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
                   'message_user': cc_id
                   }
            )

    def sqlalert_disable(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        email_id = [sql_alert.applicant.id]
        email_id.extend(project_group.objects.filter(project=sql_alert.project,
                                                     user_type=Group.objects.get(
                                                         name='项目经理')).values_list('user_id', flat=True))
        email_id.extend(list(map(int, sql_alert.carbon_copy.split(','))) if sql_alert.carbon_copy else '')

        for cc_id in list(set(email_id)):
            build_message(
                **{'message_title': '「数据预警SQL」停用消息',
                   'message_content': '「' + sql_alert.title + '」已停用',
                   'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
                   'message_user': cc_id
                   }
            )

    def sqlalert_alarm(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        email_id = [sql_alert.applicant.id]
        email_id.extend(project_group.objects.filter(project=sql_alert.project,
                                                     user_type=Group.objects.get(
                                                         name='项目经理')).values_list('user_id', flat=True))
        email_id.extend(list(map(int, sql_alert.carbon_copy.split(','))) if sql_alert.carbon_copy else '')

        for cc_id in list(set(email_id)):
            build_message(
                **{'message_title': '有一条「数据预警SQL」报警消息',
                   'message_content': '有一条「' + sql_alert.title + '」数据报警消息',
                   'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
                   'message_user': cc_id
                   }
            )

    def sqlalert_remove(self):
        sql_alert = SQLAlert.objects.get(id=self.detail_id)
        email_id = [sql_alert.applicant.id]
        email_id.extend(project_group.objects.filter(project=sql_alert.project,
                                                     user_type=Group.objects.get(
                                                         name='项目经理')).values_list('user_id', flat=True))
        email_id.extend(list(map(int, sql_alert.carbon_copy.split(','))) if sql_alert.carbon_copy else '')

        for cc_id in list(set(email_id)):
            build_message(
                **{'message_title': '「数据预警SQL」删除消息',
                   'message_content': '「' + sql_alert.title + '」已删除',
                   'message_url': '/database/instance/sqlalert/release_detail/' + str(self.detail_id) + '/',
                   'message_user': cc_id
                   }
            )

    '''数据迁移申请'''
    def migration_apply(self):
        migration = DataMigrate.objects.get(id=self.detail_id)
        project_manager_id = DataMigrate.objects.only('project').get(id=self.detail_id).project.project_manager.id
        build_message(
            **{'message_title': '申请「数据迁移」成功',
               'message_content': '申请「' + migration.title + '」成功',
               'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
               'message_user': migration.applicant.id
               }
        )

        build_message(
            **{'message_title': '有一条「数据迁移」申请需要您审批',
               'message_content': get_name_by_id.get_name(
                   migration.applicant.id) + '申请了「' + migration.title + '」, 下一步(项目经理审批)需要您去审批！',
               'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
               'message_user': project_manager_id,
               'type': '审批'
               }
        )

    def migration_approval(self):
        migration = DataMigrate.objects.get(id=self.detail_id)
        if self.adopt == '通过':
            userList = Group.objects.get(name=self.sector).user_set.all()
            for sector_user_id in userList:
                build_message(
                    **{'message_title': '有一条「数据迁移」申请需要您审批',
                       'message_content': get_name_by_id.get_name(
                           migration.applicant.id) + '申请了「' + migration.title + '」, 下一步(' + self.sector + '审批)需要您去审批！',
                       'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
                       'message_user': sector_user_id.id,
                       'type': '审批'
                       }
                )
        elif self.adopt == '不通过':
            build_message(
                **{'message_title': '您申请的「数据迁移」审批不通过',
                   'message_content': '您申请的「' + migration.title + '」审批不通过',
                   'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
                   'message_user': migration.applicant.id
                   }
            )

    def migration_approval_adopted(self):
        migration = DataMigrate.objects.get(id=self.detail_id)
        build_message(
            **{'message_title': '您申请的「数据迁移」已经审批通过',
               'message_content': '您申请的「' + migration.title + '」已经审批通过',
               'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
               'message_user': migration.applicant.id
               }
        )

    def migration_success(self):
        migration = DataMigrate.objects.get(id=self.detail_id)
        build_message(
            **{'message_title': '您申请的「数据迁移」已经执行成功',
               'message_content': '您申请的「' + migration.title + '」已经执行成功',
               'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
               'message_user': migration.applicant.id
               }
        )

    def migration_failed(self):
        migration = DataMigrate.objects.get(id=self.detail_id)
        build_message(
            **{'message_title': '您申请的「数据迁移」执行失败了',
               'message_content': '您申请的「' + migration.title + '」执行失败了',
               'message_url': '/database/instance/datamigrate/release_detail/' + str(self.detail_id) + '/',
               'message_user': migration.applicant.id
               }
        )
