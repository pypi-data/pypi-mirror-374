import os
import yaml
from copy import deepcopy
from typing import Optional

GLOBAL_CONFIG_DIR = os.getenv("DBGONE_GLOBAL_CONFIG")


def get_inner_item(dict_: dict, *keys: str, default=None):
    """获取字典中的值"""
    if not dict_:
        return default
    if not keys:
        return dict_
    if len(keys) == 1:
        return dict_.get(keys[0], default)
    return get_inner_item(dict_.get(keys[0], default), *keys[1:], default=default)

def split_string(s, split_char="."):
    """
    分隔字符串，返回列表
    例如：'a.b.1.3.c' -> [['a', 'b',], [1,3,'c']]
    """
    parts = s.split(split_char)

    idx = len(parts)
    for i, part in enumerate(parts):
        if part.isdigit():
            idx = i
            break

    result = [parts[:idx]]
    if idx < len(parts):
        result.append([int(part) if part.isdigit() else part for part in parts[idx:]])

    return result

class Config:
    """
    配置信息

    ---

    - func: reload(config_file: str = None) -> bool: 重新加载配置
    - func: get(*keys: str, default=None) -> Any: 获取配置项
    - func: save(save_path: str) -> bool: 保存配置到指定路径
    ---
    - attr: __configs: dict: 配置字典
    """

    def __init__(self, config_file: str):
        """
        初始化配置
        - param: config_file: 配置文件路径

        """
        self.__config_file = config_file
        self._load_config()

    def _load_config(self):
        """
        加载配置
        """
        with open(self.__config_file, "r", encoding="utf-8") as f:
            self.__configs: dict = yaml.load(f, Loader=yaml.FullLoader)
        return self

    def reload(self, config_file: str = None):
        """
        重新加载配置
        - param: config_file: 新的配置文件路径
        """
        if config_file:
            self.__config_file = config_file
        return self._load_config()

    def get(self, *keys: str, default=None):
        """
        获取配置项
        - param: keys: 配置项的名称
        - param: default: 默认值，一定要写关键字参数，否则会报错，default=None
        """
        return get_inner_item(deepcopy(self.__configs), *keys, default=default)
    
    def get_inner(self, keys_str: str, split_char=".", default=None):
        """
        获取内部配置项
        - param: keys_str: 配置项的名称，以"."分割
        - param: split_char: 分隔符，默认"."
        - return: 配置项的值
        """
        try:
            keys_list = split_string(keys_str, split_char=split_char)
            if len(keys_list) == 1:
                return self.get(*keys_list[0])
            elif len(keys_list) == 2:
                result = self.get(*keys_list[0])
                for k in keys_list[1]:
                    result = result[k]
                return result
        except Exception as e:
            print(f"Error in get_inner: {e}")
            return default
            
    def save(self, save_path: str):
        """
        保存配置到指定路径
        - param: save_path: 保存路径
        """
        with open(save_path, "w", encoding="utf-8") as f:
            yaml.dump(self.get(), f, allow_unicode=True, sort_keys=False)
        print(f"Config saved to {save_path}.")
        return True


class GlobalConfig(Config):
    """
    单例模式的配置信息，只能通过reload方法重新加载配置，不能直接修改__configs属性

    ---
    - func: reload(config_file: str = None) -> bool: 重新加载配置
    - func: get(*keys: str, default=None) -> Any: 获取配置项
    - func: save(save_path: str) -> bool: 保存配置到指定路径
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file: str = GLOBAL_CONFIG_DIR):
        if not hasattr(self, "initialized"):
            super().__init__(config_file)
            self.initialized = True


def update_dict(d, value, keys):
    """
    更新嵌套字典
    """
    for key in keys[:-1]:
        d = d[key]

    d[keys[-1]] = value


class AddictionalConfig(Config):
    """
    添加额外的参数信息，设置的额外参数的优先级高于config里的参数
    - 额外参数的格式：多个参数以字典形式传入，每个参数以"."分割
    - 例如：{'Train.epoch': 100} 等价于 config['Train']['epoch'] = 100
    """

    def __init__(self, config_file: str, addictions: Optional[dict]):
        """
        初始化配置
        - param: config_file: 配置文件路径
        - param: addictional_config: 额外参数字典，格式：{'Train.epoch': 100}，默认为None时等价与普通的Config类
        """
        super().__init__(config_file)
        self.__addictional_config = {}
        if isinstance(addictions, dict):
            for key, value in addictions.items():
                keys_list = split_string(key, split_char=".")
                self.__addictional_config[".".join(keys_list[0])] = {
                    "keys_list": keys_list,
                    "value": value,
                }

    def get(self, *keys: str, default=None, from_additions=True):
        """
        获取配置项，优先读取额外参数
        - param: keys: 配置项的名称
        - param: default: 默认值，一定要写关键字参数，否则会报错，default_=None
        - param: from_additions: 是否优先读取额外参数，默认True，优先读取额外参数
        """

        if not from_additions:
            return super().get(*keys, default=default)

        add_key = ".".join(keys)
        if add_key in self.__addictional_config:
            keys_list = self.__addictional_config[add_key]["keys_list"]
            add_value = self.__addictional_config[add_key]["value"]
            if len(keys_list) == 1:
                result = add_value
            elif len(keys_list) == 2:
                result = super().get(*keys, default=default)
                update_dict(d=result, value=add_value, keys=keys_list[1])
        else:
            result = super().get(*keys, default=default)
        return result
    
    def save(self, save_path, save_addictions=True):
        '''
        保存配置到指定路径
        - param: save_path: 保存路径
        - param: save_addictions: 是否保存额外参数，默认True，额外参数也会保存到配置文件中
        '''
        result = self.get()
        if save_addictions:
            for _, v in self.__addictional_config.items():
                keys_list = v["keys_list"]
                value = v["value"]
                update_dict(d=result, value=value, keys=[k for ks in keys_list for k in ks])
        with open(save_path, "w", encoding="utf-8") as f:
            yaml.dump(result, f, allow_unicode=True, sort_keys=False)
        print(f"Config saved to {save_path}.")
        return True