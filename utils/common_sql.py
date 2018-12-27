import psycopg2

from utils.get_conf import get_config_file, get_logger_file
from utils.logger_conf import configure_logger

config = get_config_file()
pgconfig = config['postgresql']
host = pgconfig['host']
port = pgconfig['port']
user = pgconfig['user']
database = pgconfig['database']
password = pgconfig['password']
domain = config['qtalk']['domain']
conference_str = 'conference.'+domain
log_path = get_logger_file()
log_path = log_path + '_sql.log'
logger = configure_logger('sql', log_path)


class UserLib:
    def __init__(self):
        self.conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
        self.conn.autocommit = True

    def search_user(self, username, user_id, limit, offset):
        s_result = list()
        conn = self.conn
        sql = "select aa.user_id,aa.department,aa.icon,aa.user_name,aa.mood from (SELECT a.user_id, a.department, b.url AS icon, a.user_name, b.mood FROM host_users a LEFT JOIN vcard_version b ON a.user_id = b.username WHERE a.hire_flag = 1 AND LOWER(a.user_type) != 's' AND (a.user_id ILIKE '%" + username + "%' OR a.user_name ILIKE '%" + username + "%' OR a.pinyin ILIKE '%" + username + "%')) aa left join (select case when m_from = '" + user_id + "' then m_to else m_from end as contact,max(create_time) mx from msg_history where m_from = '" + user_id + "' or m_to = '" + user_id + "' group by contact) bb on aa.user_id = bb.contact order by bb.mx desc nulls last limit " + str(
            limit) + " offset " + str(offset) + " ;"
        cursor = conn.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        for row in rs:
            res = dict()
            row = ['' if x is None else x for x in row]
            res['qtalkname'] = row[0]
            res['uri'] = row[0] + '@'+domain
            res['content'] = row[1]
            res['icon'] = row[2]
            res['name'] = row[3]
            res['label'] = row[3] + '(' + row[0] + ')'
            if row[4]:
                res['label'] = res['label'] + ' - ' + row[4]
            s_result.append(res)
        cursor.close()
        return s_result

    def search_group(self, user_id, groupkey, limit, offset):
        s_result = list()
        conn = self.conn
        sql = "select a.muc_name, a.domain, b.show_name, b.muc_title, b.muc_pic from user_register_mucs as a left join muc_vcard_info as b on concat(a.muc_name, '@', a.domain) = b.muc_name where a.username = '" + user_id + "' and (b.show_name ilike '%" + groupkey + "%' or b.muc_name like '%" + groupkey + "%') limit " + str(
            limit) + " offset " + str(offset) + ";"
        cursor = conn.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        for row in rs:
            row = ['' if x is None else x for x in row]
            res = dict()
            res['uri'] = row[0] + '@' + row[1]
            res['label'] = row[2]
            res['content'] = row[3]
            res['icon'] = row[4]
            s_result.append(res)
        cursor.close()
        return s_result

    def search_group_by_single(self, user_id, key, limit, offset):
        key = key.split()
        key = list(filter(lambda x: len(x) > 2, key))
        if key:
            if user_id in key:
                if not key.remove(user_id):
                    return None
        else:
            return None
        key = list(map(lambda x: "'" + x + "'", key))
        key_count = len(key)
        key_str = ','.join(key)
        s_result = list()
        conn = self.conn
        sql = "SELECT A.muc_room_name, B.show_name, B.muc_title, B.muc_pic FROM (SELECT muc_room_name, MAX(create_time) as max FROM muc_room_history aa RIGHT JOIN (SELECT muc_name FROM user_register_mucs WHERE username = '" + user_id + "' AND registed_flag != 0 AND muc_name in (SELECT muc_name FROM user_register_mucs WHERE username IN (SELECT user_id FROM host_users WHERE hire_flag = 1 AND (user_id ~ any(array[" + key_str + "]) OR user_name ~ any(array[" + key_str + "]) OR pinyin ~ any(array[" + key_str + "]))) GROUP BY muc_name HAVING COUNT(*) = " + str(
            key_count) + ")) bb ON aa.muc_room_name = bb.muc_name GROUP BY muc_room_name ORDER BY max DESC nulls last LIMIT " + str(
            limit) + " OFFSET " + str(
            offset) + ") A JOIN muc_vcard_info B ON (a.muc_room_name || '@"+conference_str+"') = b.muc_name;"
        cursor = conn.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        for row in rs:
            row = ['' if x is None else x for x in row]
            res = dict()
            res['uri'] = row[0] + '@' + conference_str
            res['label'] = row[1]
            res['content'] = row[2]
            res['icon'] = row[3]
            s_result.append(res)
        cursor.close()
        return s_result

