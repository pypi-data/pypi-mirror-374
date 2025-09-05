import optuna

from typing import Optional, List

from ..config import Config
from .params import OptType
from .params import OptParamBase

# region Optuna
class OptParamsManager:
    def __init__(self, hyperparams: Optional[List[OptParamBase]] = None):
        if hyperparams is None:
            hyperparams = []

        self.hyperparams = hyperparams

    def add_hyperparam(self, hyperparam: OptParamBase) -> bool:
        if hyperparam not in self.hyperparams:
            self.hyperparams.append(hyperparam)
            return True
        else:
            return False

    def add_to_trial(self, trial: optuna.Trial):
        for hyperparam in self.hyperparams:
            hyperparam.add_to_trial(trial)

        return trial

    def to_echart_axis(self, start_dim: int = 1) -> List[dict]:
        result = []

        for idx, hyperparam in enumerate(self.hyperparams):
            result.append(hyperparam.to_echart_axis())
            result[idx]["dim"] = idx + start_dim

        return result

    @classmethod
    def from_config(cls, config: Config|str, key: Optional[str] = "optuna"):
        if isinstance(config, str):
            config = Config(config)
        
        params = []

        if key is None:
            param_ls = config.get(default=[])
        else:
            param_ls = config.get(key, default=[])

        for param in param_ls:
            params.append(OptType[param["type"].upper()](**param["args"]))

        return cls(hyperparams=params)
    
    @classmethod
    def from_list(cls, param_ls: List[dict]):
        params = []
        for param in param_ls:
            if "type" not in param or "args" not in param:
                continue
            params.append(OptType[param["type"].upper()](**param["args"]))

        return cls(hyperparams=params)

# endregion
