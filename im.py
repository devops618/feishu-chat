from multiprocessing import Process

from dcos_utils import *


def time_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_help_card(chat_id: str):
    content = help_card()
    create_msg_req(chat_id, content)


def send_publish_card(chat_id: str, title, button_name, publish_type, publish_version, publish_env, publish_admins,
                      publish_time) -> None:
    content = publish_card(title, button_name, publish_type, publish_version, publish_env, publish_admins, publish_time)
    create_msg_req(chat_id, content)


# 处理消息回调
def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    global publish_user
    publish_user = data.event.sender.sender_id.open_id
    msg = data.event.message
    data = json.loads(msg.content)
    print(lark.JSON.marshal(data))

    if "帮助" in msg.content or "help" in msg.content.lower():
        send_help_card(msg.chat_id)

    if "git同步#" in msg.content.lower():
        # git同步#perf
        env = data["text"].lower().split("git同步#")[1].strip()
        publish_process = Process(target=gitlab_sync, args=(msg.chat_id, env,))
        publish_process.start()
        return

    if "查询#" in msg.content:
        # 查询#perf/tsp/msbatterymonitor
        tmp = data["text"].split("查询#")[1].strip()
        env = tmp.split("/")[0]
        app_id = tmp.split(env)[1]
        if app_id in get_app_ids(env):
            content = get_app_info(env, app_id)
            content_new = common_card("查询信息", content)
            create_msg_req(msg.chat_id, content_new)
        else:
            content_new = common_card("查询信息", "查询微服务不存在，请重试。")
            create_msg_req(msg.chat_id, content_new)

    if "查询id#" in msg.content.lower():
        # 查询id#环境/查询的关键字，例子：查询id#perf/msbatt
        tmp = data["text"].lower().split("查询id#")[1].strip()
        env = tmp.split("/")[0]
        query_str = tmp.split("/")[1]
        query_data = find_app_id(env, query_str)
        if len(query_data) != 0:
            content_new = common_card("查询微服务id", str(query_data))
            create_msg_req(msg.chat_id, content_new)
        else:
            content_new = common_card("查询微服务id", "查询微服务id不存在，请重试。")
            create_msg_req(msg.chat_id, content_new)

    if "发布#" in msg.content:
        # 发布#perfregistry:5000/tsp/msbatterymonitor:35-c66e2652
        publish_version = data["text"].split("发布#")[1].strip()
        publish_env = publish_version.split("registry:5000")[0].strip()
        if publish_env in dcos_env:
            app_id = publish_version.split("registry:5000")[1].strip().split(":")[0]
            app_ids = get_app_ids(publish_env)
            if app_id in app_ids:
                send_publish_card(msg.chat_id, "发布通知", "同意发布", "publish", publish_version, publish_env,
                                  publish_admins, time_now())
            else:
                send_publish_card(msg.chat_id, "发布通知", "版本错误", "", publish_version, publish_env, publish_admins,
                                  time_now())
        else:
            send_publish_card(msg.chat_id, "发布通知", "环境错误", "", publish_version, publish_env, publish_admins,
                              time_now())

    if "重启#" in msg.content:
        # 重启#perf/tsp/msbatterymonitor
        publish_version_tmp = data["text"].split("重启#")[1].strip()
        publish_env = publish_version_tmp.split("/")[0].strip()
        publish_version = publish_version_tmp.split(publish_env)[1].strip()
        if publish_env in dcos_env:
            app_ids = get_app_ids(publish_env)
            if publish_version in app_ids:
                send_publish_card(msg.chat_id, "重启通知", "同意重启", "restart", publish_version, publish_env,
                                  publish_admins, time_now())
            else:
                send_publish_card(msg.chat_id, "重启通知", "版本错误", "", publish_version, publish_env, publish_admins,
                                  time_now())
        else:
            send_publish_card(msg.chat_id, "重启通知", "环境错误", "", publish_version, publish_env, publish_admins,
                              time_now())


# 处理卡片回调
def do_publish_card(data: lark.Card) -> Any:
    # 打印卡片回调的响应体
    print(lark.JSON.marshal(data))
    publish_type = data.action.value.get("publish_type")
    publish_env = data.action.value.get("publish_env")
    publish_version = data.action.value.get("publish_version")
    publish_auditor = []
    publish_auditor.append(publish_user)
    publish_auditor.append(data.open_id)
    time_cur = time_now()

    if data.open_id in publish_admins:
        if publish_type == "publish":
            # perfregistry:5000/tsp/msbatterymonitor:35-c66e2652
            publish_process = Process(target=app_publish, args=(
                data.open_message_id, publish_type, publish_version, publish_auditor, time_cur,))
            publish_process.start()
            return publish_card("发布状态", "发布中", "", publish_version, publish_env, publish_auditor, time_cur)

        elif publish_type == "restart":
            # /tsp/msbatterymonitor
            restart_process = Process(target=app_restart, args=(
                data.open_message_id, publish_type, publish_version, publish_env, publish_auditor, time_cur,))
            restart_process.start()
            return publish_card("重启状态", "重启中", "", publish_version, publish_env, publish_auditor, time_cur)
