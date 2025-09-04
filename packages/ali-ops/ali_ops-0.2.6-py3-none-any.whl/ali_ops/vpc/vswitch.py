import os
import sys
import json
from typing import List

from alibabacloud_vpc20160428.client import Client as Vpc20160428Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_vpc20160428 import models as vpc_20160428_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from ..client import CLIENT


class VSWITCH(object):
    def __init__(self,vswitch_id,vpc_id):
        self.id = vswitch_id
        self.vpc_id = vpc_id 
        pass

    @staticmethod
    def _getvsw(vswitch_id):
        describe_vswitch_attributes_request = vpc_20160428_models.DescribeVSwitchAttributesRequest(
            region_id=CLIENT().region ,
            v_switch_id=vswitch_id
        )
        runtime = util_models.RuntimeOptions()
        try:
            CLIENT().config.endpoint = f'vpc.{CLIENT().region}.aliyuncs.com'
            res=Vpc20160428Client(CLIENT().config).describe_vswitch_attributes_with_options(describe_vswitch_attributes_request, runtime)

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


    def __str__(self):
        res=VSWITCH._getvsw(self.id)
        # 要求返回  VSwitchId  VSwitchName  VpcId  ZoneId CidrBlock 
        # 要求输出一行内容 
        return f"VSwitchId: {res.body.v_switch_id}, VSwitchName: {res.body.v_switch_name}, VpcId: {res.body.vpc_id}, ZoneId: {res.body.zone_id}, CidrBlock: {res.body.cidr_block}"

