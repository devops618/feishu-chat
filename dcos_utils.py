import os

from common_utils import *


def app_publish(message_id, publish_type, publish_version, publish_auditor, time_now):
    env = publish_version.split("registry")[0]
    app_id = publish_version.split("registry:5000")[1].split(":")[0]

    # 替换pre环境镜像仓库地址
    if env == "pre":
        # preregistry:5000/tsp/msbatterymonitor:35-c66e2652
        # harbor-pre.dfiov.com.cn:5000/tsp/msbatterymonitor:35-c66e2652
        version_tmp = publish_version.split("registry:5000")[1]
        publish_version_tmp = "harbor-pre.dfiov.com.cn:5000" + version_tmp
    else:
        publish_version_tmp = publish_version

    # 获取app当前配置
    app_url = eval("dcos_" + env) + app_id
    print(app_url)
    response = requests.get(app_url, headers=headers)
    data_tmp = json.loads(response.text)

    # 判断版本是否一致，不一致才发布
    if data_tmp["app"]["container"]["docker"]["image"] != publish_version_tmp:
        # 镜像同步
        remote_shell_exec(image_sync_host, image_sync_host_user, image_sync_host_pass, image_sync_shell_file,
                          publish_version)

        # 修改镜像版本
        data = {}
        data_tmp["app"]["container"]["docker"]["image"] = publish_version_tmp
        data["container"] = data_tmp["app"]["container"]
        data = json.dumps(data)
        print(data)

        # 发布新版本
        requests.put(url=app_url + "?force=true", headers=headers, data=data)

        # 获取app的状态
        res = get_app_status(publish_type, app_id, env, publish_version)
        if res == "true":
            # 更新消息卡片
            content = publish_card("发布通知", "发布完成", "", publish_version, env, publish_auditor,
                                   time_now)
            patch_msg_req(message_id, content)
            # 发布结果推送至 Prometheus Pushgateway
            publish_status_push(publish_version, env, "成功")
        elif res == "false":
            content = publish_card("发布通知", "发布失败", "", publish_version, env, publish_auditor,
                                   time_now)
            patch_msg_req(message_id, content)
            publish_status_push(publish_version, env, "失败")
    else:
        content = publish_card("发布通知", "发布重复", "", publish_version, env, publish_auditor,
                               time_now)
        patch_msg_req(message_id, content)


def app_restart(message_id, publish_type, app_id, env, publish_auditor, time_now):
    restart_url = eval("dcos_" + env) + app_id + "/restart"
    print(restart_url)
    requests.post(url=restart_url, headers=headers)
    # 获取app的状态
    res = get_app_status(publish_type, app_id, env)
    if res == "true":
        # 更新消息卡片
        content = publish_card("重启通知", "重启完成", "", app_id, env, publish_auditor, time_now)
        patch_msg_req(message_id, content)
    elif res == "false":
        content = publish_card("重启通知", "重启失败", "", app_id, env, publish_auditor, time_now)
        patch_msg_req(message_id, content)


# 获取app task的状态
def get_task_status(data):
    task_status = "true"
    for task in data['app']['tasks']:
        print(task)
        task_status_tmp = task['healthCheckResults'][0]['alive']
        if not task_status_tmp:
            task_status = "false"
            break
    return task_status


# 获取app的状态
def get_app_status(publish_type, app_id, env, publish_version=""):
    app_url = eval("dcos_" + env) + app_id
    count = 0

    # 周期性判断app是否部署完成
    while True:
        response = requests.get(url=app_url, headers=headers)
        data = json.loads(response.text)
        deployments = data['app']['deployments']
        print(deployments)
        publish_image = data['app']['container']['docker']['image']
        app_status = ""
        # 判断app的deployments是否完成
        if len(deployments) == 0:
            app_status = "true"
            if publish_type == "publish":
                if publish_image == publish_version:
                    res = get_task_status(data)
                    if res == "false":
                        app_status = "false"
            elif publish_type == "restart":
                res = get_task_status(data)
                if res == "false":
                    app_status = "false"
        if app_status != "":
            break

        print(app_status)
        count = count + 1
        # 25分钟后退出检查
        if count == 50:
            app_status = "false"
            break
        time.sleep(30)

    return app_status


# 获取环境的所有app id
def get_app_ids(env):
    apps_list = []
    app_url = eval("dcos_" + env)
    response = requests.get(url=app_url, headers=headers)
    data = json.loads(response.text)
    for app in data['apps']:
        apps_list.append(app['id'])
    return apps_list


# 发布结果推送至 Prometheus Pushgateway
def publish_status_push(publish_version, publish_env, publish_status):
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    day = today.day
    hour = today.hour

    # sitregistry:5000/tsp/mssoibluetoothkey:850-60be42b5
    publish_version_tmp = publish_version.split("registry:5000")[1].strip()
    project_name = publish_version_tmp.split("/")[1]
    app_name = publish_version_tmp.split("/")[2].split(":")[0]
    app_version = publish_version_tmp.split("/")[2].split(":")[1]

    push_url = f"{prometheus_pushgateway}/metrics/job/pushgateway_permanent"
    push_labels1 = f"/env_type/{publish_env}/project_name/{project_name}/app_name/{app_name}/app_version/{app_version}"
    push_labels2 = f"/fb_status/{publish_status}/year/{year}/month/{month}/day/{day}/hour/{hour}"

    cmd = f"echo 'dcos_release_key' '1' | curl --data-binary  @- {push_url}{push_labels1}{push_labels2}"
    print(cmd)
    os.system(cmd)


def get_app_versions(env, app_id):
    app_url = eval("dcos_" + env) + app_id
    versions_tmp = requests.get(url=app_url + "/versions", headers=headers)
    versions = versions_tmp.json()['versions']
    versions.sort(reverse=True)

    versions_list = []
    versions_image_dict = {}
    for i in range(0, 5):
        versions_list.append(versions[i])
    for version in versions_list:
        res = requests.get(app_url + "/versions/" + version, headers=headers)
        image = res.json()['container']['docker']['image']
        version_new = str(change_timezone(version, "Asia/Shanghai"))
        versions_image_dict[version_new] = image
    versions_image_dict_sort = json.dumps(versions_image_dict, indent=0, sort_keys=True)
    return versions_image_dict_sort


def get_app_info(env, app_id):
    app_url = eval("dcos_" + env) + app_id
    response = requests.get(url=app_url, headers=headers)
    data = json.loads(response.text)
    image = data['app']['container']['docker']['image']
    instances = data['app']['instances']
    cpus = data['app']['cpus']
    mem = data['app']['mem']
    version = data['app']['version']
    version_new = change_timezone(version, "Asia/Shanghai")
    versions_image_dict = get_app_versions(env, app_id)
    tasksstaged = data['app']['tasksStaged']
    tasksrunning = data['app']['tasksRunning']
    taskshealthy = data['app']['tasksHealthy']
    tasksunhealthy = data['app']['tasksUnhealthy']
    content = (f"镜像版本: {image}\n"
               f"版本时间: {version_new}\n"
               f"历史版本: {versions_image_dict}\n"
               f"实例数: {instances}\n"
               f"CPU: {cpus}\n"
               f"内存: {mem}\n"
               f"暂停实例数: {tasksstaged}\n"
               f"运行实例数: {tasksrunning}\n"
               f"健康实例数: {taskshealthy}\n"
               f"不健康实例数: {tasksunhealthy}")
    return content


# 输入关键字查询微服务id
def find_app_id(env, query_str):
    app_ids = get_app_ids(env)
    data = [x for i, x in enumerate(app_ids) if x.find(query_str) != -1]
    return data
