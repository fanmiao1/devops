from cijenkins.jenkinsAPI import getLogin
from cijenkins.models import JenkinsConfig
from devops.settings import MEDIA_ROOT
import re
import os

def getconfigfile(jenkins_env,job_name):
    configfile = getLogin(jenkins_env).get_job_config(job_name)
    jobname_dic = MEDIA_ROOT + '/tmp/' + job_name
    jobname_dic_isExists = os.path.exists(jobname_dic)
    if not jobname_dic_isExists:
        os.makedirs(jobname_dic)
    file_path = MEDIA_ROOT + '/tmp/' + job_name + "/" + "config.xml"
    with open(file_path,"w+b") as fd:
        fd.write(str.encode(configfile))
        fd.close()

    if os.path.exists(file_path):
        with open(file_path,'r',encoding='UTF-8') as fp:
            read_file = fp.read()
            match_str = re.findall(r'<remote>(.*)<\/remote>',read_file)
            fp.close()
    else:
        pass
    return match_str[0]




# def reconfig_job_views(jenkins_env,job_name,remote_new,config):
#     getconfig = getLogin(jenkins_env).get_job_config(job_name)
#     modify = modifyconfig(config=getconfig)