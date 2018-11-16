import jenkins
from .models import JenkinsConfig


def getLogin(jenkins_env):
    jenkins_env = JenkinsConfig.objects.get(jenkins_id=jenkins_env)
    url_address = jenkins_env.url
    user_id = jenkins_env.username
    api_token = jenkins_env.token
    server = jenkins.Jenkins(url=url_address, username=user_id, password=api_token)
    return server

def getJobsList(jenkins_env):
    job_list = getLogin(jenkins_env).get_all_jobs()
    return job_list

def buildJob(jenkins_env, job_name):
    build_job = getLogin(jenkins_env).build_job(job_name)
    return build_job

def buildStatus(jenkins_env,job_name):
    last_build = getLogin(jenkins_env).get_job_info(job_name)['lastBuild']['number']
    build_status = getLogin(jenkins_env).get_build_info(job_name, last_build)['building']
    return build_status

def buildResult(jenkins_env,job_name):
    last_build = getLogin(jenkins_env).get_job_info(job_name)['lastBuild']['number']
    build_result = getLogin(jenkins_env).get_build_info(job_name, last_build)['result']
    return build_result

def jobInfo(jenkins_env,job_name):
    job_info = getLogin(jenkins_env).get_job_info(job_name)
    return job_info

def consoleOutput(jenkins_env,job_name,num_id):
    console = getLogin(jenkins_env).get_build_console_output(job_name,num_id)
    return console

def buildJobParam(jenkins_env,job_name,deploy_env,version):
    parameters = {'deploy_env':deploy_env,'version':version}
    rollback_version = getLogin(jenkins_env).build_job(job_name,parameters=parameters)
    return rollback_version
