from cijenkins.jenkinsAPI import *
import time


def get_buildhistory(jenkins_env,job_name):
    buildhistory = getLogin(jenkins_env).get_job_info(job_name)['builds']

    time_dict = []
    for i in buildhistory:
        try:
            string_num = i['number']
            buildresult = getLogin(jenkins_env).get_build_info(job_name, string_num)['result']
            builddate = getLogin(jenkins_env).get_build_info(job_name, string_num)['timestamp']
            time_local = time.localtime(builddate / 1000)
            build_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            time_dict.append({'number': string_num, 'time': build_datetime, 'result': buildresult})
        except:
            continue
    return time_dict if time_dict else ""