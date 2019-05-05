#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from kafka import KafkaConsumer
# from xml.etree import ElementTree as eTree
from utils.redis_utils import redis_cli
from conf.constants import *
from conf.search_params_define import *
from conf.cache_params_define import *

log_path = get_logger_file(name='cache.log')
cache_log = configure_logger('cache', log_path)


def add_queue():
    consumer = KafkaConsumer(qtalk_chat_topic,
                             qtalk_group_topic,
                             bootstrap_servers=consumer_broker_params,
                             group_id=group_id,
                             max_partition_fetch_bytes=10 * 1024 * 1024,
                             value_deserializer=lambda m: m.decode(),
                             key_deserializer=lambda m: m.decode())
    domain = r_domain
    for message in consumer:
        if message.key not in ['chat', 'groupchat']:
            continue
        pre_value = message.value
        try:
            value = json.loads(pre_value)
            if message.key == "chat":
                from_host = value['from_host']
                to_host = value['to_host']
                if from_host != domain or to_host != domain:
                    continue
                m_from = value['m_from']
                m_to = value['m_to']
                # m_body = value.get("m_body")
                # msg = eTree.fromstring(m_body)
                # m_type = msg.get('type')
                # m_body = msg.find("body")
                # if m_type not in ["chat"]:
                #     continue
                handle_redis(key=SINGLE_KEY, field=m_from, value=m_to)
                handle_redis(key=SINGLE_TRACE_KEY, field=m_from, value=m_to)

            elif message.key == "groupchat":
                jid = value['realfrom'] if "realfrom" in value else value['sendjid']
                user_list = value['userlist']
                room_host = value['room_host'].replace('conference.', '')
                from_host = jid.split('@')[1]
                if from_host != domain or room_host != domain:
                    continue
                # msg = eTree.fromstring(value.get('packet'))
                # type = msg['type']
                # if type not in ['groupchat']:
                #     continue

                ## 此处加入domain会导致每个用户的缓存长度高达 50 * 20 , 如果遇到性能瓶颈应考虑只缓存当前域
                # 去掉domain 占用过多空间
                # m_to = value.get('muc_room_name') + '@' + value.get('room_host')
                m_to = value.get('muc_room_name')

                handle_redis(key=MUC_KEY, field=user_list, value=m_to)
                handle_redis(key=MUC_TRACE_KEY, field=user_list, value=m_to)
            else:
                continue
        except Exception as e:
            cache_log.exception('Failed message {message},\n {e}'.format(message=message, e=e))
            continue
    consumer.close()


def handle_redis(key, field, value):
    # redis存储的顺序是倒顺序的， lpush的时候需要颠倒数组
    if not redis_cli:
        raise ConnectionError("REDIS CLIENT CONN FAILED!")
    if key in (SINGLE_KEY, SINGLE_TRACE_KEY):
        if not isinstance(field, str) or not isinstance(value, str):
            raise TypeError("WRONG FIELD {field} OR VALUE {value} TYPE".format(field=field, value=value))
        for name in (field, value):
            _k = key + '_' + name
            value = value if name == field else field
            if key == SINGLE_KEY:
                contacts = redis_cli.lrange(name=_k, start=0, end=-1)
                redis_cli.delete(_k)
                if value in contacts:
                    contacts.remove(value)
                redis_cli.lpush(_k, *contacts[::-1], value)
                redis_cli.ltrim(_k, start=0, end=19)
            elif key == SINGLE_TRACE_KEY:
                redis_cli.zincrby(name=_k, amount=1, value=value)

    elif key in (MUC_KEY, MUC_TRACE_KEY):
        if not isinstance(field, list) or not isinstance(value, str):
            raise TypeError("WRONG FIELD {field} OR VALUE {value} TYPE".format(field=field, value=value))
        for user in field:
            # 命名规则如果哪一天改成允许@了 此处就会原地爆炸
            if '@' in user:
                _user = user.split('@')
                if _user[1] != r_domain:
                    return
                _u = _user[0]
            else:
                _u = user
            _k = key + '_' + _u
            if key == MUC_KEY:
                contacts = redis_cli.lrange(name=_k, start=0, end=-1)
                redis_cli.delete(_k)
                if value in contacts:
                    contacts.remove(value)
                redis_cli.lpush(_k, *contacts[::-1], value)
                redis_cli.ltrim(_k, start=0, end=19)
            elif key == MUC_TRACE_KEY:
                redis_cli.zincrby(name=_k, amount=1, value=value)
    else:
        return


if __name__ == '__main__':
    add_queue()
