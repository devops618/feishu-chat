import time
import requests
import json

from lark_oapi.api.im.v1 import *
from client import client
from cards import *
from config import *


# 发送卡片消息
def create_msg_req(chat_id: str, content):
    request = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
                      .receive_id(chat_id)
                      .msg_type("interactive")
                      .content(content)
                      .build()) \
        .build()

    response = client.im.v1.chat.create(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")


# 更新卡片消息
def patch_msg_req(message_id, content):
    # 构造请求对象
    request: PatchMessageRequest = PatchMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(PatchMessageRequestBody.builder()
                      .content(content)
                      .build()) \
        .build()

    # 发起请求
    response: PatchMessageResponse = client.im.v1.message.patch(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")


def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

    body = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    response = requests.request("POST", url, headers=headers, json=body)
    print(response.text)
    if response.status_code == 200:
        tenant_access_token = response.json().get("tenant_access_token")
        return tenant_access_token


def update_msg_req(message_id, receive_id, content):
    time.sleep(10)
    tenant_access_token = get_access_token()
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}"

    # 请求体
    content_new = json.dumps({
        "receive_id": receive_id,
        "content": content,
        "msg_type": "interactive"
    })

    token_headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + tenant_access_token
    }

    response = requests.request("PATCH", url, headers=token_headers, data=content_new)
    print(response.text)
