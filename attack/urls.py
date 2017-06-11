# coding: utf-8
from views import *

url_handlers = [
    (r"^/$", Attacking_Hosts_Page_Handler),
    # 攻击方视角: 攻击者发起请求数
    (r"/attack/attacking_hosts_data", Attacking_Hosts_Data_Handler),
    (r"/attack/attacking_hosts", Attacking_Hosts_Page_Handler),
    # 被攻击方视角: 被攻击nginx服务器收到请求数
    (r"/attack/under_attack_data", Under_Attack_Data_Handler),
    (r"/attack/under_attack", Under_Attack_Page_Handler),
    # 服务器性能
    (r"/attack/server_performance_data/(\d+)", Server_Performance_Data_Handler),
    (r"/attack/server_performance/(\d+)", Server_Performance_Page_Handler),
]