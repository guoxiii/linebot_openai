import openai

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

service_data = '''
以下資料，標題是客問題，摘要是答案：
標題：產品有做動物實驗嗎
摘要：我們全品項保養都為無動物實驗，因此對於健康與環境都是友善的
標題：素食者可以使用嗎
摘要：是的，我們全品項堅持綠色純素,讓消費者或是茹素者都可以安心使用沒有問題
標題：為什麼蓓樂膚屬於環保美妝
摘要：我們主要有3個環保作法：1、100%使用生質可分解材質包材，2、100%使用可回收環保瓶器，3、100%對生態友善用料
標題：該如何挑選出最適合自己的產品?
摘要：建議您可以私訊客服，簡單提供您目前的年齡、膚況簡述、想改善的肌膚問題等，讓客服為您推薦適合的產品
標題：孕婦、孩童可以使用嗎
摘要：部分產品含有少量的添加物，建議在購買前可以預先詢問小編，或將產品內容物列表給予醫生判定，並遵從醫生建議使用
標題：新客戶註冊怎麼使用優惠
摘要：新客戶註冊即可獲得$100優惠券，可以到註冊信箱查收優惠碼，如找不到可查看垃圾信件夾
標題：下單多久可以收到商品
摘要：郵局宅配1-3天、全家超商2-5天、萊爾富3-7天、OK超商7-14天，離島或偏遠地區則需加計5-7天，實際天數不包含例假日，並視物流情況而定
標題：如何退換貨
摘要：請至會員專區的訂單查詢選擇欲退貨訂單，點選退貨申請並填寫退貨單，由專人協助您辦理退貨/退款事宜，詳細流程請參考退換貨政策與須知
標題：該如何加入會員
摘要：您可點選網站上方的「會員登入/註冊」圖示，輸入帳號密碼即可登入，首次使用可以註冊成為會員
標題：忘記密碼怎麼辦
摘要：進入會員登入頁面後點選「忘記密碼」即可重設密碼，或直接致電客服人員協助處理
標題：常收不到訂單確認信/到貨通知信
摘要：請您再次登入信箱，檢查垃圾信件夾中是否有來自蓓樂膚的信件，並設置為非垃圾郵件，若查無信件可直接致電客服處理
標題：該如何修改個人資料及密碼
摘要：登入會員專區後,點選「會員資料」即可變更您的個人資訊及密碼，更改email後請留意新信箱是否可正常收到訂單通知
標題：如何使用優惠代碼
摘要：優惠代碼是我們不定期公布的一組代碼，可在結帳時輸入獲得折扣。建議可留意註冊信件或訂閱官方EDM獲取優惠代碼
標題：什麼是紅利點數？該如何使用？
摘要：紅利點數是我們回饋給會員的福利，每消費$100即可獲得1點，可於結帳時選擇紅利折抵訂單金額(1點可折$1)，點數於訂單成立10天後生效
標題：紅利點數的生效日期
摘要：紅利點數於訂單結案10日後生效，以蓓樂膚官網系統紀錄為準
標題：退貨時如何處理紅利點數
摘要：退貨時，該筆訂單所獲得的紅利點數將被同步扣除，已使用的點數將無法退還，如有異常請聯繫客服處理
標題：哪裡查詢紅利點數
摘要：登入會員專區,點選「紅利點數」即可查看紅利點數紀錄及異動明細
標題：如何訂購商品
摘要：可透過網路下單、免費訂購專線或實體通路購買，網路下單後約2個工作天出貨，詳細購物流程請參考官網說明
標題：訂購完想再訂購其他商品，可以再加訂嗎
摘要：是的，可以致電客服提供訂單編號，我們將為您合併訂單
標題：訂單成立後,是否可以取消
摘要：可以，請至會員專區的訂單查詢選擇欲取消的訂單並點選取消訂單，若已出貨則無法自行取消，需致電客服協助處理
標題：可以更改收件人地址/資訊嗎
摘要：可以的，建議您可以直接致電客服，提供訂單編號並更新收件人地址或資訊，客服人員會立即為您處理
標題：目前提供哪些付款方式
摘要：提供線上刷卡、ATM轉帳、超商付款及貨到付款等付款方式，線上刷卡使用SSL加密機制，請放心使用
標題：訂購完成後想更改付款方式可以嗎
摘要：很抱歉，訂單完成後我們無法更改付款方式，如需變更，建議取消原訂單並重新下單
標題：如何知道是否付款成功
摘要：請登入會員專區查看訂單狀態，若已付款成功，訂單狀態將顯示為「備貨中」
標題：可選擇的配送方式有那些
摘要：目前提供「郵局宅配到府」和「超商取貨」兩種配送方式
標題：如何了解訂單配送進度
摘要：請登入會員專區查詢訂單，若已出貨會顯示貨運單號，即可在宅配或超商系統查詢配送進度
標題：商品到貨/取貨流程
摘要：1、商品出貨後會收到email通知，2、選擇超商取貨會再收到簡訊通知取貨，3、需在7天內前往指定門市取件並付款，4、若無法親自取件可請他人代領
標題：訂單可否修改指定取貨時間
摘要：很抱歉，超商取貨服務時段是依照超商作業規範，無法個人指定取貨時間
標題：已取貨完成卻又收到取貨提醒通知
摘要：這是系統統一發送的提醒，若您已完成取貨，則可以不用理會該通知
標題：請問運費如何計算
摘要：消費滿NT$999即可免運費，未達免運門檻則酌收NT$60運費
標題：訂購後需多久可收到商品
摘要：大約為1-14天不等,並視配送方式及地區而有所不同
標題：沒在期限內取貨該怎辦
摘要：若逾期未取貨，商品將退回本公司且訂單自動取消，您將無法再次收件，未來也可能影響您使用超商取貨或貨到付款的權益
標題：未收到貨到門市通知函怎辦
摘要：請檢查一下垃圾信件夾是否有通知函，或進入會員專區查詢出貨進度，若確實未收到通知可聯繫客服協助
標題：門市說沒有我的商品怎辦
摘要：若您已收到通知函但門市表示沒有您的商品，請立即與客服人員聯繫，我們會立刻為您查詢商品下落
標題：國家/地區配送權益說明
摘要：1、商品以台幣計價，海外信用卡將產生手續費和匯率差異，2、部分地區需支付關稅，請先確認可送達，3、購買人若來自中國需提供身分證資料，4、採用中華郵政配送，運費將依重量和地區而有所不同，詳情請先聯繫客服確認
標題：退換貨政策與須知
摘要：所有商品均享有7天鑑賞期(猶豫期非試用期)，請保持商品完整包裝狀態，退貨須包含商品、發票、贈品等，詳細須知請參考官網退換貨政策
標題：如何辦理退貨/退款?
摘要：請至會員專區訂單查詢選擇欲退貨訂單，點選退貨申請並填寫退貨單，由專人為您處理後續退貨或退款事宜
標題：可以辦理換貨嗎
摘要：我司僅提供一次性退貨服務，若需換貨請先辦理退貨退款後再重新下單購買
標題：收到商品幾天內可申請退換貨
摘要：收到商品起7天內可申請退換貨，逾期則無法受理
標題：退貨須知有哪些
摘要：1、須保持商品完整包裝無拆封使用過，2、須連同發票、贈品一併寄回，3、每張訂單僅一次免費退貨機會
標題：無法接受退換貨的情況
摘要：1、已超過7天鑑賞期，2、商品經拆封或使用過，3、非因商品本身瑕疵，4、商品損毀或變質，5、贈品或發票遺失
標題：辦理退貨/退款需多久
摘要：收到退回商品後，將於7個工作天內為您處理退款事宜(不含假日)
標題：寄回商品須注意事項
摘要：寄回商品時請注意以下事項：1、保持商品及外包裝完整無拆封，2、一併附上發票及訂單明細，3、若是線上刷卡付款則無需提供銀行帳戶資訊，4、一併將贈品與組合內其他商品一併寄回
標題：有幾次免費退換貨機會
摘要：每張訂單僅提供一次免費退換貨服務
標題：退貨時贈品須一併寄回嗎
摘要：是的，辦理退貨時贈品必須一併寄回，否則將影響您的退貨權益
標題：退貨時發票須一併寄回嗎
摘要：是的，發票也是必須一併寄回的單據，若遺失發票將無法辦理退貨
標題：退貨次數的影響
摘要：若您有2次無故退換貨的紀錄，公司將保留是否接受您的訂單權利
標題：拆封過的商品可以退貨嗎
摘要：很抱歉，除商品本身瑕疵外，一經拆封使用過的商品將無法接受退貨
標題：因個人原因退貨可以嗎
摘要：非商品本身瑕疵問題，因個人原因而退貨的情況是無法接受的
標題：退貨的商品狀態須如何
摘要：退貨的商品須保持完整的包裝狀態(包括外盒、配件、內包裝等)，請勿拆封使用過，並連同贈品、發票一併寄回，否則將影響退貨權益

你只能依照上述摘要內容
如果上述摘要找不到答案，請回答：無法確認您的問題答案，上班後將由客服人員回覆。
你必須簡短的回答以下問題
'''

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
    global hist
    global service_data
    hist.append({"role": "user", "content": user_msg})
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
