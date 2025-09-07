from typing import Any, Dict, List
from .mono_attr import MonoAttr

class Mono:
    """模拟 reft.mono.Mono，用于 UI 测试和独立运行。"""
    def __init__(self, monos: List[MonoAttr], env: Dict[str, Any] = None):
        self.monos = monos  # List of MonoAttr
        self.env = env or {}

    def handle(self, *args, **kwargs):
        """Placeholder for handle method."""
        pass