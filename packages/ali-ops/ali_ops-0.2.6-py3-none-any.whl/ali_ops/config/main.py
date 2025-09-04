
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import input_dialog, yes_no_dialog
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.formatted_text import HTML
import json
import platform
import os

# 阿里云区域选择列表
REGION_CHOICES = [
    ("cn-shenzhen", "cn-shenzhen"),       ("cn-hangzhou", "cn-hangzhou"),
    ("cn-beijing", "cn-beijing"),         ("cn-shanghai", "cn-shanghai"),
    ("cn-qingdao", "cn-qingdao"),         ("cn-zhangjiakou", "cn-zhangjiakou"),
    ("cn-huhehaote", "cn-huhehaote"),     ("cn-wulanchabu", "cn-wulanchabu"),
    ("cn-chengdu", "cn-chengdu"),         ("cn-heyuan", "cn-heyuan"),
    ("cn-guangzhou", "cn-guangzhou"),     ("cn-fuzhou", "cn-fuzhou"),
    ("cn-wuhan-lr", "cn-wuhan-lr"),       ("cn-nanjing", "cn-nanjing"),
    ("ap-southeast-1", "ap-southeast-1"), ("ap-southeast-2", "ap-southeast-2"),
    ("ap-southeast-3", "ap-southeast-3"), ("ap-southeast-5", "ap-southeast-5"),
    ("ap-northeast-1", "ap-northeast-1"), ("ap-south-1", "ap-south-1"),
    ("us-east-1", "us-east-1"),           ("us-west-1", "us-west-1"),
    ("eu-west-1", "eu-west-1"),           ("eu-central-1", "eu-central-1")
]


class CONFIG(object):
    """生成 处理 本项目的配置文件"""
    
    # __linux_config_path = os.path.expanduser("~/.aliyun/config.json")
    # __windows_config_path = os.path.expanduser("~\\.aliyun\\config.json")
    __linux_config_path = os.path.expanduser("~/.aliops/config.json")
    __windows_config_path = os.path.expanduser("~\\.aliops\\config.json")

    def __init__(self):
        system = platform.system()
        if system == "Windows":
            self.__config_path__ = CONFIG.__windows_config_path
        elif system == "Linux":
            self.__config_path__ = CONFIG.__linux_config_path
        elif system == "Darwin":
            self.__config_path__ = CONFIG.__linux_config_path
        else:
            self.__config_path__ = CONFIG.__linux_config_path
    
    def list(self) -> None:
        """列出所有的配置"""
        print(f"Configuration file path: {self.__config_path__}")
        try:
            with open(self.__config_path__, 'r') as f:
                config = json.load(f)
                print(json.dumps(config, indent=4))
        except FileNotFoundError:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
        

    
    def region(self,set=False):
        """
        如果 set=False 调用 self.curprof 获取当前正在使用的配置文件, 然后获取返回值的 region_id 字段 
        如果 set=True 则 首先通过 questionary.select 让用户选择区域 得到region_id 然后使用 self.curprof 函数重新设置当前配置文件的 region_id 
        """
        if not set:
            # 获取当前配置并返回region_id
            current_config = self.curprof()
            if current_config:
                return current_config.get("region_id")
            else:
                return None
        else:
            # 让用户选择新的区域
            new_region_id = questionary.select(
                "请选择区域:",
                choices=[
                    "cn-shenzhen",
                    "cn-hangzhou",
                    "cn-beijing",
                    "cn-shanghai", 
                    "cn-qingdao",
                    "cn-zhangjiakou",
                    "cn-huhehaote",
                    "cn-wulanchabu",
                    "cn-chengdu",
                    "cn-heyuan",
                    "cn-guangzhou",
                    "cn-fuzhou",
                    "cn-wuhan-lr",
                    "cn-nanjing",
                    "ap-southeast-1",
                    "ap-southeast-2",
                    "ap-southeast-3",
                    "ap-southeast-5",
                    "ap-northeast-1",
                    "ap-south-1",
                    "us-east-1",
                    "us-west-1",
                    "eu-west-1",
                    "eu-central-1"
                ]
            ).ask()

            # 使用curprof函数更新当前配置的region_id
            if new_region_id:
                self.curprof(region_id=new_region_id)
                print(f"区域已更新为: {new_region_id}")
            else:
                print("操作已取消")

    

    
    def regen(self):
        """
        根据用户的输入 生成 config.json 当中的 prifiles 字段 
        更具 profiles.name 判断是否重名 如果重名 则 询问用户是否覆盖 
        如果不重名 把 得到的 profile 插入到 config.json 中的 profiles 字段中去 
        此时询问用户是否 需要立即应用当前配置 如果用户回答Y config.json 中的 current 字段的值更改为当前 profile的name 
        """
        # 获取用户输入的配置信息
        profile_name = questionary.text("请输入配置文件的名字:").ask()
        access_key_id = questionary.text("请输入 access_key_id:").ask()
        access_key_secret = questionary.text("请输入 access_key_secret:").ask()
        region_id = questionary.select(
                            "请选择区域:",
                            choices=[
                                "cn-shenzhen",
                                "cn-hangzhou",
                                "cn-beijing",
                                "cn-shanghai", 
                                "cn-qingdao",
                                "cn-zhangjiakou",
                                "cn-huhehaote",
                                "cn-wulanchabu",
                                "cn-chengdu",
                                "cn-heyuan",
                                "cn-guangzhou",
                                "cn-fuzhou",
                                "cn-wuhan-lr",
                                "cn-nanjing",
                                "ap-southeast-1",
                                "ap-southeast-2",
                                "ap-southeast-3",
                                "ap-southeast-5",
                                "ap-northeast-1",
                                "ap-south-1",
                                "us-east-1",
                                "us-west-1",
                                "eu-west-1",
                                "eu-central-1"
                            ]
                ).ask()
        
        new_profile = {
            "name": profile_name,
            "mode": "AK",
            "access_key_id": access_key_id,
            "access_key_secret": access_key_secret,
            "region_id": region_id,
			"output_format": "json",
			"language": "en",
			"site": "china"
            }
        
        # 读取现有配置文件
        config = {}
        try:
            with open(self.__config_path__, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，创建新的配置结构
            config = {"profiles": [], "current": ""}
        
        # 确保profiles字段存在
        if "profiles" not in config:
            config["profiles"] = []
        
        # 检查是否存在同名配置
        existing_profile_index = -1
        for i, profile in enumerate(config["profiles"]):
            if profile.get("name") == profile_name:
                existing_profile_index = i
                break
        
        # 如果存在同名配置，询问用户是否覆盖
        if existing_profile_index != -1:
            overwrite = questionary.confirm(f"配置文件 '{profile_name}' 已存在，是否覆盖？").ask()
            if overwrite:
                config["profiles"][existing_profile_index] = new_profile
                print(f"配置文件 '{profile_name}' 已覆盖")
            else:
                print("操作已取消")
                return
        else:
            # 如果不重名，添加新配置
            config["profiles"].append(new_profile)
            print(f"配置文件 '{profile_name}' 已添加")
        
        # 询问用户是否立即应用当前配置
        apply_now = questionary.confirm("是否立即应用当前配置？").ask()
        if apply_now:
            config["current"] = profile_name
            print(f"当前配置已切换到 '{profile_name}'")
        
        # 确保配置文件目录存在
        os.makedirs(os.path.dirname(self.__config_path__), exist_ok=True)
        
        # 保存配置文件
        with open(self.__config_path__, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"配置文件已保存到: {self.__config_path__}")

    def curprof(self,**kwargs):
        """
        根据 self.__config_path__ 中的路径设置 查找并读取 config.json 配置文件 
        找到配置文件后 读取 其中的 current 字段 
            如果用户没有传入关键字参数 根据 current 字段的值 读取相应的配置 并且返回一个字典
            如果用户传入了关键字参数  同样需要 先根据 current 字段 获取相应的 配置 
            然后 需要根据用户传入的关键字参数 修改读取到的当前配置中的对应字段 然后重新把修改好的配置写入到 self.__config_path__
        
        """
        try:
            with open(self.__config_path__, 'r') as f:
                config = json.load(f)
            
            # 获取当前配置名称
            current_profile_name = config.get("current", "")
            if not current_profile_name:
                print("当前没有设置活跃的配置文件")
                return None
            
            # 在profiles中查找对应的配置
            profiles = config.get("profiles", [])
            current_profile = None
            current_profile_index = -1
            for i, profile in enumerate(profiles):
                if profile.get("name") == current_profile_name:
                    current_profile = profile.copy()
                    current_profile_index = i
                    break
            
            if current_profile is None:
                print(f"未找到名为 '{current_profile_name}' 的配置文件")
                return None
            
            # 如果没有传入关键字参数，直接返回当前配置
            if not kwargs:
                return current_profile
            
            # 如果传入了关键字参数，修改配置并保存
            for key, value in kwargs.items():
                if key in current_profile:
                    current_profile[key] = value
                    config["profiles"][current_profile_index][key] = value
                else:
                    print(f"警告: 配置项 '{key}' 不存在于当前配置中")
            
            # 将修改后的配置写回文件
            with open(self.__config_path__, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"配置文件已更新: {self.__config_path__}")
            return current_profile
            
        except FileNotFoundError:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
            return None
        except json.JSONDecodeError:
            print("配置文件格式错误")
            return None










if  __name__ == "__main__":
    config = CONFIG()
    result = config.curprof()
    if result:
        print("当前配置:")
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        print("未能获取当前配置")
