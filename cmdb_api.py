from flask import Flask,request,jsonify
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mico.settings')
django.setup()
from asset.utils import goPublish
from asset.models import gogroup,goservices,minion,svn,goconf
from django.contrib import auth



app = Flask(__name__)

@app.route('/',methods=['GET'])
def message():
    return jsonify({'hi':'hello world!!'})

@app.route('/deploy',methods=['POST'])
def deploy_go():
    env = request.json.get('env')
    project = request.json.get('project')
    sub_project = request.json.get('sub_project')
    username = request.json.get('username')
    password = request.json.get('password')
    #ip = request.remote_addr
    ip = request.headers['X-Real-Ip']


    env = deploy_env(env)
    if env == 0:
        return jsonify({'result': 'The env not found.!!'})

    try:
        if login(username,password) == 1:
            if env and project and sub_project and username and ip:
                if gogroup.objects.filter(name=project):
                    if goservices.objects.filter(name=sub_project) or sub_project == "all":
                        publish = goPublish(env)
                        result = publish.deployGo(project, sub_project, username, ip)
                        print result
                        if result:
                            result = str(result)
                            if result.find('ERROR') > 0 or result.find('error') > 0 or result.find('Skip') > 0:
                                result = 'Failed'
                            else:
                                result = 'Successful'
                        else:
                            result = 'Failed'
                        return jsonify({'result': result})
                    else:
                        result = "No " + sub_project + " project!!"
                        return jsonify({'result': result})
                else:
                    result = "No " + project + " project!!"
                    return jsonify({'result': result})
            else:
                return jsonify({'result': 'argv is error!!!'})
        else:
            return jsonify({'result': 'username or password is error'})
    except Exception, e:
        print e
        return jsonify({'result': "Internal Server Error"})


@app.route('/api/subProject',methods=['POST'])
def add_sub_project():

    hostname = request.json.get('hostname')
    project = request.json.get('project')
    sub_project_name = request.json.get('sub_project_name')
    username = request.json.get('username')
    password = request.json.get('password')
    env = request.json.get('env')
    owner = request.json.get('owner')
    has_statsd = request.json.get('has_statsd')
    has_sentry = request.json.get('has_sentry')
    comment = request.json.get('comment')

    env = deploy_env(env)


    if env == 0:
        return jsonify({'result': 'The env not found.!!'})

    if login(username, password) == 1:
        if project and hostname and sub_project_name and owner and has_sentry and has_statsd and comment:
            try:
                saltminion = minion.objects.get(saltname=hostname)
                project = gogroup.objects.get(name=project)
                ip = saltminion.ip
                if goservices.objects.filter(saltminion=saltminion).filter(group=project).filter(name=sub_project_name).filter(env=env):
                    return jsonify({'result': 'The %s subproject is existing!!' % sub_project_name })
            except Exception, e:
                print e
                return jsonify({'result': 'wrong hostname or project name!!'})

            try:
                obj = goservices(ip=ip,name=sub_project_name ,env=env,group=project,saltminion=saltminion,owner=owner,has_statsd=has_statsd,has_sentry=has_sentry,comment=comment)
                obj.save()
                return jsonify({'result': 'added %s subproject is successful.!!' % sub_project_name })
            except Exception, e:
                print e
                return jsonify({'result': 'added %s subproject was failed.!!' % sub_project_name })
        else:
            return jsonify({'result': 'argv is error!!!'})
    else:
        return jsonify({'result': 'username or password is error'})


@app.route('/api/newProject',methods=['POST'])
def add_new_project():
    new_project = request.json.get('new_project')
    username = request.json.get('username')
    password = request.json.get('password')
    svn_username = request.json.get('svn_username')
    svn_password = request.json.get('svn_password')
    svn_repo = request.json.get('svn_repo')
    svn_root_path = request.json.get('svn_root_path')
    svn_move_path = request.json.get('svn_move_path')
    svn_revert_path = request.json.get('svn_revert_path')
    svn_execute_file = request.json.get('svn_execute_file')
    env = request.json.get('env')

    env = deploy_env(env)

    if env == 0:
        return jsonify({'result': 'The env not found.!!'})

    if login(username, password) == 1:
        if new_project and svn_username and svn_password and svn_repo and svn_root_path and svn_move_path and svn_revert_path and svn_execute_file:
            try:
                if gogroup.objects.filter(name=new_project):
                    return jsonify({'result': 'The %s new project is existing!!' % new_project})
                else:
                    ###added a group project
                    obj = gogroup(name=new_project)
                    obj.save()

                    ###added an info for svn table
                    project = gogroup.objects.get(name=new_project)
                    obj = svn(username=svn_username,password=svn_password,
                              repo=svn_repo,localpath=svn_root_path,
                              movepath=svn_move_path,revertpath=svn_revert_path,
                              executefile=svn_execute_file,project=project)
                    obj.save()

                    return jsonify({'result': 'added %s new subproject is successful!!' % new_project})
            except Exception, e:
                print e
                return jsonify({'result': 'added %s new subproject is failed!!' % new_project})
        else:
            return jsonify({'result': 'argv is error!!!'})
    else:
        return jsonify({'result': 'username or password is error'})



@app.route('/api/goconf',methods=['POST'])
def add_goconf():   ###added an info for goconf table
    username = request.json.get('username')
    password = request.json.get('password')
    svn_username = request.json.get('svn_username')
    svn_password = request.json.get('svn_password')
    svn_repo = request.json.get('svn_repo')
    svn_root_path = request.json.get('svn_root_path')
    project = request.json.get('project')
    hostname = request.json.get('hostname')
    env = request.json.get('env')

    env = deploy_env(env)

    if env == 0:
        return jsonify({'result': 'The env not found.!!'})

    if login(username, password) == 1:
        if svn_username and svn_password and svn_repo and svn_root_path and project and hostname:
            try:
                hostname = minion.objects.get(saltname=hostname)
                project = gogroup.objects.get(name=project)
                if goconf.objects.filter(hostname=hostname).filter(project=project).filter(env=env):
                    return jsonify({'result': 'The %s project is existing!!' % project})
                else:
                    obj = goconf(username=svn_username,password=svn_password,repo=svn_repo,localpath=svn_root_path,env=env,hostname=hostname,project=project)
                    obj.save()
                    return jsonify({'result': 'added %s goconf is successful!!' % project})
            except Exception, e:
                print e
                return jsonify({'result': 'wrong hostname or project name!!'})
        else:
            return jsonify({'result': 'argv is error!!!'})

    else:
        return jsonify({'result': 'username or password is error'})


def login(username,password):
    user = auth.authenticate(username = username,password = password)
    if user is not None:
        return 1
    else:
        return 0

def deploy_env(env):
    if env is None:
        return 1
    elif int(env) not in [1, 2]:
        return 0
    else:
        return env


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)




