from .models import *
from database.models import *
from django.db.models import Q
from django.db.models import Sum, Count

def get_project_flow_count(startdate, enddate):
    all_count = project.objects.filter(applicationtime__range=(startdate,enddate)).count()
    through_count = project.objects.filter(status=9,applicationtime__range=(startdate,enddate)).count()
    no_approval_count = project.objects.filter(applicationtime__range=(startdate,enddate)).exclude(Q(status=9)|Q(status=0)).count()
    no_through_count = project.objects.filter(status=0,applicationtime__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict


def get_project_userflow_count(startdate, enddate):
    all_count = project_userflow.objects.filter(applicationtime__range=(startdate,enddate)).count()
    through_count = project_userflow.objects.filter(status=9,applicationtime__range=(startdate,enddate)).count()
    no_approval_count = project_userflow.objects.filter(applicationtime__range=(startdate,enddate)).exclude(Q(status=9)|Q(status=0)).count()
    no_through_count = project_userflow.objects.filter(status=0,applicationtime__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict


def get_cronflow_count(startdate, enddate):
    all_count = cronflow.objects.filter(applicationtime__range=(startdate,enddate)).count()
    through_count = cronflow.objects.filter(status=9,applicationtime__range=(startdate,enddate)).count()
    no_approval_count = cronflow.objects.filter(applicationtime__range=(startdate,enddate)).exclude(Q(status=9)|Q(status=0)).count()
    no_through_count = cronflow.objects.filter(status=0,applicationtime__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict


def get_project_releaseflow_count(startdate, enddate):
    all_count = project_releaseflow.objects.filter(applicationtime__range=(startdate,enddate)).count()
    through_count = project_releaseflow.objects.filter(status=3,applicationtime__range=(startdate,enddate)).count()
    no_approval_count = project_releaseflow.objects.filter(applicationtime__range=(startdate,enddate)).exclude(Q(status=3)|Q(status=0)).count()
    no_through_count = project_releaseflow.objects.filter(status=0,applicationtime__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict


def get_user_apply_flow_count(startdate, enddate):
    all_count = ProjectUserApplyFlow.objects.filter(applicationtime__range=(startdate,enddate)).count()
    through_count = ProjectUserApplyFlow.objects.filter(status=9,applicationtime__range=(startdate,enddate)).count()
    no_approval_count = ProjectUserApplyFlow.objects.filter(applicationtime__range=(startdate,enddate)).exclude(Q(status=9)|Q(status=0)).count()
    no_through_count = ProjectUserApplyFlow.objects.filter(status=0,applicationtime__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict


def get_authority_flow_count(startdate, enddate):
    all_count = authority_flow.objects.filter(applicationtime__range=(startdate,enddate)).count()
    through_count = authority_flow.objects.filter(status=3,applicationtime__range=(startdate,enddate)).count()
    no_approval_count = authority_flow.objects.filter(applicationtime__range=(startdate,enddate)).exclude(Q(status=3)|Q(status=0)).count()
    no_through_count = authority_flow.objects.filter(status=0,applicationtime__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict


def get_database_release_count(startdate, enddate):
    all_count = Application.objects.filter(application_time__range=(startdate,enddate)).count()
    through_count = Application.objects.filter(application_status=4,application_time__range=(startdate,enddate)).count()
    no_approval_count = Application.objects.filter(application_time__range=(startdate,enddate)).exclude(Q(application_status=4)|Q(application_status=0)).count()
    no_through_count = Application.objects.filter(application_status=0,application_time__range=(startdate,enddate)).count()
    count_dict = {
        'all_count' : all_count, 
        'through_count' : through_count,
        'no_approval_count' : no_approval_count,
        'no_through_count': no_through_count
    }
    return count_dict

def get_workflow_total_count():
    count = 0
    try:
        count = project.objects.all().count() + project_userflow.objects.all().count() + \
                ProjectUserApplyFlow.objects.all().count() + authority_flow.objects.all().count() + \
                project_releaseflow.objects.all().count() + Application.objects.all().count() + \
                cronflow.objects.all().count()
    except Exception as e:
        print ('The total of statistical workflow is abnormal, Error : ' + str(e))
        pass
    return count