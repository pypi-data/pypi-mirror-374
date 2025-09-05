import torch
from typing import Union, Optional

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ModelManager:
    """
    训练器和测试器的基类，封装了模型保存和加载的功能

    - attr: model: torch.nn.Module, 模型
    - attr: device: torch.device, 设备
    - attr: device_ids: list[int], 多卡训练/推理时，设置多个GPU的ID
    ---
    - func: save_model(save_path: str) -> str, 保存模型
    - func: load_model(load_path: str) -> torch.nn.Module, 加载模型
    """

    def __init__(
        self,
        model: Union[torch.nn.Module, torch.nn.DataParallel],
        device: Union[torch.device, str] = DEVICE,
        device_ids: Optional[list[int]] = None,
    ):
        # 确保设备是torch.device对象
        self.device = torch.device(device) if isinstance(device, str) else device
        # 如果未提供device_ids，则默认为空列表
        self.device_ids = device_ids
        # 包装模型
        self.model = self._wrap_model(model)

    def _wrap_model(self, model: torch.nn.Module) -> torch.nn.Module:
        model = model.module if isinstance(model, torch.nn.DataParallel) else model
        model = model.to(self.device)

        # 如果使用cuda，则都使用DataParallel
        if self.device.type == "cuda":
            model = torch.nn.DataParallel(model, device_ids=self.device_ids)
            self.device_ids = (
                model.device_ids
            )  # 更新device_ids，如果一开始是None的，会找到所有可用的gpu

        return model

    def save_model(self, save_path: str) -> str:
        """
        保存模型
        - param: save_path: 保存路径
        - return: save_path
        """
        # 获取实际的模型（如果使用DataParallel，在这里其实就是使用cuda的）
        model = (
            self.model.module
            if isinstance(self.model, torch.nn.DataParallel)
            else self.model
        )
        # 将模型移动到CPU进行保存
        model_cpu = model.to("cpu")
        torch.save(model_cpu.state_dict(), save_path)
        # 将模型移回原始设备
        model_cpu.to(self.device)
        return save_path

    def load_model(self, load_path: str) -> torch.nn.Module:
        # 获取实际的模型（如果使用DataParallel）
        model = (
            self.model.module
            if isinstance(self.model, torch.nn.DataParallel)
            else self.model
        )
        # 从文件中加载状态字典
        state_dict = torch.load(load_path, map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict)
        # 重新包装模型
        self.model = self._wrap_model(model)

        print(f"Load model from {load_path}")
        return self.model
