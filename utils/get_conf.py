# -*- encoding:utf-8 -*-
import os
import configparser
import datetime


def get_config_file():
    project_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    conf_path = project_dir + '/conf/configure.ini'
    config = configparser.ConfigParser()
    config.read(conf_path)
    return config


def get_logger_file():
    project_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    tt = datetime.datetime.today()
    logger_path = project_dir + '/log/' + str(tt.year) + '_' + str(tt.month) + '_' + str(tt.day)
    return logger_path
