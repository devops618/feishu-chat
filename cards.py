import lark_oapi as lark

# 卡片配置
card_config = {
    "wide_screen_mode": True,
    "update_multi": True
}


# 使用帮助卡片
def help_card():
    content = '''**✔ 发布微服务**
    发布#环境 镜像（注意把sit去掉），示例：
    <font color='green'>发布#perfregistry:5000/tsp/msbatterymonitor:35-c66e2652</font>
**✔ 重启微服务**
    重启#环境 微服务id，示例：
    <font color='green'>重启#perf/tsp/msbatterymonitor</font>
**✔ 查询微服务信息**
    查询#环境 微服务id，示例：
    <font color='green'>查询#perf/tsp/msbatterymonitor</font>
**✔ 查询微服务id**
    查询id#环境/模糊查询微服务id的关键字，示例：
    <font color='green'>查询id#perf/msbatt</font>
**✔ GitLab配置同步**
    git同步#环境，示例：
    <font color='green'>git同步#perf</font>'''

    card = {
        "config": card_config,
        "elements": [
            {
                "tag": "markdown",
                "content": content
            }
        ],
        "header": {
            "template": "blue",
            "title": {
                "content": "使用帮助",
                "tag": "plain_text"
            }
        }
    }

    return lark.JSON.marshal(card)


def common_card(title, content):
    card = {
        "config": card_config,
        "elements": [
            {
                "tag": "markdown",
                "content": content
            }
        ],
        "header": {
            "template": "blue",
            "title": {
                "content": title,
                "tag": "plain_text"
            }
        }
    }

    return lark.JSON.marshal(card)


# 发布消息卡片
def publish_card(title, button_name, publish_type, publish_version, publish_env, publish_auditor, publish_time):
    at_publish_auditor = ""
    for num in range(0, len(publish_auditor), 1):
        at_publish_auditor_tmp = "<at id=%s></at>" % publish_auditor[num]
        at_publish_auditor = at_publish_auditor + at_publish_auditor_tmp

    content = '''🟠 **发布环境**\n%s
**🔴 发布版本**\n%s
**🕒 发布时间**\n%s
**👤 发布审核**\n%s
''' % (publish_env, publish_version, publish_time, at_publish_auditor)

    card = {
        "config": card_config,
        "elements": [
            {
                "tag": "markdown",
                "content": content
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button_name
                        },
                        "type": "danger",
                        "value": {
                            "publish_type": publish_type,
                            "publish_env": publish_env,
                            "publish_version": publish_version
                        }
                    }
                ]
            }
        ],
        "header": {
            "template": "red",
            "title": {
                "content": title,
                "tag": "plain_text"
            }
        }
    }

    return lark.JSON.marshal(card)
