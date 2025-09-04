

import os
import sys
from typing import List
from alibabacloud_vpc20160428.client import Client as Vpc20160428Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_vpc20160428 import models as vpc_20160428_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


from ..config import CONFIG
import json 
from ..client  import CLIENT 
import questionary
from .vswitch import VSWITCH

class VPC(object):
    """
    管理和配置阿里云VPC
    """

    def __init__(self,ist:bool=False):
        self._ist_flag =ist 
        if ist==False: 
            return 
        else: 
            res=VPC.__getvpcs()
            vpcs = res.body.vpcs.vpc
            choise_list=[]
            for vpc in vpcs:
                choise_list.append(f"{vpc.vpc_id}__{vpc.cidr_block}__{vpc.vpc_name}")

            choise_res=questionary.select("请选择VPC:",choise_list).ask()
            choise_id = choise_res.split("__")[0]
            # print(choise_id)
            
            # 根据 choise_id 找到 vpcs 当中对应的 vpc 然后把这个vpc的所有字段都变成VPC实例的属性 
            selected_vpc = None
            for vpc in vpcs:
                if vpc.vpc_id == choise_id:
                    selected_vpc = vpc
                    break
            
            if selected_vpc:
                self.vpc_id = selected_vpc.vpc_id
                self.vpc_name = selected_vpc.vpc_name
                self.cidr_block = selected_vpc.cidr_block
                self.region_id = selected_vpc.region_id
                self.status = selected_vpc.status
                self.vswitchs=[]
                if selected_vpc.v_switch_ids and selected_vpc.v_switch_ids.v_switch_id:
                    for vswitch_id in selected_vpc.v_switch_ids.v_switch_id:
                        self.vswitchs.append(VSWITCH(vswitch_id, self.vpc_id))
                        pass
            
    def __getattribute__(self, name):

        _ist_flag = object.__getattribute__(self, "_ist_flag")
                
        if _ist_flag==False and name in type(self).__dict__:
            cls_attr = type(self).__dict__[name]

            if callable(cls_attr) and not isinstance(cls_attr, (staticmethod, classmethod)):
                raise AttributeError(f"'{type(self).__name__}' 在 ist=False 时不可访问实例方法 '{name}'")
        else: 
            pass 
        return object.__getattribute__(self, name)


    def vswls(self):
        for _ in self.vswitchs:
            print(_)


    def vswcreate(self):
        pass 

    def vswdel(self):
        pass

    @staticmethod
    def __getvpcs()-> vpc_20160428_models.DescribeVpcsResponse:
        """
        直接返回VPCS对象 因为可能会有不止一个地方需要使用这个对象
        """
        describe_vpcs_request = vpc_20160428_models.DescribeVpcsRequest(
            region_id=CLIENT().region 
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            CLIENT().config.endpoint = f'vpc.{CLIENT().region}.aliyuncs.com'
            res=Vpc20160428Client(CLIENT().config).describe_vpcs_with_options(describe_vpcs_request, runtime)
            # 返回的res是json格式 这里先打印成人类可读的形式
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            return res 
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
        pass 
    
    @staticmethod
    def ls() -> None:
        """
        把vpcs 以人类可读的方式列出来
        """
        # 从 res 当中获取 Vpc信息并美化打印出来 包含 VpcId VpcName CidrBlock RegionId Status VswitchIds
        res = VPC.__getvpcs()
        # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        vpcs = res.body.vpcs.vpc
        for vpc in vpcs:
            print(f"VPC ID: {vpc.vpc_id}")
            print(f"VPC 名称: {vpc.vpc_name}")
            print(f"CIDR 块: {vpc.cidr_block}")
            print(f"区域 ID: {vpc.region_id}")
            print(f"状态: {vpc.status}")
            print(f"交换机 IDs: {', '.join(vpc.v_switch_ids.v_switch_id) if vpc.v_switch_ids and vpc.v_switch_ids.v_switch_id else '无'}")
            print("-" * 50)

            
