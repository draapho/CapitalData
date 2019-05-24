# -*- coding: utf-8 -*-

import sys
import smtplib
import time
import pytz
import collect_data
import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler
from myutil import *
from tendo import singleton


def send_mail(missed):
    # 定义相关数据,请更换自己的真实数据
    smtpserver = 'smtp.gmail.com'
    sender = 'kim.yu.job@gmail.com'
    # receiver可设置多个，使用“,”分隔
    receiver = 'draapho@gmail.com'
    username = 'kim.yu.job@gmail.com'
    password = 'Y7bqQ4ahpjGF265S'

    msg = MIMEMultipart()
    # boby = """
    # <p>股票资金流和价格数据自动更新完成, 详细结果请查看附件</p>
    # """
    # mail_body = MIMEText(boby, _subtype='html', _charset='utf-8')
    boby = "股票数据自动更新完成, 详细结果见附件.\r\n" \
            "以下数据更新失败:\r\n" \
            + "\tget_all_infos_missed:{}\r\n".format(missed['missed_info']) \
            + "\tget_all_funds_missed:{}\r\n".format(missed['missed_fund']) \
            + "手动修复使用如下指令:\r\n" \
            + "\tpython collect_data.py {} {}\r\n".format(missed['missed_info'], missed['missed_fund'])

    mail_body = MIMEText(boby, _subtype='plain', _charset='utf-8')
    msg['Subject'] = Header("股票数据更新", 'utf-8')
    msg['From'] = sender
    receivers = receiver
    toclause = receivers.split(',')
    msg['To'] = ",".join(toclause)
    # print(msg['To'])
    msg.attach(mail_body)

    # 添加report附件
    att = MIMEText(open(get_report_file(), "rb").read(), "base64", "utf-8")
    att["Content-Type"] = "application/octet-stream"
    times = time.strftime("%m_%d_%H_%M", time.localtime(time.time()))
    filename_report = get_report_name()
    att["Content-Disposition"] = 'attachment; filename= %s ' % filename_report
    msg.attach(att)

    # 登陆并发送邮件
    try:
        smtp = smtplib.SMTP(smtpserver)
        # 打开调试模式
        # smtp.set_debuglevel(1)
        smtp.connect(smtpserver, 587)
        smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(sender, toclause, msg.as_string())
    except Exception as e:
        print("邮件发送失败: {}".format(e))
    else:
        print("邮件发送成功")
    finally:
        smtp.quit()

def collect_silence(repeat=None):
    finished = False
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(tz)
    week = now.strftime('%a')
    print("===> collect_silence START:{} <===".format(now))
    try:
        cd = collect_data.collect_data()
        check = cd.update_check()
        if (check == "PASS"):
            cd.get_all_infos()
            if ((week == 'Fri' and now.hour >= 15) or week == 'Sat' or week == 'Sun'):
                cd.get_all_funds()
            cd.update_finished()
            send_mail(cd.get_missed_codes())
            finished = True
    except Exception as e:
        print(e)
    print("===> collect_silence END:{} <===".format(datetime.datetime.now(tz)))

    if (repeat=="repeat"):
        scheduler = BlockingScheduler()
        if finished or (check == "UPDATED"):    # 更新成功
            if (now.hour >= 15):
                tomorrow = now+datetime.timedelta(days=1)
                next_run_time = tomorrow.replace(hour=16, minute=1, second=1)
            else:
                next_run_time = now.replace(hour=16, minute=1, second=1)
        elif (check == "DENY"):     # 股票数据变动中, 当天重试
            next_run_time = now.replace(hour=16, minute=1, second=1)
        else:                       # 更新失败, 1小时后重试.
            next_run_time = now+datetime.timedelta(hours=1)
        scheduler.add_job(func=collect_silence, args=('repeat',), next_run_time=next_run_time, timezone='Asia/Shanghai')
        print("collect_silence 将再次运行于: {}".format(next_run_time))
        scheduler.start()


if __name__ == '__main__':
    me = singleton.SingleInstance()
    if len(sys.argv) == 2:
        collect_silence(repeat=sys.argv[1])
    else:
        collect_silence()
