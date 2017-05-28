# coding: utf-8
import json
import time

import torndb
from common.init import *
from settings import *

db = torndb.Connection(db_server, db_database, db_username, db_password)

current_result = {
    "time": "",
    "output1": "",
    "output2": "",
    "accumulate": 0,
    "per_senconds": 0
}

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

class Under_Attack_Data_Handler(WiseHandler):
    def get(self):
        self.write(json.dumps(current_result))


    def post(self):
        global current_result

        # current_time = float(self.get_argument("time", None, strip=True))
        count = int(self.get_argument("count", None, strip=True))
        output1 = self.get_argument("output1", None, strip=True)
        output2 = self.get_argument("output2", None, strip=True)

        current_result["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if count <= current_result["accumulate"]:
            current_result["per_senconds"] = 0
        else:
            current_result["per_senconds"] = float(count - current_result["accumulate"])/2
        current_result["accumulate"] = count
        current_result["output1"] = output1
        current_result["output2"] = output2

class Under_Attack_Page_Handler(WiseHandler):
    def get(self):
        self.render("attack/under_attack.html")