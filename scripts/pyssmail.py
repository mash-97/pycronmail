#!/usr/bin/python

import sys
import os
import time
import datetime
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

import psutil


# convert bytes to GigaByte
def GB(bytes):
  return bytes/1024**3


# cpu cores
def get_cpu_count():
  cpu_count = psutil.cpu_count()

# average cpu usage percent
def get_average_cpu_usage(count=5):
  av_cpu_percent = sum([psutil.cpu_percent(interval=1) for i in range(count)])/count
  return av_cpu_percent


# cpu frequency
def get_cpu_freq():
  cpu_freq = psutil.cpu_freq()
  cpu_freq = {
    "current": cpu_freq.current,
    "min": cpu_freq.min,
    "max": cpu_freq.max
  }
  return cpu_freq

# disk usage for '/'
def get_disk_usage():
  disk_usage = psutil.disk_usage('/')
  disk_usage = {
    "total": GB(disk_usage.total),
    "used": GB(disk_usage.used),
    "free": GB(disk_usage.free),
    "percent": disk_usage.percent
  }
  return disk_usage


# get battery status
def get_battery_status():
  battery_status = psutil.sensors_battery()
  battery_status = {
    "percent": battery_status.percent,
    "power_plugged": battery_status.power_plugged
  }
  return battery_status

# get virtual memory stats
def get_virtual_memory_stats():
  virtual_memory = psutil.virtual_memory()
  virtual_memory = {
    "total": GB(virtual_memory.total),
    "percent": virtual_memory.percent
  }
  return virtual_memory


# get host stats
def get_host_stats():
  host = os.uname()
  host = {
    "sysname": host.sysname,
    "nodename": host.nodename,
    "kernel_version": host.release,
    "version": host.version,
    "machine": host.machine
  }
  return host

def form_system_status_body():
  start_time = time.time()

  # system status
  host = get_host_stats()
  cc = get_cpu_count()
  acu = get_average_cpu_usage()
  vms = get_virtual_memory_stats()
  du = get_disk_usage()
  cf = get_cpu_freq()
  bs = get_battery_status()

  end_time = time.time()
  elapsed_time = (end_time-start_time)

  # create plain text message
  text = f"""\
  [Host Info]
  sysname: {host['sysname']}
  nodename: {host['nodename']}
  kernel version: {host['kernel_version']}
  version: {host['version']}
  machine: {host['machine']}

  [CPU Stats]
  cpu cores: {cc}
  average cpu usage: {acu}%%
  current cpu frequency: {cf['current']} Mhz
  minimum cpu frequency: {cf['min']} Mhz
  maximum cpu frequency: {cf['max']} Mhz

  [Virtual Memory Stats]
  total: {vms['total']}GB
  usage percent: {vms['percent']}%%

  [Disk Usage]
  total: {du['total']}GB
  usage percent: {du['percent']}%%

  [Others]
  battery percent: {bs['percent']}%%
  power plugged: {bs['power_plugged']}

  (data processed in %.3fs)
  """%(elapsed_time)

  html = f"""\
  <html>
  <body>
    <b>[Host Info]</b>
    sysname: {host['sysname']}
    nodename: {host['nodename']}
    kernel version: {host['kernel_version']}
    version: {host['version']}
    machine: {host['machine']}

    <b>[CPU Stats]</b>
    cpu cores: {cc}
    average cpu usage: {acu}%%
    current cpu frequency: {cf['current']} Mhz
    minimum cpu frequency: {cf['min']} Mhz
    maximum cpu frequency: {cf['max']} Mhz

    <b>[Virtual Memory Stats]</b>
    total: {vms['total']}GB
    usage percent: {vms['percent']}%%

    <b>[Disk Usage]</b>
    total: {du['total']}GB
    usage percent: {du['percent']}%%

    <b>[Others]</b>
    battery percent: {bs['percent']}%%
    power plugged: {bs['power_plugged']}

    <b>(data processed in %.3fs)
  </body>
  </html>
  """%(elapsed_time)

  return [text, html]

def get_system_status_message(sender_email, receiver_email, text, html):
  # time
  current_datetime = datetime.datetime.today()
  __datetime__ = current_datetime.strftime("%Y/%m/%d %H:%M:%S")

  # create message mime context
  message = MIMEMultipart("alternative")
  message['subject'] = f"System Status - {__datetime__}"
  message['from'] = sender_email
  message['to'] = receiver_email

  # Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  # The email client will try to render the last part first
  # Add HTML/plain-text parts to MIMEMultipart message
  message.attach(part1)
  message.attach(part2)
  
  return message


def send_mail(sender_email, sender_password, receiver_email, message):
  # Create secure connection with server and send email
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
      server.login(sender_email, sender_password)
      server.sendmail(
          sender_email, receiver_email, message.as_string()
      )


def parse_sender_config(file_path):
  sender_email = None
  sender_password = None
  with open(file_path, "r") as fp:
    lines = fp.readlines()
    flines = []
    for line in lines:
      line = line.strip()
      if len(line) != 0:
        flines.append(line)
    sender_email = flines[0]
    sender_password = flines[1]
  return [sender_email, sender_password]

def parse_receiver_emails(file_path):
  receiver_emails = []
  with open(file_path, "r") as fp:
    lines = fp.readlines()
    for line in lines:
      line = line.strip()
      if len(line) != 0:
        receiver_emails.append(line)
  return receiver_emails


if __name__ == '__main__':
  # parse args or exit with 1
  if(len(sys.argv)!=4):
    exit(1)
  
  log_file_path = sys.argv[1]
  logging.basicConfig(filename=log_file_path, encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
  sender_config_file_path = sys.argv[2]
  receiver_emails_store_path = sys.argv[3]
  
  logging.info(f"parsed sender configs: {parse_sender_config(sender_config_file_path)}")
  logging.info(f"parsed receiver emails: {parse_receiver_emails(receiver_emails_store_path)}")
  logging.info(f"form status message: ")
  fssb = form_system_status_body()
  logging.info(f"plain text: {fssb[0]}")
  logging.info(f"html text: {fssb[1]}%%")
