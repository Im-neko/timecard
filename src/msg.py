#!/usr/bin/env python
#-*- coding:utf-8 -*-
import json

import requests

from src.config import *

def sendmsg(name, text):
    msg = name + ': ' + str(text)
    requests.post(SLACK_URL, data = json.dumps({
        'text': msg,
        'username': 'MFcloud',
    }))

def senderr(name, text):
    msg = name + ': ' + str(text)
    requests.post(ERROR_URL, data = json.dumps({
        'text': msg,
        'username': 'MFcloud',
    }))

if __name__ == '__main__':
    sendmsg('test', 'test dayo-\nすっごーい！！')
