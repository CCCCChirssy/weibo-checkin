import os
import json
import random
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ========== 配置开始 ==========
# 从环境变量读取微博 Cookie（SUB 字段）
cookies = {
    "SUB": os.getenv("WEIBO_COOKIE")
}

# 要签到的超话 ID
super_topic_active_ids = [
    "10080800f1d9cd468629907643285acb16e9cc",  # Weibo第五人格战队
    "100808b8ca70cde6c7ff54bcec884aee9d5480",  # 第五瓜格
    "1008087978bfc1c2820f11b9b79e531a45136a",  # alf
    "100808133d563be98d9459a7913559febf81f6",  # 弄简超话
    "100808d6ba113cf2e00a6572986696326c0623",  # 邱鼎杰超话
    "100808a387ee7fb8d5dea2854bc76a6de87f5c",  # AKA超话
    "1008084d36d00e9f5006d9322a036f5d7ba6a3",  # 黄星超话
    "1008083432a95e8ad1b69c92119c71c41b88cd",  # 星有千千杰
    "1008084ae963ad8bf87770e6068ea45002438c",  # 梦鹿超话
    "100808f9b6bf9b331198f80a35b65f6f00d1ed",  # 爱丽超话
    "1008087357bb2df2b2dcb8d973307abaeeb39b",  # 桃晚安超话
    "1008087637dcb6a0120cd2b6f510a6641aa767",  # 凉哈皮超话
    "100808b4bf8a5c0b20e51311890056b32cee0c",  # 约瑟夫超话
    "10080872a86d733a10c3385b19121e0a8d3b73",  # 佣兵超话
    "100808dcaa877c980824229dbadc31cb933166",  # 隐士超话
    "10080864872fd0a303a8cfcfa3caf03eba7ebb",  # REJECT超话
    "10080802fa0e806651ebb67a3355432cdca4e1",  # 捏捏超话
    "1008080ace918458b3513a1a4961b51a8b9e50",  # 空调超话
    "1008083d659ffdc204023af75d08396610c5ab",  # 狼队超话
    "100808148df2ceb9ae32c3a89a9995e826cff1",  # 年锦超话
    "1008087b462fedd7abdb4dfc1ac9d294e41404",  # 白露超话
    "1008083f32014bbfea2ca789394bc63cc2bfef",  # 487超话
    "1008086019f3ccd867f052c1c103d79fe907fb",  # 宠爱超话
    "100808e4bb7c196d2989fe2b94ce4054e94148",  # 配配超话
    "1008082c0d3b7895976fb42022380cc1bd9223",  # 回忆超话
    "1008086b9483eae5fd1ba02ec4412378a83cf3",  # 幻贺超话
    "1008087ef93524a3a132a44420286b0fc5cecb",  # 过客超话
    "10080817c87af74adac8187d197f89c2fdbe10",  # 姚驰超话
    "100808677f12455f7885572c521c7af0c00620",  # 元泰超话
    "100808b4fe836edf12db5c1b372b54fda70578",  # MRC超话
    "1008084e40c046f3fc8a3f9d7deb2bca3659e4",  # YMY超话
    "1008083bd107fe1f830f2cea9b5d9a64ead83e",  # 黄羿超话
    "10080897afaada1c56c2b42646f13ec4c2c29e",  # 官鸿超话
    "1008085a8e56b29a9b9fd47a743e9ab23868b3",  # 夏之光超话
    "100808e0dedfe2081535fdf7087ca1deb71e49",  # 黄俊捷超话
    "1008084d5636cd202a55b815d93af3e509be4d",  # 澜久超话
    "100808773a77fe72cec9bcd6ef5da70f39d13a",  # 坠子超话
    
]

# 邮件配置，从环境变量读取
mail_config = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender": os.getenv("MAIL_SENDER"),     # 发件人邮箱
    "receiver": os.getenv("MAIL_RECEIVER"), # 收件人邮箱
    "auth_code": os.getenv("MAIL_AUTH_CODE")# QQ 邮箱授权码
}
# ========== 配置结束 ==========

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
]

headers = {
    "User-Agent": random.choice(user_agents),
    "Referer": "https://weibo.com/"
}

log_messages = []

def random_wait(min_wait=3, max_wait=8):
    """随机等待，防止触发风控"""
    wait_time = random.randint(min_wait, max_wait)
    time.sleep(wait_time)

def send_email(subject, body):
    """发送邮件通知"""
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(mail_config["sender"])
    message['To'] = Header(mail_config["receiver"])
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp = smtplib.SMTP_SSL(mail_config["smtp_server"], mail_config["smtp_port"])
        smtp.login(mail_config["sender"], mail_config["auth_code"])
        smtp.sendmail(mail_config["sender"], [mail_config["receiver"]], message.as_string())
        smtp.quit()
        print("📧 邮件已发送")
    except Exception as e:
        print("发送邮件失败:", e)

def check_in(cookies, active_id):
    """签到单个超话"""
    headers["User-Agent"] = random.choice(user_agents)
    session = requests.Session()
    session.cookies.update(cookies)

    url = f"https://weibo.com/p/{active_id}/super_index"
    session.get(url, headers=headers)
    random_wait()

    checkin_url = f"https://weibo.com/p/aj/general/button?id={active_id}&api=http://i.huati.weibo.com/aj/super/checkin"
    checkin_response = session.get(checkin_url, headers=headers)

    try:
        result = json.loads(checkin_response.text)
        if "msg" in result:
            msg = f"✅ 超话 [{active_id}] 签到结果：{result['msg']}"
        else:
            msg = f"⚠️ 超话 [{active_id}] 返回未知内容：{result}"
    except Exception as e:
        msg = f"❌ 超话 [{active_id}] 签到失败，错误：{e}"

    print(msg)
    log_messages.append(msg)

if __name__ == "__main__":
    print("⏰ 开始签到...")

    random.shuffle(super_topic_active_ids)
    for active_id in super_topic_active_ids:
        check_in(cookies, active_id)
        random_wait()

    # 拼接邮件内容
    mail_subject = "微博超话签到通知"
    mail_body = "\n".join(log_messages)
    send_email(mail_subject, mail_body)
