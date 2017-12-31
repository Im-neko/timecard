#!/usr/bin/python3
#-*- coding:utf-8 -*-
import json
import urllib.parse
from multiprocessing import Process

import falcon

from src import api
from src import get_module_logger

reqlogger = get_module_logger(__name__, 'access.log')


class Test():

    def on_get(self, req, res):
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': 'alive'})

    def on_post(self, req, res):
        data = urllib.parse.parse_qs(req.stream.read().decode('utf-8'))
        try:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': data['text'][0]}
        except:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': ''} 
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': json.dumps(data)})


class Time_in():

    def on_post(self, req, res):
        data = urllib.parse.parse_qs(req.stream.read().decode('utf-8'))
        try:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': data['text'][0]}
        except:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': ''} 
        p = Process(target=api.time_in, args=(d,))
        p.start()
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': str(d['user_name'])+' start working request accept'})


class Time_out():

    def on_post(self, req, res):
        data = urllib.parse.parse_qs(req.stream.read().decode('utf-8'))
        try:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': data['text'][0]}
        except:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': ''} 
        p = Process(target=api.time_out, args=(d,))
        p.start()
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': str(d['user_name'])+' stop working request accept'})


class Rest_s():

    def on_post(self, req, res):
        data = urllib.parse.parse_qs(req.stream.read().decode('utf-8'))
        try:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': data['text'][0]}
        except:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': ''}
        p = Process(target=api.rest_s, args=(d,))
        p.start()
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': str(d['user_name'])+' stop working request accept'})


class Rest_e():

    def on_post(self, req, res):
        data = urllib.parse.parse_qs(req.stream.read().decode('utf-8'))
        try:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': data['text'][0]}
        except:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': ''}
        p = Process(target=api.rest_e, args=(d,))
        p.start()
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': str(d['user_name'])+' start working request accept'})


class Rest_mm():

    def on_post(self, req, res):
        data = urllib.parse.parse_qs(req.stream.read().decode('utf-8'))
        try:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': data['text'][0]}
        except:
             d = {'user_id': data['user_id'][0], 'user_name': data['user_name'][0], 'memo': ''}
        p = Process(target=api.rest_mm, args=(d,))
        p.start()
        reqlogger.debug('[HEADER]:%r' % req.headers +
                        '[ADDRESS]:%r' % req.remote_addr +
                        '[METHOD]:%r' % req.method +
                        '[BODY]:%r' % data)
        res.status = falcon.HTTP_200
        res.body = json.dumps({'message': str(d['user_name'])+' start working request accept'})
