#!/usr/bin/python3
#-*- coding:utf-8 -*-
import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname('__file__'), '.env')
load_dotenv(dotenv_path)

MONGO_NAME = os.environ.get('MONGO_NAME')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_DB')
AES_KEY = os.environ.get('AES_KEY')
SLACK_URL = os.environ.get('SLACK_URL')
ERROR_URL = os.environ.get('ERROR_URL')
