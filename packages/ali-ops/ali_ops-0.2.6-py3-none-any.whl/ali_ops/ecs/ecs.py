

import os
import sys
from typing import List
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import json
from ..config import CONFIG 
from ..client import CLIENT

class ECS(object): 
    """
    阿里云ECS服务
    """
    
    def __init__(self):
        credential = CredentialClient()
        config = open_api_models.Config(
            credential=credential
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Ecs
        current_config = CONFIG().curprof()
        if current_config is None:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
            self.region = None
            self.__client = None
            return
        
        self.region = current_config["region_id"] 
        config.endpoint = f'ecs.{self.region}.aliyuncs.com'
        self.__client = Ecs20140526Client(config)
        pass
    

    
        
    
    def crpp(self):
        """
        创建按量付费实例 或者竞价实例 
        """
        if self.__client is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return
        
        private_dns_name_options = ecs_20140526_models.RunInstancesRequestPrivateDnsNameOptions(
            hostname_type='IpBased',
            enable_instance_id_dns_arecord=True,
            enable_instance_id_dns_aaaarecord=True,
            enable_ip_dns_arecord=True,
            enable_ip_dns_ptr_record=True
        )
        image_options = ecs_20140526_models.RunInstancesRequestImageOptions(
            login_as_non_root=True
        )
        system_disk = ecs_20140526_models.RunInstancesRequestSystemDisk(
            category='cloud_essd',
            size='30'
        )
        run_instances_request = ecs_20140526_models.RunInstancesRequest(
            instance_charge_type='PostPaid',  # 按量付费和竞价实例相同的 
            region_id=self.region,
            v_switch_id='vsw-wz9y0k7lke0e5obyafder',
            private_ip_address='10.0.3.2',
            instance_type='ecs.c2.large',
            spot_strategy='SpotAsPriceGo', # 最优方式就是系统自动出价 
            spot_interruption_behavior='Stop',
            image_id='debian_12_9_x64_20G_alibase_20250314.vhd',
            system_disk=system_disk,
            internet_charge_type='PayByTraffic',
            internet_max_bandwidth_out=100,
            security_group_ids=[
                'sg-wz93hfiperquzquh7k92'
            ],
            password='ggmm12LPP!',
            image_options=image_options,
            instance_name='test',
            private_dns_name_options=private_dns_name_options
            
        )
        runtime = util_models.RuntimeOptions()
        try:
            CLIENT().config.endpoint = f'ecs.{CLIENT().region}.aliyuncs.com'
            res=Ecs20140526Client(CLIENT().config).run_instances_with_options(run_instances_request, runtime)
            print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        except Exception as error:
            print(error.message)
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


    # @staticmethod
    # def del():
    #     pass 


    @staticmethod
    def __getecs():
        if CLIENT().config is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return

        describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(
            region_id=CLIENT().region
        )
        runtime = util_models.RuntimeOptions()
        CLIENT().config.endpoint = f'ecs.{CLIENT().region}.aliyuncs.com'
        res=Ecs20140526Client(CLIENT().config).describe_instances_with_options(describe_instances_request, runtime)
        # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        return res 



    @staticmethod
    def ls() -> None:
        """
        列出当前region下的所有ECS实例
        """
        try:
            res=ECS.__getecs()
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))

            # 找出 res.body.Instances.Instance 当中的所有 instance 
            # 然后 针对每个 instance 列出他们的  
            #   InstanceId PublicIpAddress InstanceName InstanceType InternetChargeType 
            #   RegionId PrimaryIpAddress ImageId  SecurityGroupIds VSwitchId  VpcId
            instances = res.body.instances.instance
            for instance in instances:
                print(f"InstanceId: {instance.instance_id}")
                print(f"PublicIpAddress: {instance.public_ip_address}")
                print(f"InstanceName: {instance.instance_name}")
                print(f"InstanceType: {instance.instance_type}")
                print(f"InternetChargeType: {instance.internet_charge_type}")
                print(f"RegionId: {instance.region_id}")
                
                # Get primary IP address from network interfaces
                primary_ip = ""
                if instance.network_interfaces and instance.network_interfaces.network_interface:
                    primary_ip = instance.network_interfaces.network_interface[0].primary_ip_address
                print(f"PrimaryIpAddress: {primary_ip}")
                
                print(f"ImageId: {instance.image_id}")
                print(f"SecurityGroupIds: {instance.security_group_ids}")
                
                # Get VSwitch and VPC from VPC attributes
                vswitch_id = ""
                vpc_id = ""
                if instance.vpc_attributes:
                    vswitch_id = instance.vpc_attributes.v_switch_id
                    vpc_id = instance.vpc_attributes.vpc_id
                print(f"VSwitchId: {vswitch_id}")
                print(f"VpcId: {vpc_id}")
                print("-" * 50)


        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(f"Error occurred: {str(error)}")
            # 如果是阿里云SDK的异常，尝试获取更多信息
            if hasattr(error, 'data') and error.data:
                print(f"Recommend: {error.data.get('Recommend', 'No recommendation available')}")
            UtilClient.assert_as_string(str(error))

