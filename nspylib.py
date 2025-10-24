#-------------------------------------------------------------------------------
# Name:        NSPyLib
#
# Author:      Nikolay Sisyukin
# URL:         https://nikolay.sisyukin.ru/
#
# Created:     28.11.2024
# Copyright:   (c) Nikolay Sisyukin 2024
# Licence:     MIT License
#-------------------------------------------------------------------------------

KB = 2 ** 10  #  1KB in bytes
MB = 2 ** 20  #  1MB in bytes
GB = 2 ** 30  #  1GB in bytes
TB = 2 ** 40  #  1TB in bytes

import os, sys, json, codecs, requests, urllib3, ssl, smtplib, ipaddress, base64, zlib
import xml.etree.ElementTree as xml

from xml.etree.ElementInclude import include

from requests.auth import HTTPBasicAuth

from re import A

from datetime import datetime as dt
from time import time

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.utils import formatdate

urllib3.disable_warnings()

#-------------------------------------------------------------------------------

def nowDateTime(sp=None):
    if sp:
        sp1, sp2, sp3 = sp, sp, sp
    else:
        sp1, sp2, sp3 = '-', ' ', ':'  

    now = dt.now()
    
    year = str(now.year).rjust(4, '0')
    month = str(now.month).rjust(2, '0')
    day = str(now.day).rjust(2, '0')
    hour = str(now.hour).rjust(2, '0')
    minute = str(now.minute).rjust(2, '0')
    second = str(now.second).rjust(2, '0')
    
    now = f'{year}{sp1}{month}{sp1}{day}{sp2}{hour}{sp3}{minute}{sp3}{second}'

    return now

#-------------------------------------------------------------------------------

def sendEmail(subject, mail, recipients, sender, password, server, port, ssl_mode=False):
    date = f'{dt.now():%Y-%m-%d %H:%M:%S}'

    header_of_mail = '<html>\n<body style="font-family: Arial !important;">'
    footer_of_mail = '</body>\n</html>'
    body_of_mail = header_of_mail + mail + footer_of_mail
    
    message = MIMEMultipart('alternative')

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = '; '.join(recipients)
    message['Date'] = formatdate(localtime=True)
            
    message.attach(MIMEText(body_of_mail, 'html')) 
    
    context = ssl.create_default_context()

    if not ssl_mode:
        with smtplib.SMTP(server, port) as server:
            server.starttls(context=context)
            server.login(sender, password)
            for recipient in recipients:
                server.sendmail(sender, recipient, str(message).encode('utf-8'))
    elif ssl_mode:
        with smtplib.SMTP_SSL(server, port) as server:
            server.login(sender, password)
            for recipient in recipients:
                server.sendmail(sender, recipient, str(message).encode('utf-8'))

#-------------------------------------------------------------------------------

def sendEmailFromConfigParam(conf_filename, title, message, recipients):
    sender = readJSONfromFile(conf_filename)
    sendEmail(title, message, recipients, 
              sender['login'], sender['password'], 
              sender['server'], sender['port'], ssl_mode=sender['ssl'])

#-------------------------------------------------------------------------------

def readXMLfromFile(filename):
    # find
    # findall
    tree = xml.parse(filename)
    root = tree.getroot()
    return root

#-------------------------------------------------------------------------------

def printKeyLenJSON(data, varname=''):
    print('-' * 50)
    print(varname)
    print('-' * 50)
    for key, value in data.items():
        print(f'{key} - {len(value)}')
    print('-' * 50, '\n')

#-------------------------------------------------------------------------------

def is_valid_json(s: str) -> bool:
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False

#-------------------------------------------------------------------------------

def jsonToBase64(text):
    return base64.b64encode(json.dumps(text).encode('utf-8')).decode('utf-8')

#-------------------------------------------------------------------------------

def base64ToJson(base64_data):
    return json.loads(base64.b64decode(base64_data).decode('utf-8'))

#-------------------------------------------------------------------------------

def base64SplitToMany(base64_data, part_size):
    parts = []
    for i in range(0, len(base64_data), part_size):
        parts.append(base64_data[i:i + part_size])
    return parts

#-------------------------------------------------------------------------------

def base64JoinFromMany(base64_data_parts):
    return ''.join(base64_data_parts)
#-------------------------------------------------------------------------------

def readJSONfromFile(filename, enc='UTF-8'):
    with open(filename, 'r', encoding=enc) as f:
        return json.load(f)

#-------------------------------------------------------------------------------

def dumpJSONtoFile(filename, data, mode='w'):
    with open(filename, mode, encoding="UTF-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#-------------------------------------------------------------------------------

def dumpJSONtoScreen(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))

#-------------------------------------------------------------------------------

def readTEXTfromFile(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        return f.read()

#-------------------------------------------------------------------------------

def readLINEfromFile(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        return f.readline().split('\n')[0]
 
#-------------------------------------------------------------------------------

def readLINESfromFile(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        return f.read().splitlines()

#-------------------------------------------------------------------------------

def writeTEXTtoFile(filename, text, mode='w'):
    with open(filename, mode, encoding='UTF-8') as f:
        f.write(text)

#-------------------------------------------------------------------------------

def writeLINEtoFile(filename, new_line, mode='w'):
    with open(filename, mode, encoding='UTF-8') as f:
        f.write(new_line + '\n')

#-------------------------------------------------------------------------------

def writeLINEStoFile(filename, new_lines, mode='w', sep='\n'):
    with open(filename, mode, encoding='UTF-8') as f:
        if isinstance(new_lines, list):
            for line in new_lines:
                f.write(line + sep)
        elif isinstance(new_lines, str):
            f.write(new_lines + sep)

#-------------------------------------------------------------------------------

def writeLINEStoBeginFile(filename, new_lines):
    with open(filename, 'r', encoding='UTF-8') as f:
        old_lines = readLINESfromFile(filename)
    with open(filename, 'w', encoding='UTF-8') as f:
        for line in new_lines:
            if line not in old_lines:
                f.write(line + '\n')
        for line in old_lines:
            f.write(line + '\n')

#-------------------------------------------------------------------------------

def writeLogLINEtoFile(filename, new_line):
    log_line = f'{nowDateTime()}: {new_line}'
    writeLINEtoFile(filename, log_line, 'a')

#-------------------------------------------------------------------------------

def ipToInt(ip):
    try:
        if '/' in ip:
            ip = ip.split('/')[0]
        ip_obj = ipaddress.ip_address(ip)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            return int(ipaddress.IPv4Address(ip))
        elif isinstance(ip_obj, ipaddress.IPv6Address):
            return int(ipaddress.IPv6Address(ip))
    except:
        return 0

#-------------------------------------------------------------------------------

def sortedIPs(ip_list):
    return sorted(ip_list, key=ipToInt)

#-------------------------------------------------------------------------------

def CIDRtoIpRage(cidr):
    return str(ipaddress.IPv4Network(cidr)[0]), str(ipaddress.IPv4Network(cidr)[-1])

#-------------------------------------------------------------------------------

def ipRangeToCIDR(ip_first, ip_last):
    return [str(ipnet) for ipnet in ipaddress.summarize_address_range(ipaddress.IPv4Address(ip_first), ipaddress.IPv4Address(ip_last))]

#-------------------------------------------------------------------------------

def CIDRsubstract(cidr1, cidr2):
    return sortedIPs(list(map(str, ipaddress.ip_network(cidr1).address_exclude(ipaddress.ip_network(cidr2)))))

#-------------------------------------------------------------------------------

def sortDictByKey(data):
    result = {key: data[key] for key in sorted(data.keys())}
    return result

def sortDictByValue(data):
    result = {key: value for key, value in sorted(data.items(), key=lambda item: item[1])}
    return result

if __name__ == '__main__':
    print("This is a library module and should not be run directly.")