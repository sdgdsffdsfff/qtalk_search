# -*- encoding:utf-8 -*-
import base64
import hashlib
import redis
from urllib.parse import parse_qs
from utils.logger_conf import configure_logger
from utils.get_conf import get_logger_file, get_config_file

log_path = get_logger_file()
log_path = log_path + '_author.log'
author_log = configure_logger('author', log_path)

config = get_config_file()
r_host = config['redis']['host']
r_database = config['redis']['database']
r_timeout = config['redis']['timeout']
r_port = config['redis']['port']
r_password = config['redis']['password']
r_domain = config['qtalk']['domain']

redis_cli = redis.StrictRedis(host=r_host, port=r_port, db=r_database, password=r_password, decode_responses=True)

g_user = ''


def check_ckey(ckey, u):
    global g_user
    if not g_user:
        g_user = u
    if not isinstance(ckey, str):
        ckey = str(ckey)
    if len(ckey) <= 0:
        return False
    try:
        ckey_parse = base64.b64decode(ckey).decode("utf-8")
        result = parse_qs(ckey_parse)
        user = result['u'][0]
        if user != u:  # 避免ckey是从别的domain传过来的情况
            return False
        time = result['t'][0]
        if result['d'][0] == r_domain:
            user_keys = redis_cli.hkeys(user)
            for i in user_keys:
                i = str(i) + str(time)
                i = md5(i)
                i = str(i).upper()
                if i == str(result['k'][0]):
                    if g_user != u:
                        author_log.info('user = {} , ckey = {} login success!'.format(result['u'][0], ckey))
                    return True
        else:
            author_log.error("unknown domain {} get for user {}".format(result['d'][0], user))
            return False
    except Exception as e:
        author_log.error(e)
        return False


def md5(string):
    m = hashlib.md5()
    m.update(string.encode("utf8"))
    return m.hexdigest()


def md5GBK(string1):
    m = hashlib.md5(string1.encode(encoding='gb2312'))
    return m.hexdigest()

