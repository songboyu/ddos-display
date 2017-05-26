# coding: utf-8
from views import *

url_handlers = [
    (r"^/$", Attacking_Hosts_Page_Handler),
    # 攻击方视角: 正在攻击的主机列表
    (r"/attack/attacking_hosts_data", Attacking_Hosts_Data_Handler),
    (r"/attack/attacking_hosts", Attacking_Hosts_Page_Handler),
    # 被攻击方视角: 被攻击的服务器流量
    # (r"/attack/under_attack", Cloud_VMs_Libvirt_Handler),
]