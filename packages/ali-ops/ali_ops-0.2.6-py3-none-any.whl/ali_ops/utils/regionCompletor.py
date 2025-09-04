
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit import prompt

class RegionAutoSelector:
    """Region 自动选择器类，用于传给 FuzzyCompleter 类做参数"""
    
    def __init__(self):
        self.region_choices = [
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
    
    def get_completions(self, document, complete_event):
        """返回匹配的 region 选项"""
        text = document.text_before_cursor
        for region_value, region_display in self.region_choices:
            if text.lower() in region_value.lower():
                yield Completion(region_value, start_position=-len(text))
    
    def get_all_regions(self):
        """获取所有可用的 region"""
        return [region[0] for region in self.region_choices]
    
    def is_valid_region(self, region):
        """检查给定的 region 是否有效"""
        return region in self.get_all_regions()


fuzzy_custom = FuzzyCompleter(RegionAutoSelector())
result = prompt('输入命令: ', completer=fuzzy_custom)
      