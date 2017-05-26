# coding: utf-8
import json

import torndb
from common.init import *
from settings import *

db = torndb.Connection(db_server, db_database, db_username, db_password)

class Attacking_Hosts_Data_Handler(WiseHandler):
    def get(self):
        table = 'ddos_count'
        try:
            sql = "select * from %s" % table
            results = db.query(sql)
            results = {'hosts': results}
        except Exception, e:
            self.send_error(500)
            self.write(e)
        self.write(json.dumps(results))

class Attacking_Hosts_Page_Handler(WiseHandler):
    def get(self):
        self.render("attack/attacking_hosts.html")

class Under_Attack_Page_Handler(WiseHandler):
    def post(self):


class Under_Attack_Page_Handler(WiseHandler):
    def get(self):
        self.render("attack/under_attack.html")