# -*- encoding: utf8 -*-
__author__ = 'jingyu.he'
from flask import Flask, render_template
from service.meeting.meeting_detail import meeting_blueprint
from service.sharemsg.sharemsg import sharemsg_blueprint
from service.search.msearch import search_blueprint
from service.updatecheck.updatecheck import updatecheck_blueprint

app = Flask(__name__, template_folder='../templates', static_folder='../static', static_url_path='/py/static')

app.register_blueprint(meeting_blueprint, url_prefix='/')
app.register_blueprint(sharemsg_blueprint, url_prefix='/')
app.register_blueprint(search_blueprint, url_prefix='/')
# app.register_blueprint(updatecheck_blueprint, url_prefix='/')


@app.route('/healthcheck.html', methods=['GET'])
def healthcheck():
    return render_template('healthcheck.html')
