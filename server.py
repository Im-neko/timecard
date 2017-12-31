#!/usr/bin/python3
# -*- coding:utf-8 -*-
import falcon

from src import Commands

api = falcon.API()

api.add_route('/timecard/time_in', Commands.Time_in())
api.add_route('/timecard/time_out', Commands.Time_out())
api.add_route('/timecard/rests', Commands.Rest_s())
api.add_route('/timecard/reste', Commands.Rest_e())
api.add_route('/timecard/restmm', Commands.Rest_mm())
api.add_route('/', Commands.Test())
