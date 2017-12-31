#!/usr/bin/python3
# -*- coding:utf-8 -*-
import os, signal
import traceback
from datetime import datetime as datetime
from datetime import timedelta as timedelta

import pymongo

from src.config import *
from src import msg
from src import get_module_logger

"""
各種パラメータ
時間は基本的にdatetime型で管理

mongo://
/user::collection
@userdata::dict - @timecardを含むデータ
    @timecards::dict - usercardのObjectId。
        @key::str - timecardYYYY/mm
        @value::ObjectId - hash
    @slack_id::str - slackのユーザーID
    @work_expire::date - working expire date
    @working_flag::int - 勤務中:0 休憩中:1 勤務外:2

/:timecardYYYYMM::collection - 月別に新たに生成
@usercard::dict - ユーザー別に作成
    @slack_id::str - slackのユーザーid
    @userId::ObjectId - ユーザー情報登録時のハッシュ(mongoに追加される時に作成されるハッシュ)
    @card::dict - work$(work_date)を入れておく辞書
    @key:work$(work_date)
    @value::dict
        @work$(work_date)::dict - work_dateは日付::str(勤務開始日)
            @key1:@working_time::list - 一つのブロック(開始から終了)で一つの要素
                (ex) working_time:[[datetime.datetime(hoge), datetime.datetime(huge)]]
            @key2:@additional_rest::list - 追加で休憩時間を(休憩開始時間~休憩終了時間)で一つの要素
                (ex) additional_rest:[[datetime.datetime(hoge), datetime.datetime(huge)]]
            @key3:memo::str - 作業内容などのメモ(どんどん追加していく感じ)


dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
MONGO_NAME = os.environ.get('MONGO_NAME')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGO_DB = os.environ.get('MONGO_DB')
"""

apilogger = get_module_logger(__name__, 'api.log')

timecard = 'timecard'+(datetime.now()).strftime('%Y%m')
work_date = str(datetime.now().day)


def getuserData(data, DB):
    """ 
    ユーザー情報の取得・作成(新しい月や新規登録) 
    @slack_id - slackのユーザーid
    @user_data - timecard含めた諸々のデータ
    """
    # set params
    slack_id = data['user_id']

    user_data = DB.user.find_one({'slack_id': slack_id})
    try:
        if user_data:
            apilogger.info('%r' % user_data)
            return True, user_data
        else:
            DB.user.insert({'slack_id': slack_id, 'timecards': {}, 'working_flag': 2})
            user_data = DB.user.find_one({'slack_id': slack_id})
            apilogger.info('%r' % user_data)
            return True, user_data
    except:
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        return False, 'Failed to generate account'


def makeusercard(slack_id, userId, DB):
    """usercardの追加. 基本月始めに追加"""
    try:
        timecards = DB.user.find_one({'_id': userId})['timecards']
        co = DB[timecard]
        usercard_id = co.insert_one({'slack_id': slack_id,
                                     'userId': userId,
                                     'work' + work_date:{'working_time': [],
                                                         'additional_rest': [],
                                                         'memo': ''}}).inserted_id
        timecards[timecard] = usercard_id
        DB.user.update_one({'_id':{'$eq': userId}}, {'$set': {'timecards': timecards}})
        usercard = co.find_one({'userId': {'$eq': userId}})
        apilogger.info('%r' % usercard)
        return usercard
    except:
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        return False


def push_start_period(data, start_time, DB):
    """
    開始打刻
    """
    try:
        memo = data['memo']
        slack_id = data['user_id']
        flag, user_data = getuserData(data, DB)
        print([start_time])
        if flag:
            userId = user_data['_id']
            co = DB[timecard]
            usercard = co.find_one({'userId': userId})
            if not usercard:
                # usercardがなかった場合
                usercard = makeusercard(slack_id, userId, DB)

            if 'work'+work_date in co.find_one({'userId': userId}):
                working_time = usercard['work' + work_date]['working_time']
                working_time.append([start_time])
            else:
                working_time = [[start_time]]
            co.update_one({'userId': {'$eq': userId}},
                          {'$set':
                               {'work' + work_date:
                                    {'working_time': working_time,
                                     'additional_rest': [],
                                     'memo': '' + memo + '\n'}}})
        apilogger.info('%r' % user_data)
        return user_data
    except:
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        return False


def push_end_period(data, end_time, DB):
    """ 
    終了打刻
    """
    try:
        flag, user_data = getuserData(data, DB)
        if flag:
            userId = user_data['_id']
            co = DB[timecard]
            usercard = co.find_one({'userId': userId})
            if usercard:
                additional_rest = usercard['work'+work_date]['additional_rest']
                memo = usercard['work'+work_date]['memo'] + data['memo']
                print(user_data['work_expire'])
                if datetime.now() < user_data['work_expire']:
                    # 日を跨いでいない場合
                    working_time = usercard['work'+work_date]['working_time']
                    print(working_time)
                    working_time[-1].append(end_time)
                    co.update_one({'userId': {'$eq': userId}},
                                  {'$set':
                                       {'work' + work_date:
                                            {'working_time': working_time,
                                             'additional_rest': additional_rest,
                                              'memo': memo + '\n'}}})
                else:
                    # 日を跨いでいた場合前日の23:59:59で一旦終了扱いに
                    last_day_2359 = datetime.now() - timedelta(hours=datetime.now().hour,
                                                               minutes=datetime.now().minute,
                                                               seconds=datetime.now().second+1)
                    working_time = usercard['work'+str(int(work_date)-1)]['working_time']
                    working_time[-1].append(last_day_2359)
                    co.update_one({'userId': {'$eq': userId}},
                                  {'$set':
                                       {'work' + str(int(work_date)-1):
                                            {'working_time': working_time,
                                             'additional_rest': additional_rest,
                                             'memo': user_data['memo']}}})
                    # 00:00:00から開始扱いに
                    today_00 = datetime.now() - timedelta(hours=datetime.now().hour,
                                                               minutes=datetime.now().minute,
                                                               seconds=datetime.now().second)
                    # 00:00:00に開始打刻
                    push_start_period(userId, today_00, DB)
                    # 現在時刻で終了打刻
                    new_usercard = co.find_one({'userId': {'$eq': userId}})
                    working_time = new_usercard['work'+work_date]['working_time']
                    working_time[-1].append(end_time)
                    co.update_one({'userId': {'$eq': userId}},
                                  {'$set':
                                       {'work' + work_date:
                                            {'working_time': working_time,
                                             'additional_rest': additional_rest,
                                             'memo': memo + '\n'}}})
        apilogger.info('%r' % user_data)
        return user_data
    except:
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        return False


def push_rest_period(data, add_rest, DB):
    """追加の休憩を後から入れる"""
    try:
        memo = data['memo']
        slack_id = data['user_id']
        flag, user_data = getuserData(data, DB)
        if flag:
            userId = user_data['_id']
            co = DB[timecard]
            usercard = co.find_one({'userId': userId})
            if not usercard:
                # usercardがなかった場合
                usercard = makeusercard(slack_id, userId, DB)

            working_time = usercard['work' + work_date]['working_time']
            additional_rest = usercard['work' + work_date]['additional_rest'].append(add_rest)
            DB.timecard.update_one({'userId': {'$eq': userId}},
                                   {'$set':
                                        {'work' + work_date:
                                             {'working_time': working_time,
                                              'additional_rest': additional_rest,
                                              'memo': '' + memo + '\n'}}})
        apilogger.info('%r' % user_data)
        return user_data
    except:
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        return False


def time_in(data):
    """勤務開始"""
    try:
        pid = os.getpid()
        now_time = datetime.now()
        memo = data['memo']
        client = pymongo.MongoClient(MONGO_NAME, int(MONGO_PORT))
        DB = client[MONGO_DB]
        user_data = DB.user.find_one({'slack_id': data['user_id']})
        if user_data:
            working_flag = user_data['working_flag']
            if working_flag in [0, 1]:
                if working_flag == 0:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在勤務中です。\n 出勤前に退勤してください*')
                else:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在休憩中です。\n 業務再開するか、一度休憩終了して退勤してください*')
                os.kill(pid, signal.SIGKILL)
            else:
                res = push_start_period(data, now_time, DB)
        else:
            res = push_start_period(data, now_time, DB)
        if res:
            work_expire = datetime.now() + timedelta(days=1)
            DB.user.update_one({'_id': {'$eq': res['_id']}}, {'$set':{'work_expire': work_expire, 'working_flag': 0}})
            msg.sendmsg('', '*' + str(data['user_name']) + '*: *'+ memo + '*')
        else:
            msg.sendmsg('', '*1001:想定外のエラーが発生しました。管理しゃに問い合わせてください。*')
        apilogger.info('%r' % user_data)
        os.kill(pid, signal.SIGKILL)
    except:
        msg.sendmsg('', '*1002:想定外のエラーが発生しました。管理者に問い合わせてください*')
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        os.kill(pid, signal.SIGKILL)


def time_out(data):
    """退勤"""
    try:
        client = pymongo.MongoClient(MONGO_NAME, int(MONGO_PORT))
        DB = client[MONGO_DB]
        pid = os.getpid()
        now_time = datetime.now()
        memo = data['memo']
        user_data = DB.user.find_one({'slack_id': data['user_id']})
        if user_data:
            working_flag = user_data['working_flag']
            if working_flag in [1, 2]:
                if working_flag == 1:
                     msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在休憩中です。\n このまま退勤する場合は一旦業務再開してから退勤してください。*')
                else:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在勤務外時間です。\n 仕事を始めてから退勤してください*')
                os.kill(pid, signal.SIGKILL)
            else:
                res = push_end_period(data, now_time, DB)
        else:
            res = push_end_period(data, now_time, DB)
        if res:
            DB.user.update_one({'_id': {'$eq': res['_id']}}, {'$set':{'work_expire': '', 'working_flag': 2}})
            msg.sendmsg('', '*' + str(data['user_name']) + '*: *' + memo + '*')
        else:
            msg.sendmsg('', '*1003:想定外のエラーが発生しました。管理者に問い合わせてください*')
    except:
        msg.sendmsg('', '*1004:想定外のエラーが発生しました。管理者に問い合わせてください*')
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
    os.kill(pid, signal.SIGKILL)


def rest_s(data):
    """
    休憩開始
    """
    try:
        client = pymongo.MongoClient(MONGO_NAME, int(MONGO_PORT))
        DB = client[MONGO_DB]
        pid = os.getpid()
        now_time = datetime.now()
        memo = data['memo']
        user_data =  DB.user.find_one({'slack_id': data['user_id']})
        if user_data:
            working_flag = user_data['working_flag']
            if working_flag in [1,2]:
                if working_flag == 1:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在休憩中です。\n 2重に休憩はできません。*')
                else:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在勤務外時間です。\n 勤務を開始してから休憩してください。*')
                os.kill(pid, signal.SIGKILL)
            else:
                res = push_end_period(data, now_time, DB)
        else:
            res = push_end_period(data, now_time, DB)
        if res:
            DB.user.update_one({'_id': {'$eq': res['_id']}}, {'$set':{'working_flag': 1}})
            msg.sendmsg('', '*' + str(data['user_name']) + '*: *' + memo + '*')
        else:
            msg.sendmsg('', '*1005:想定外のエラーが発生しました。管理者に問い合わせてください*')
        os.kill(pid, signal.SIGKILL)
    except:
        msg.sendmsg('', '*1006:想定外のエラーが発生しました。管理者に問い合わせてください*')
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        os.kill(pid, signal.SIGKILL)


def rest_e(data):
    """
    休憩終了
    """
    try:
        client = pymongo.MongoClient(MONGO_NAME, int(MONGO_PORT))
        DB = client[MONGO_DB]
        pid = os.getpid()
        now_time = datetime.now()
        memo = data['memo']
        user_data =  DB.user.find_one({'slack_id': data['user_id']})
        if user_data:
            working_flag = user_data['working_flag']
            if working_flag in [0,2]:
                if working_flag == 0:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在勤務中です。\n 休憩してから休憩終了してください*')
                else:
                    msg.sendmsg('', '*' + str(data['user_name']) + '*: *現在勤務外時間中です。\n 勤務開始してから休憩終了してください*')
                os.kill(pid, signal.SIGKILL)
            else:
                res = push_start_period(data, now_time, DB)
        else:
            res = push_start_period(data, now_time, DB)
        if res:
            DB.user.update_one({'_id': {'$eq': res['_id']}}, {'$set':{'working_flag': 0}})
            msg.sendmsg('', '*' + str(data['user_name']) + '*: *' + memo + '*')
        else:
            msg.sendmsg('', '*1007:想定外のエラーが発生しました。管理者に連絡してください。*')
        os.kill(pid, signal.SIGKILL)
    except:
        msg.sendmsg('', '*1008:想定外のエラーが発生しました。管理者に連絡してください。*')
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        os.kill(pid, signal.SIGKILL)


def rest_mm(data):
    """
    休憩時間の追加
    """
    try:
        client = pymongo.MongoClient(MONGO_NAME, int(MONGO_PORT))
        DB = client[MONGO_DB]
        pid = os.getpid()
        now_time = datetime.now()
        memo = data['memo']
        res = push_rest_period(data, now_time, DB)
        if res:
            msg.sendmsg('', '*' + str(data['user_name']) + '*: *'+ memo + '*')
        else:
            msg.sendmsg('', '*1009:想定外のエラーが発生しました。管理者:に問い合わせてください。*')
        os.kill(pid, signal.SIGKILL)
    except:
        msg.sendmsg('', '*1010:想定外のエラーが発生しました。管理者に問い合わせてください*')
        trace = traceback.format_exc()
        apilogger.error('[TRACE]:%r' % trace)
        os.kill(pid, signal.SIGKILL)

