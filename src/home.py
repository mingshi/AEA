#!/usr/bin/env python
# -*- coding: utf-8 -*-
import markdown
import os.path
import re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import tornado.autoreload
import time
import string

import pycurl
import cStringIO
from hashlib import md5
import urllib
import urllib2
import json
import urlparse


from tornado.options import define, options
from sqlalchemy.orm import scoped_session, sessionmaker
from models import Reimbursed, Reimsub, Reimtype, Approve
from db import db_session

define("port", default=7777, help="run on the given port", type=int)
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/myadd",MyAddHandler),
            (r"/detail/([0-9]+)",MyDetailHandler),
            (r"/approve/([0-9]+)",ApproveHandler),
            (r"/login",EntryHandler),
            (r"/logout",LogoutHandler),
        ]
        settings = dict(
            blog_title="Anjuke_Expense_Applying",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
            #xsrf_cookies=True,
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
        debug=True)
        
        self.db = db_session
        tornado.web.Application.__init__(self, handlers, **settings)
        
        
class BaseHandler(tornado.web.RequestHandler):
    
    current_userinfo = {}
    cookie_userinfo = {}
    def prepare(self):
        print self.__class__.__name__
        if self.__class__.__name__ == 'EntryHandler':
            pass
        else :
            if not self.current_user:
                self.redirect("/login")
            self.cookie_userinfo = tornado.escape.json_decode(self.current_user)
            self.current_userinfo = self.get_userinfo(self.cookie_userinfo['user_code'])
    
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
    def get_userinfo(self, keyword):
        m = md5(keyword)
        m2 = md5(m.hexdigest() + 'ajkcfin')
        request = urllib2.Request("http://kq.corp.anjuke.com/api/?columns=code&keyword="+ keyword +"&auth="+ m2.hexdigest() +"&superior=1")
        resource = urllib2.urlopen(request).read()
        resource =  json.loads(resource)
        if resource:
            return resource[0]
        else:
            return
    def get_process(self, user_id, total_expense, species):
        print self.process_url + '?uid='+str(user_id)+'&app=1&cost=' + str(total_expense) +'&type='+str(species)
        request = urllib2.Request(self.process_url + '?uid='+str(user_id)+'&app=1&cost=' + str(total_expense) +'&type='+str(species))
        resource = urllib2.urlopen(request).read()
        print resource       
        
        resource =  json.loads(resource)        
        if resource:
            process = [[";"+final[0]+";",final[1]] for final in resource['business']] + \
             [[";"+";".join([final[0] for final in resource['cashier']])+";" , u"出纳票审"]] + \
             [[";"+final[0]+";",final[1]] for final in resource['financial']] + \
             [[";".join([ final[0] for final in resource['final']]), u"出纳付款"]]          
            print process
            return process
        else:
            return
        
    def authority(self, reimbursed):
        if reimbursed.status == 0:
            current_auth = self.db.query(Approve).filter_by(reim_id=reimbursed.id).filter_by(status=0).first()
            if string.find(current_auth.user_ids, ";"+str(self.current_userinfo['user_id'])+";")!=-1:
                return current_auth
    @property
    def db(self):
        return self.application.db
    
    client_id = 'ewa7t8u2sqx389z013it'
    client_secret = '9l3z3aoo3vxbq36qv9cbkdnsxqhlrr07tlby3wqu'
    auth_url = 'https://auth.corp.anjuke.com/oauth/2.0/login'
    auth_logout_url = 'https://auth.corp.anjuke.com/oauth/2.0/logout'
    
#     process_url = 'http://192.168.192.148:8899/process/process.get'
    process_url = 'http://jessiejia.dev.anjuke.com/tmp.php'

class HomeHandler(BaseHandler):
    def get(self):
#         reimbursed_ing = self.db.query(Reimbursed).filter_by(user_id=self.current_userinfo['user_id']).filter_by(status=0).all()
#         reimbursed_finish = self.db.query(Reimbursed).filter_by(user_id=self.current_userinfo['user_id']).filter_by(status=1).all()
#         reimbursed_refuse = self.db.query(Reimbursed).filter_by(user_id=self.current_userinfo['user_id']).filter_by(status=2).all()
#         
#         
#         approve_ing = self.db.query(Reimbursed).filter_by(user_ids like "%"+self.current_userinfo['user_id']+"%").filter_by(status=0).all()
#         approve_ed = self.db.query(Reimbursed).filter_by(user_ids like "%"+self.current_userinfo['user_id']+"%").filter_by(status!=0).all()
        
        
        self.render("home.html")
class MyAddHandler(BaseHandler):
    def get(self):
        reim_types = self.db.query(Reimtype).all()
        self.render("myadd.html", reim_types=reim_types)
    def post(self):
        arguments = self.request.arguments
        expenses = arguments['expense[]']
        type_ids = arguments['type_id[]']
        comments = arguments['comment[]']
        
        total_expense = 0
        for key in range(0,len(type_ids)):
            if type_ids[key] and expenses[key]:
                # validate more...0
                total_expense = total_expense + float(expenses[key])
        
        # Reimbursed
        reimbursed = Reimbursed(user_id=self.current_userinfo['user_id'], status=0,create_time=time.strftime("%Y-%m-%d", time.localtime()), total_expense=total_expense)
        self.db.add(reimbursed)
        self.db.commit()
        # Reimsub
        for key in range(0,len(type_ids)):
            if type_ids[key] and expenses[key]:
                reimsub = Reimsub(id=reimbursed.id, type_id=type_ids[key], expense=expenses[key], comment=comments[key])
                self.db.add(reimsub)
        self.db.commit()
        # Approve
        species = 1
        process = self.get_process(self.current_userinfo['user_id'], total_expense, species)
        
        approve = Approve(reim_id=reimbursed.id, user_name=process[0][1], user_ids=process[0][0], status=0, flag=0,operator=0, comment='')
        self.db.add(approve)
        self.db.commit()
        
        self.redirect("/detail/" + str(reimbursed.id))
class MyDetailHandler(BaseHandler):
    def get(self, reimbursed_id):
        reim_types = self.db.query(Reimtype).all()
        reimbursed = self.db.query(Reimbursed).filter_by(id=reimbursed_id).first()
        reimsubs = self.db.query(Reimsub).filter_by(id=reimbursed_id).all()
        dict_reim_types = {}
        for reim_type in reim_types:
            dict_reim_types[reim_type.id] = reim_type.type
        # process
        approves = self.db.query(Approve).filter_by(reim_id=reimbursed_id).all()
        species = 1
        process = self.get_process(reimbursed.user_id, reimbursed.total_expense, species)
        process = process[len(approves):]
        # userinfo
        userinfo = self.get_userinfo(self.current_userinfo['code'])
        # authority
        current_auth = self.authority(reimbursed)
        self.render("mydetail.html", userinfo=userinfo, reimbursed=reimbursed, reimsubs=reimsubs, dict_reim_types=dict_reim_types, approves=approves, process=process, current_auth=current_auth)

class ApproveHandler(BaseHandler):
    def updateApprove(self,reimbursed):
        species = 1
        process = self.get_process(reimbursed.user_id, reimbursed.total_expense, species)
        approves = self.db.query(Approve).filter_by(reim_id=reimbursed.id).all()
        process = process[len(approves):]
        if len(process)>1:
            approve = Approve(reim_id=reimbursed.id, user_name=process[0][1], user_ids=process[0][0], status=0, flag=0,operator=0, comment='')
            self.db.add(approve)
            self.db.flush()
        else:
            reimbursed.status=1
            self.db.flush()
        
    def post(self, reimbursed_id):
        reimbursed = self.db.query(Reimbursed).filter_by(id=reimbursed_id).first()
        current_auth = self.authority(reimbursed)
        if current_auth:
            arguments = self.request.arguments
            print arguments
            if 'approve' in arguments:
                current_auth.status=1
                current_auth.operator=self.current_userinfo['user_id']
                current_auth.comment=arguments['myurge'][0]
                self.db.flush()
                self.updateApprove(reimbursed)
                self.db.commit()
            elif 'refuse' in arguments:
                current_auth.status=2
                current_auth.operator=self.current_userinfo['user_id']
                current_auth.comment=arguments['myurge'][0]
                self.db.flush()
                # update reimbursed status
                reimbursed.status=2
                self.db.commit()
            else:
                # canshu cuo wu
                pass
        else:
            # mei quan xian
            pass
        
        
        self.redirect("/detail/" + str(reimbursed.id))
        
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        urllib2.Request(self.auth_logout_url)
        self.redirect("/")
                
class EntryHandler(BaseHandler):
    def get(self):
        arguments = self.request.arguments
        if 'code' in arguments:
            print arguments['code']
            access_token = self.token(arguments['code'][0])
            print access_token
            if access_token is None:
                self.redirect('/login', permanent=True)
            else:
                resource = self.resource(access_token)
                print resource
                self.set_secure_cookie("user", tornado.escape.json_encode({'user_code':resource['code'],'user_id':resource['user_id'],'chinese_name':resource['name'],'username':resource['username']}))
                self.redirect("/")
        else:
            self.authorize()
            
    def authorize(self):
        self.redirect(self.auth_url + "/authorize?client_id="+ self.client_id, permanent=True)
        
    def token(self, code):
        data = {"client_id": self.client_id,"client_secret":self.client_secret,"code":code}
        print data
        buf = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.CONNECTTIMEOUT, 60)
        c.setopt(pycurl.TIMEOUT, 300)
        c.setopt(c.URL, self.auth_url + "/token")
        c.setopt(c.POSTFIELDS,  urllib.urlencode(data))
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.perform()
        ret = buf.getvalue()
        buf.close()
        print ret
        ret = urlparse.parse_qs(ret)
        if 'access_token' in ret:
            return ret['access_token'][0]
        else:
            return
    def resource(self, access_token):
        request = urllib2.Request('https://auth.corp.anjuke.com/oauth/2.0/user')
        request.add_header('Authorization', 'bearer '+ access_token)
        resource = urllib2.urlopen(request).read()
        # what about error??
        resource =  json.loads(resource)
        if resource:
            return resource[0]
        else:
            return
class EntryModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == "__main__":
    main()
