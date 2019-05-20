# -*- coding: utf-8 -*-

import sys
import smtplib
import time
import collect_data
import collect_autofix
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler
from myutil import *
from tendo import singleton


def send_mail(blocks, shares):
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
    boby = "股票资金流数据自动更新完成, 详细结果见附件.\r\n" \
            "已尝试自动修复如下数据:\r\n" \
            + "\tblocks:{}\r\n\tshares:{}\r\n".format(blocks, shares) \
            + "手动修复使用如下指令:\r\n" \
            + "\tpython collect_data.py {} {}\r\n".format(blocks, shares)
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


def alarm_clock():
    print("alarm clock: 周一到周五 北京时间 16:00")
    scheduler = BlockingScheduler()
    scheduler.add_job(collect_data_process, 'cron', day_of_week='mon-fri',
                      hour=16, minute=1, timezone='Asia/Shanghai')
    scheduler.start()


def collect_data_process():
    print("start collect_data_silence")
    try:
        cd = collect_data.collect_data()
        if (cd.update_check()):
            cd.get_all_indexs()
            cd.get_all_blocks()
            cd.get_all_shares()
            cd.update_finished()
            blocks, shares = collect_autofix.check_report()
            collect_autofix.fix_missed_data(blocks, shares)
            send_mail(blocks, shares)
    except Exception as e:
        print(e)
    print("end collect_data_silence")


if __name__ == '__main__':
    me = singleton.SingleInstance()
    collect_data_process()
    if len(sys.argv) == 2:
        if sys.argv[1] == "alarm_clock":
            alarm_clock()
