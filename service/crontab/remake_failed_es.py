#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import time
import os
from xml.etree import ElementTree as eTree
from tools.remake_msg_es import ROBOTS
from utils.get_conf import get_logger_file, get_config_file, get_project_dir
from utils.common_sql import UserLib
from service.kafka2es.kafka2es import handle_body

project_dir = get_project_dir()
yestrday_format = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
msg_file_dir = project_dir + '/log/{}_msgidfailed.log'.format(yestrday_format)
muc_file_dir = project_dir + '/log/{}_mucidfailed.log'.format(yestrday_format)
file_list = list(filter(lambda x: os.path.exists(x), [msg_file_dir, muc_file_dir]))
interval = 500
userlib = UserLib()
try:
    for _f in file_list:
        if 'msgidfailed' in _f:
            m_type = 'chat'
        elif 'mucidfailed' in _f:
            m_type = 'muc'
        else:
            continue
        with open(_f, 'r') as f:
            ids = f.readlines()
            ids = list(map(lambda x: x.replace('\n', '').strip(), ids))
            msg_count = len(ids)
            msg_ids = []
            i = 0
            while i < msg_count:
                msg_ids.append(ids[i:i + interval])
                i = i + interval
            # 分批进行查询
            for msg_interval in msg_ids:
                time.sleep(5)
                data = userlib.get_msg_by_msg_ids(msgids=msg_interval, msgtype=m_type)
                # 对每批进行xml解析
                for msg in data:
                    _msg = msg['body']
                    root = eTree.fromstring(_msg)
                    if m_type == "groupchat":
                        _chattype = root.get('type')
                        body = root.find("body")
                        _to = root.attrib.get('to')
                        _tohost = _to.split('@')[1]
                        _from = root.attrib.get('realfrom')
                        _time = root.attrib['msec_times']  # time 1542877246165 ms 可能是int
                        _body = body.text
                        _mtype = body.attrib["msgType"]
                        _conversation = _from + '_' + _to
                        doc_type = 'muc_msg'
                    elif m_type in ["chat", "consult"]:
                        _chattype = root.attrib.get('type')
                        _from = root.attrib.get('from', '')
                        _to = root.attrib.get('to', '')
                        _time = root.attrib['msec_times']  # time 1542877246165 ms 可能是int
                        body = root.find("body")
                        _body = body.text
                        _mtype = body.attrib["msgType"]
                        _conversation = sorted([_from, _to])[0] + '_' + sorted([_from, _to])[1]
                        doc_type = 'message'
                        if m_type == "consult":
                            _qchatid = root.attrib.get('qchatid', None)
                    else:
                        continue
    
                    if '@' in _from:
                        if _from.split('@')[0] in ROBOTS:
                            continue
                    else:
                        if _from in ROBOTS:
                            continue
                    if 'sendjid' in root.attrib:
                        _realfrom = root.attrib.get('sendjid', _from)
                    elif 'realfrom' in root.attrib:
                        _realfrom = root.attrib.get('realfrom', _from)
                    else:
                        _realfrom = _from
                    if 'realto' in root.attrib:
                        _realto = root.attrib.get('realto', _to)
                    else:
                        _realto = _to
                    doc_body = {
                        'msg': _msg,
                        'body': _body,
                        'raw_body': _body,
                        'msgid': msg['msg_id'],
                        'id': msg['id'],
                        'from': _from,
                        'to': _to,
                        'conversation': _conversation,
                        'realfrom': _realfrom,
                        'realto': _realto,
                        'mtype': _mtype,
                        'time': _time,
                        'doc_type': doc_type,
                        'chat_type': _chattype
                    }
                    extendinfo = body.attrib.get("extendInfo", "")
                    if extendinfo:
                        extend_dict = {'extendinfo': extendinfo}
                        doc_body = {**doc_body, **extend_dict}
                    handle_body(doc_body)
except Exception as e:
    print(e)
finally:
    userlib.close()
    for f in file_list:
        os.remove(f)
