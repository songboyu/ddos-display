# coding: utf-8
import json
import time
import re

import torndb
import requests
from common.init import *
from settings import *

db = torndb.Connection(db_server, db_database, db_username, db_password)

current_result = {
    "time": "",
    "output1": "",
    "output2": "",
    "accumulate": 0,
    "amount": 0,
    "per_senconds": 0
}

last_count = 0
statistics_count = 0

result1 = {} # 网关性能
result2 = {} # 被攻击服务器性能

class Attacking_Hosts_Data_Handler(WiseHandler):
    def get(self):
        table = 'ddos_count'
        try:
            sql = "select src_ip, sum(count) AS count, sum(count_s) AS count_s, dest_ip from %s GROUP BY src_ip, dest_ip" % table
            results = db.query(sql)
            count_amount = 0
            count_s_amount = 0
            for result in results:
                count = int(result["count"])
                count_s = int(result["count_s"])

                count_amount += count
                count_s_amount += count_s
                result["count"] = count
                result["count_s"] = count_s
            # print results
            results = {
                'hosts': results,
                'count_amount': count_amount,
                'count_s_amount': count_s_amount,
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            }
        except Exception, e:
            self.write(e)
            self.send_error(500)
        self.write(json.dumps(results))

class Attacking_Hosts_Page_Handler(WiseHandler):
    def get(self):
        self.render("attack/attacking_hosts.html")

# 被攻击nginx服务器收到请求数数据
class Under_Attack_Data_Handler(WiseHandler):
    def get(self):
        global statistics_count, last_count

        statistics_count += 1

        current_result["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        r = requests.get("http://101.101.101.104/nginx_status")
        current_count = int(re.findall(r"\n \d+ \d+ (\d+)", r.text)[0]) - statistics_count
        if current_count <= last_count or last_count == 0:
            current_result["per_senconds"] = 0
        else:
            current_result["per_senconds"] = float(current_count - last_count)/2

        current_result["amount"] = last_count = current_count

        current_result["accumulate"] += current_result["per_senconds"] * 2
        self.write(json.dumps(current_result))


    def post(self):
        global current_result

        # current_time = float(self.get_argument("time", None, strip=True))
        # count = int(self.get_argument("count", None, strip=True))
        output1 = self.get_argument("output1", None, strip=True)
        output2 = self.get_argument("output2", None, strip=True)
        #
        # current_result["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # if count <= current_result["accumulate"]:
        #     current_result["per_senconds"] = 0
        # else:
        #     current_result["per_senconds"] = float(count - current_result["accumulate"])/2
        # current_result["accumulate"] = count
        current_result["output1"] = output1
        current_result["output2"] = output2

class Under_Attack_Page_Handler(WiseHandler):
    def get(self):
        self.render("attack/under_attack.html")

# 服务器性能数据
class Server_Performance_Data_Handler(WiseHandler):
    def get(self, num):
        global result1, result2
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if num == "1":
            result1['time'] = current_time
            self.write(json.dumps(result1))
        elif num == "2":
            result2['time'] = current_time
            self.write(json.dumps(result2))
        else:
            self.send_error(500)

    def post(self, num):
        global result1, result2
        if num == "1":
            result1 = json.loads(self.request.body)
        elif num == "2":
            result2 = json.loads(self.request.body)
        else:
            self.send_error(500)

class Server_Performance_Page_Handler(WiseHandler):
    def get(self, num):
        if num == "1":
            self.render("attack/server_performance.html", num=num, title="网关服务器性能")
        elif num == "2":
            self.render("attack/server_performance.html", num=num, title="被攻击服务器性能")
        else:
            self.send_error(500)

