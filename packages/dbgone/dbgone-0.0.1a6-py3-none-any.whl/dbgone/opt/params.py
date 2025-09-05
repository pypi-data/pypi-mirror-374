import optuna

from typing import Optional, List

from pydantic import BaseModel,Field
from abc import ABC, abstractmethod
from enum import Enum

# region Models



class OptParamBase(BaseModel, ABC):
    """
    OptParamBase: 调优参数基类
    - param name: str 调优参数名称

    - property short_name: str, 缩写参数名称

    - abstract func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - abstract func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式

    - func __repr__(self) -> str, 打印该参数的字符串表示
    """

    name: str

    @property
    def short_name(self) -> str:
        """
        缩写参数名称
        """
        return self.name.split(".")[-1]

    @abstractmethod
    def add_to_trial(self, trial: optuna.Trial):
        """
        向optuna.trial中添加该参数的猜测值
        """
        pass

    @abstractmethod
    def to_echart_axis(self) -> dict:
        """
        转为echart的parallelAxis的坐标轴格式
        """
        pass

    def __repr__(self) -> str:
        return "class " + self.__class__.__name__ + " - " + str(self.model_dump())

    def __str__(self) -> str:
        return self.__repr__()
    

class OptInt(OptParamBase):
    """
    OptInt: 整数类型的调优参数
    - param name: str 调优参数名称
    - param low: int 最低值
    - param high: int 最高值
    - param step: Optional[int] 步长
    - param log: bool 是否以对数刻度, 默认为False

    - func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式
    """

    low: int = Field(..., description="最低值")
    high: int = Field(..., description="最高值")
    step: Optional[int] = Field(None, description="步长")
    log: bool = Field(False, description="是否以对数刻度")

    def add_to_trial(self, trial: optuna.Trial) -> int:
        return trial.suggest_int(
            name=self.name, low=self.low, high=self.high, step=self.step, log=self.log
        )

    def to_echart_axis(self) -> dict:
        return {"name": self.short_name, "min": self.low, "max": self.high}


class OptChoice(OptParamBase):
    """
    OptChoice: 离散选择类型的调优参数
    - param name: str 调优参数名称
    - param choices: list 可选值列表

    - func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式
    """

    choices: List[str] = Field(..., description="可选值列表")

    def add_to_trial(self, trial: optuna.Trial) -> str:
        return trial.suggest_categorical(name=self.name, choices=self.choices)

    def to_echart_axis(self) -> dict:
        return {
            "name": self.short_name,
            "data": self.choices,
            'type': 'category', 
        }


class OptUniform(OptParamBase):
    """
    OptUniform: 均匀分布的调优参数
    - param name: str 调优参数名称
    - param low: float 最低值
    - param high: float 最高值

    - func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式
    """

    low: float = Field(..., description="最低值")
    high: float = Field(..., description="最高值")

    def add_to_trial(self, trial: optuna.Trial) -> float:
        return trial.suggest_uniform(name=self.name, low=self.low, high=self.high)

    def to_echart_axis(self) -> dict:
        return {"name": self.short_name, "min": self.low, "max": self.high}


class OptLogUniform(OptUniform):
    """
    OptLogUniform: 对数均匀分布的调优参数
    - param name: str 调优参数名称
    - param low: float 最低值
    - param high: float 最高值

    - func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式
    """

    def add_to_trial(self, trial: optuna.Trial) -> float:
        return trial.suggest_loguniform(name=self.name, low=self.low, high=self.high)

    def to_echart_axis(self) -> dict:
        return {"name": self.short_name, "min": self.low, "max": self.high}


class OptDiscreteUniform(OptUniform):
    """
    OptDiscreteUniform: 离散均匀分布的调优参数
    - param name: str 调优参数名称
    - param low: float 最低值
    - param high: float 最高值
    - param q: float 步长

    - func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式
    """

    q: float = Field(..., description="步长")

    def add_to_trial(self, trial: optuna.Trial) -> float:
        return trial.suggest_discrete_uniform(
            name=self.name, low=self.low, high=self.high, q=self.q
        )

    def to_echart_axis(self) -> dict:
        return {"name": self.short_name, "min": self.low, "max": self.high}


class OptFloat(OptUniform):
    """
    OptFloat: 浮点数类型的调优参数
    - param name: str 调优参数名称
    - param low: float 最低值
    - param high: float 最高值
    - param step: Optional[float] 步长
    - param log: bool 是否以对数刻度, 默认为False

    - func add_to_trial(self, trial: optuna.Trial), 向optuna.trial中添加该参数的猜测值
    - func to_echart_axis(self) -> dict, 转为echart的parallelAxis的坐标轴格式
    """

    step: Optional[float] = Field(None, description="步长")
    log: bool = Field(False, description="是否以对数刻度")

    def add_to_trial(self, trial: optuna.Trial) -> float:
        return trial.suggest_float(
            name=self.name, low=self.low, high=self.high, step=self.step, log=self.log
        )

    def to_echart_axis(self) -> dict:
        return {"name": self.short_name, "min": self.low, "max": self.high}


class OptType(Enum):
    """
    OptType: 调优参数类型枚举
    - enum INT: OptInt, 整数类型的调优参数
    - enum CHOICE: OptChoice, 离散选择类型的调优参数
    - enum UNIFORM: OptUniform, 均匀分布的调优参数
    - enum LOGUNIFORM: OptLogUniform, 对数均匀分布的调优参数
    - enum DISCRETEUNIFORM: OptDiscreteUniform, 离散均匀分布的调优参数
    - enum FLOAT: OptFloat, 浮点数类型的调优参数

    - func __call__(self, **kwargs) -> OptParamBase, 根据枚举值生成相应的OptParamBase实例
    """

    INT = OptInt
    CHOICE = OptChoice
    UNIFORM = OptUniform
    LOGUNIFORM = OptLogUniform
    DISCRETEUNIFORM = OptDiscreteUniform
    FLOAT = OptFloat

    def __call__(self, **kwargs) -> OptParamBase:
        return self.value(**kwargs)


# endregion