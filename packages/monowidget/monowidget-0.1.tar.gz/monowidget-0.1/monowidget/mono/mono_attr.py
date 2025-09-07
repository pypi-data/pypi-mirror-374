from typing import Any, Dict, Optional, Callable
from datetime import datetime


class MonoAttr:
    """模拟 reft.mono.MonoAttr，用于 UI 测试和独立运行。只支持新的直接传参方式。"""
    
    def __init__(self, name: str, value: Any, lineno: int = 0, 
                 range=None, enum=None, color=None, tooltip=None, 
                 label=None, group=None, header=None, title=None, 
                 readonly=False, separator=None, space=None, 
                 min_datetime=None, max_datetime=None, **kwargs):
        """
        初始化MonoAttr，支持所有参数的直接传参方式
        
        Args:
            name: 属性名称
            value: 属性值，类型将自动推断
            lineno: 行号（可选，默认为0）
            range: 数值范围，格式为(start, stop, step)的元组
            enum: 枚举值列表，如['a', 'b', 'c']或[1, 2, 3]
            color: 颜色设置，可以是#RRGGBB格式的颜色字符串或(fg, bg)元组
            tooltip: 鼠标悬停提示文本
            label: 显示标签文本，如未提供则使用name
            group: 分组名称，用于在UI中分组显示
            header: 分组标题，用于创建分组头部
            title: 页面标题，用于创建页面级标题
            readonly: 是否为只读模式，布尔值
            separator: 是否添加分隔符，布尔值
            space: 是否添加空白间隔，布尔值
            **kwargs: 其他自定义属性，将自动过滤掉type参数
        
        Examples:
            >>> # 基本使用
            >>> attr = MonoAttr("width", 100, range=(0, 1000, 10))
            >>> 
            >>> # 枚举类型
            >>> attr = MonoAttr("mode", "fast", enum=["slow", "medium", "fast"])
            >>> 
            >>> # 完整配置
            >>> attr = MonoAttr("opacity", 0.8, 
            ...                range=(0.0, 1.0, 0.01),
            ...                label="透明度",
            ...                group="视觉效果",
            ...                tooltip="控制元素透明度")
            >>> 
            >>> # 函数按钮类型
            >>> def my_function():
            ...     print("Button clicked!")
            >>> attr = MonoAttr("点击按钮", my_function)
        """
        self.name = name
        self.value = value
        self.lineno = lineno
        
        # 收集所有显式参数到属性字典
        attrs = {
            'range': range,
            'enum': enum,
            'color': color,
            'tooltip': tooltip,
            'label': label,
            'group': group,
            'header': header,
            'title': title,
            'readonly': readonly,
            'separator': separator,
            'space': space,
            'min_datetime': min_datetime,
            'max_datetime': max_datetime,
        }
        
        for key, val in kwargs.items():
            attrs[key] = val
            
        # 特殊处理函数按钮类型
        # 当value是可调用对象时，自动设置为函数按钮类型
        if callable(value) and not isinstance(value, type):
            # 设置类型为'function'，这将在工厂类中映射到QMonoAttrFunctionItem
            attrs['type'] = 'function'
        
        # 过滤掉None值，保持属性字典简洁
        self._attrs = {k: v for k, v in attrs.items() if v is not None}
    
    @property
    def attrs(self) -> Dict[str, Any]:
        """获取属性字典"""
        return self._attrs
    
    @attrs.setter
    def attrs(self, value):
        """设置属性，只接受字典格式"""
        if isinstance(value, dict):
            # 移除type参数
            self._attrs = {k: v for k, v in value.items() if k.lower() != 'type'}
        else:
            # 不再支持老的字符串列表格式
            raise TypeError("MonoAttr不再支持字符串列表格式，请使用直接传参方式")
    
    def get_attr(self, key: str, default: Any = None) -> Any:
        """获取特定属性值"""
        return self._attrs.get(key, default)
    
    def set_attr(self, key: str, value: Any) -> None:
        """设置特定属性值"""
        if key.lower() != 'type':  # 不允许设置type属性
            self._attrs[key] = value
    
    def has_attr(self, key: str) -> bool:
        """检查是否存在特定属性"""
        return key in self._attrs
    
    def __repr__(self) -> str:
        return f"MonoAttr(name='{self.name}', value={self.value}, attrs={self._attrs})"
