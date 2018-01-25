#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

import requests
import pymongo

from src.config import *


def get_working_users():
    """
    現在勤務中のユーザーを取得
    """
    
