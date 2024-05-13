from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
import traceback
import requests
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
# openai.api_key = os.getenv('OPENAI_API_KEY')

sys_msg = "蓓樂膚智能客服"
client = openai.OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

qa_url = "https://www.purifycare.com/files/ai_service/purify_ai_service.txt"
qa_before = "以下資料，標題是問題，摘要是答案："
qa_after = '''
請盡量簡短的回答顧客的問題：{{custom_question}}
你只能在上述的標題與摘要找答案來回答顧客問題，如果無法回答，請回覆顧客：{{qa_no_data}}
'''
qa_no_data = "抱歉，因無法確認您的問題答案，我會請客服人員盡快回覆您。"

hist = []
backtrace = 2

def get_reply(messages):
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = messages
        )

        reply = response.choices[0].message.content
    except openai.APIError as err:
        reply = f"發生錯誤\n{ err.error.message }"

    return reply

def chat(sys_msg, user_msg):
    qa = requests.get(qa_url)

    if qa.status_code == 200:
        global hist        
        hist.append({"role": "user", "content": user_msg})

        qa.encoding = "utf-8"
        qa_after_adj = qa_after.replace("{{custom_question}}", user_msg).replace({{qa_no_data}}, qa_no_data)
        service_data = f"{qa_before}\n{qa.text}\n{qa_after_adj}"
        reply = get_reply([{"role": "user", "content": service_data}] + hist + [{"role": "system", "content": sys_msg}])
        hist.append({"role": "assistant", "content": reply})
        hist = hist[-2 * backtrace:]
        return reply

"""
def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer
"""


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()

    try:
        if len(msg) == 0:
            pass
        elif event.source.type == "group" and msg[0] != '/':
            pass
        else:
            if event.source.type == "group":
                msg = msg[1:]

            if len(msg) > 0:
                GPT_answer = chat(sys_msg, msg) # GPT_response(msg)
                print(GPT_answer)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('智能客服目前無法回答您的問題，稍後將由客服人員回覆'))        

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
