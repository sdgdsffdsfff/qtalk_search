#!/usr/bin/env python
# -*- encoding: utf8 -*-

import json


class RequestUtil:

    def __init__(self):
        pass

    @staticmethod
    def get_request_args(request):
        if "GET" == request.method:
            args = request.args
        else:
            if "text/plain" in request.content_type:
                args = json.loads(request.data)
            elif "application/json" in request.content_type:
                args = request.json
            else:
                args = request.form
        return args

    @staticmethod
    def get_list_args(args, field, delimiter=","):
        value = args.get(field)
        if value:
            return value.split(delimiter)
        else:
            return []

    @staticmethod
    def default_int(str_value, default_value):
        if not str_value:
            return default_value
        try:
            return int(str_value)
        except Exception as e:
            return default_value