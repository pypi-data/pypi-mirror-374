# -*- coding: utf-8 -*-
from monowidget._utils.core import *
from typing import Any, Dict, List, Iterable, Tuple

class IdOrderedDict(dict):
    """保持键创建顺序的有序字典
    
    继承自Python内置dict，提供所有字典方法，同时维护键的创建顺序，并支持键的替换操作
    内部使用一个列表来存储键的顺序
    """
    
    def __init__(self, data: Dict = None):
        """初始化有序字典
        
        Args:
            data: 可选的初始数据字典
        """
        # 初始化内部键顺序列表
        self._keys = []
        
        # 调用父类dict的初始化
        super().__init__()
        
        if data is not None:
            if isinstance(data, dict):
                for k, v in data.items():
                    self[k] = v
            elif isinstance(data, IdOrderedDict):
                # 复制另一个IdOrderedDict的内容和顺序
                super().update(data)
                self._keys = data._keys.copy()
            else:
                # 处理其他可迭代对象
                for k, v in data:
                    self[k] = v
    
    def __setitem__(self, key: Any, value: Any):
        """设置键值对，如果键不存在则添加到顺序列表末尾"""
        if key not in self:
            self._keys.append(key)
        super().__setitem__(key, value)
    
    def __getitem__(self, key: Any) -> Any:
        """获取键对应的值"""
        return super().__getitem__(key)
    
    def __delitem__(self, key: Any):
        """删除键值对，并从顺序列表中移除"""
        if key in self:
            super().__delitem__(key)
            self._keys.remove(key)
    
    def __contains__(self, key: Any) -> bool:
        """检查键是否存在"""
        return super().__contains__(key)
    
    def __iter__(self):
        """迭代所有键，按照创建顺序"""
        return iter(self._keys)
    
    def __len__(self) -> int:
        """返回字典的长度"""
        return super().__len__()
    
    def __repr__(self) -> str:
        """返回字典的字符串表示"""
        items = [f"{repr(k)}: {repr(v)}" for k, v in self.items()]
        return f"IdOrderedDict({{{', '.join(items)}}})"
    
    def __str__(self) -> str:
        """返回字典的字符串表示"""
        return self.__repr__()
    
    def replace(self, old_key: Any, new_key: Any) -> bool:
        """替换键名，保持原有的顺序位置
        
        Args:
            old_key: 要替换的旧键名
            new_key: 新的键名
        
        Returns:
            bool: 替换是否成功
        """
        if old_key not in self:
            return False
        
        # 如果新键与旧键相同，不需要操作
        if old_key == new_key:
            return True
        
        # 获取旧键的值
        value = self[old_key]
        
        # 获取旧键的位置
        index = self._keys.index(old_key)
        
        # 删除旧键
        del self[old_key]
        del self._keys[index]  # 确保从键列表中删除旧键
        
        # 如果新键已存在，先从字典和顺序列表中移除
        if new_key in self:
            del self[new_key]
            if new_key in self._keys:
                self._keys.remove(new_key)
        
        # 在原位置插入新键
        self._keys.insert(index, new_key)
        
        # 设置新键的值
        super().__setitem__(new_key, value)
        
        return True
    
    def keys(self) -> List:
        """返回所有键的列表，按照创建顺序"""
        return self._keys.copy()
    
    def values(self) -> List:
        """返回所有值的列表，按照键的创建顺序"""
        return [self[k] for k in self._keys]
    
    def items(self) -> List[Tuple]:
        """返回所有键值对的列表，按照键的创建顺序"""
        return [(k, self[k]) for k in self._keys]
    
    def get(self, key: Any, default: Any = None) -> Any:
        """获取键对应的值，如果键不存在则返回默认值"""
        return super().get(key, default)
    
    def setdefault(self, key: Any, default: Any = None) -> Any:
        """获取键对应的值，如果键不存在则设置默认值并返回"""
        if key not in self:
            self[key] = default
        return self[key]
    
    def update(self, other: Dict) -> None:
        """更新字典，按照other中的键值对更新当前字典
        
        对于other中的每个键值对：
        - 如果键不存在于当前字典，则添加到顺序列表末尾
        - 如果键已存在于当前字典，则更新值但保持顺序不变
        """
        if isinstance(other, IdOrderedDict):
            # 对于IdOrderedDict，保持其键的顺序
            for k, v in other.items():
                self[k] = v
        else:
            # 对于普通字典或其他可迭代对象，按照迭代顺序添加
            if isinstance(other, dict):
                items = other.items()
            else:
                items = other
            
            for k, v in items:
                self[k] = v
    
    def clear(self) -> None:
        """清空字典"""
        super().clear()
        self._keys.clear()
    
    def copy(self) -> 'IdOrderedDict':
        """创建字典的浅拷贝"""
        new_dict = IdOrderedDict()
        new_dict.update(self)
        new_dict._keys = self._keys.copy()
        return new_dict
    
    def pop(self, key: Any, default: Any = None) -> Any:
        """删除并返回指定键的值，如果键不存在则返回默认值"""
        if key in self:
            value = self[key]
            del self[key]
            return value
        elif default is not None:
            return default
        else:
            raise KeyError(key)
    
    def popitem(self) -> Tuple[Any, Any]:
        """删除并返回最后一个键值对"""
        if not self._keys:
            raise KeyError("popitem from an empty IdOrderedDict")
        
        key = self._keys[-1]
        value = self[key]
        del self[key]
        return key, value
    
    def fromkeys(cls, keys: Iterable, value: Any = None) -> 'IdOrderedDict':
        """创建一个新的IdOrderedDict，使用给定的键和默认值"""
        new_dict = cls()
        for key in keys:
            new_dict[key] = value
        return new_dict
    
    fromkeys = classmethod(fromkeys)
    
    def move_to_end(self, key: Any, last: bool = True) -> None:
        """将指定的键移动到顺序列表的开头或末尾
        
        Args:
            key: 要移动的键
            last: True表示移动到末尾，False表示移动到开头
        """
        if key not in self._dict:
            raise KeyError(key)
        
        self._keys.remove(key)
        if last:
            self._keys.append(key)
        else:
            self._keys.insert(0, key)
    
    def get_key_at_index(self, index: int) -> Any:
        """根据索引获取键
        
        Args:
            index: 键的索引位置
        
        Returns:
            Any: 键的值
        """
        if index < 0 or index >= len(self._keys):
            raise IndexError("list index out of range")
        return self._keys[index]
    
    def get_index_of_key(self, key: Any) -> int:
        """获取键的索引位置
        
        Args:
            key: 要查找的键
        
        Returns:
            int: 键的索引位置
        """
        if key not in self._keys:
            raise KeyError(key)
        return self._keys.index(key)