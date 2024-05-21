from flask import Flask
from lark_oapi.adapter.flask import *

from im import *

app = Flask(__name__)

# 注册事件回调
event_handler = lark.EventDispatcherHandler.builder(ENCRYPT_KEY, VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()

# 注册卡片回调
card_handler = lark.CardActionHandler.builder(ENCRYPT_KEY, VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register(do_publish_card) \
    .build()


@app.route("/event", methods=["POST"])
def event():
    resp = event_handler.do(parse_req())
    return parse_resp(resp)


@app.route("/card", methods=["POST"])
def card():
    resp = card_handler.do(parse_req())
    return parse_resp(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9777)
