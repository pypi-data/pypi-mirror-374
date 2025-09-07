from typing import Tuple, List, Dict, Any
from PyQt6.QtGui import QColor
import sys
import os
from typing import Any, Dict, Tuple
from datetime import datetime
from PyQt6.QtCore import QDateTime

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monowidget._utils import *

class MonoaRuntime:
    BG_ALPHA = 15
    BG_COLOR = "#FFFF00"
    FG_ALPHA = 200
    FG_COLOR = None
    DEFAULTS = {
        "type": None, "range": None, "enum": None,
        "color": None,
        "tooltip": None, "label": None, "group": None,
        "header": None, "title": None, "readonly": False,
        "separator": None, "space": None
    }
    INSPECTOR_KEYS = ('group', 'header', 'title', 'separator', 'space')

    def __init__(self):
        self.monoa_env = {
            'Type': self.Type, 'Range': self.Range, 'Enum': self.Enum,
            'Color': self.Color, 'Tooltip': self.Tooltip, 'Label': self.Label,
            'Group': self.Group, 'Header': self.Header, 'Title': self.Title,
            'Readonly': self.Readonly, 'Separator': self.Separator, 'Space': self.Space,
            'Separate': self.Separator, 'Spacer': self.Space
        }
        self.cmonoa = None
        self.monoa_env.update(self._lower_keyword_expand(self.monoa_env))
        self.monoa_env.update(self._upper_keyword_expand(self.monoa_env))

    @staticmethod
    def _lower_keyword_expand(_d) -> dict:
        return {k.lower(): v for k, v in _d.items()}

    @staticmethod
    def _upper_keyword_expand(_d) -> dict:
        return {k.upper(): v for k, v in _d.items()}

    @staticmethod
    def _remove_builtins(_d) -> dict:
        return {k: v for k, v in _d.items() if not k.startswith('__')}

    def Type(self, x):
        if isinstance(x, str):
            x = x.lower()
            if x == 'int':
                return {"type": int}
            elif x == 'float':
                return {"type": float}
            elif x == 'str':
                return {"type": str}
            elif x == 'bool':
                return {"type": bool}
            elif x == 'complex':
                return {"type": complex}
            elif x == 'datetime':
                return {"type": datetime}
            elif x == 'function':
                # 添加对function类型的支持
                return {"type": 'function'}
            else:
                raise MonoaRuntimeEvalError(self.cmonoa, f"Type '{x}' is not supported.")
        elif x in (int, float, str, bool, complex, datetime):
            return {"type": x}
        raise MonoaRuntimeEvalError(self.cmonoa, f"Type '{x}' is not supported.")

    def Range(self, x, y=None, s=1):
        rangex = range if abs(int(x) - x) < 1e-4 and abs(int(s) - s) < 1e-4 and ((y is None) or abs(int(y) - y) < 1e-4) else rangef
        if y is None:
            _range = rangex(0, x, s)
        else:
            if y <= x: raise MonoaRuntimeEvalError(self.cmonoa, f"End of range must be greater than start. but got range({x}, {y})")
            _range = rangex(x, y, s)
        if s <= 0: raise MonoaRuntimeEvalError(self.cmonoa, f"Step of range must be greater than 0. but got step({s})")
        return {"range": _range}

    def Enum(self, *args):
        if not args: raise MonoaRuntimeEvalError(self.cmonoa, f"Enum must have at least one argument.")
        return {"enum": list(args)}

    def Color(self, fg=None, bg=None):
        def _parse_color(c, alpha):
            if c is None: return None
            c = c.strip()
            if not c.startswith('#'): raise MonoaRuntimeUnexpectedColor(self.cmonoa, f"Color must be in #RRGGBB format. but got {c}")
            qc = QColor(c)
            qc.setAlpha(alpha)
            return qc

        fg = _parse_color(fg or self.FG_COLOR, self.FG_ALPHA)
        bg = _parse_color(bg or self.BG_COLOR, self.BG_ALPHA)
        return {"color": (fg, bg)}

    def Tooltip(self, x):
        return {"tooltip": x}

    def Label(self, x):
        return {"label": x}

    def Group(self, x="", fg=None):
        if not isinstance(x, str): raise MonoaRuntimeEvalError(self.cmonoa, f"Group name must be str.")
        fg = QColor(fg).setAlpha(self.FG_ALPHA) if fg and fg.startswith('#') else None
        return {"group": (x, fg)}

    def Header(self, x, fg=None):
        if not isinstance(x, str): raise MonoaRuntimeEvalError(self.cmonoa, f"Header name must be str.")
        fg = QColor(fg).setAlpha(self.FG_ALPHA) if fg and fg.startswith('#') else None
        return {"header": (x, fg)}

    def Title(self, x, fg=None):
        v = self.Header(x, fg)['header']
        return {"title": v}

    def Readonly(self):
        return {"readonly": True}

    def Separator(self):
        return {"separator": True}

    def Space(self, x=20):
        if not isinstance(x, int): raise MonoaRuntimeEvalError(self.cmonoa, f"Space height must be int.")
        return {"space": x}

    def _check_range_with_type(self, _range, _type):
        if _range is None: return True
        if _type in (int, float, complex): return True
        raise MonoaRuntimeEvalError(self.cmonoa, f"Type '{_type}' is not supported for Range.")

    def _check_enum_with_type(self, _enum, _type, _value):
        if _enum is None: return True
        if _type == bool: raise MonoaRuntimeEvalError(self.cmonoa, f"Type '{_type}' is not supported for Enum.")
        if _type == str and _value not in _enum: _enum.insert(0, _value)
        if _type == complex and _value not in _enum: _enum.insert(0, _value)
        for e in _enum:
            if not isinstance(e, _type):
                raise MonoaRuntimeDismatchedEnumType(self.cmonoa, f"Type of Enum must be {_type}. but got Enum={_enum}")
        return True

    def __call__(self, monoa, monoe: Dict[str, Any], **kwargs) -> Tuple[dict, list]:
        """
        处理属性，支持直接函数传参和新的MonoAttr结构
        
        Args:
            monoa: 属性对象 (MonoAttr)
            monoe: 环境变量字典
            **kwargs: 直接传参的属性（优先级高于monoa.attrs），但不包括type
        """
        lst, res, self.cmonoa = [], {}, monoa
        
        # 1. 优先处理直接传参的属性（过滤掉type）
        direct_attrs = {k: v for k, v in kwargs.items() if k.lower() != 'type'}
        
        # 2. 处理MonoAttr中的属性（新的结构，过滤掉type）
        mono_attrs = getattr(monoa, '_attrs', getattr(monoa, 'attrs', {}))
        if isinstance(mono_attrs, dict):
            # 新的结构：直接是字典（过滤掉type）
            for key, value in mono_attrs.items():
                if key.lower() != 'type' and key not in direct_attrs:  # 直接传参优先级更高
                    direct_attrs[key] = value
        else:
            # 旧的结构：字符串列表（向后兼容）
            if hasattr(monoa, '__iter__') and hasattr(monoa, 'iterall'):
                try:
                    # 处理旧的字符串格式
                    monoa.iterall(lambda attr: attr.strip() if attr.strip().endswith(')') else attr.strip() + '()')
                    
                    env = monoe.copy()
                    for expression in monoa:
                        try:
                            _ = eval(expression, self.monoa_env, env)
                        except Exception as e:
                            raise MonoaRuntimeEvalError(self.cmonoa, f"Error evaluating expression: {expression} - {e}")
                        if not isinstance(_, dict):
                            raise MonoaRuntimeEvalError(self.cmonoa, f"Expression '{expression}' must return a dict.")
                        k = list(_)[0]
                        if k in self.INSPECTOR_KEYS:
                            lst.append((k, _[k]))
                        else:
                            # 合并结果，直接传参优先级更高
                            if k not in direct_attrs:
                                res.update(_)
                except (TypeError, AttributeError):
                    # 如果无法迭代，跳过旧的字符串处理
                    pass
        
        # 3. 处理所有属性（包括新的直接传参和旧的字符串解析结果）
        for key, value in direct_attrs.items():
            key_lower = key.lower()
            
            # 移除type处理，改为自动判断
            if key_lower == 'range':
                if isinstance(value, tuple):
                    if len(value) == 2:
                        x, y = value
                        s = 1
                    elif len(value) == 3:
                        x, y, s = value
                    else:
                        raise MonoaRuntimeEvalError(self.cmonoa, f"Range tuple must have 2 or 3 elements")
                else:
                    x, y, s = value, None, 1
                
                rangex = range if abs(int(x) - x) < 1e-4 and abs(int(s) - s) < 1e-4 and ((y is None) or abs(int(y) - y) < 1e-4) else rangef
                if y is None:
                    _range = rangex(0, x, s)
                else:
                    if y <= x: 
                        raise MonoaRuntimeEvalError(self.cmonoa, f"End of range must be greater than start. but got range({x}, {y})")
                    _range = rangex(x, y, s)
                if s <= 0: 
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Step of range must be greater than 0. but got step({s})")
                res['range'] = _range
            
            elif key_lower == 'enum':
                if not value: 
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Enum must have at least one argument.")
                if isinstance(value, (list, tuple)):
                    res['enum'] = list(value)
                else:
                    res['enum'] = [value]
            
            elif key_lower == 'color':
                def _parse_color(c, alpha):
                    if c is None: return None
                    c = str(c).strip()
                    if not c.startswith('#'): 
                        raise MonoaRuntimeUnexpectedColor(self.cmonoa, f"Color must be in #RRGGBB format. but got {c}")
                    qc = QColor(c)
                    qc.setAlpha(alpha)
                    return qc

                if isinstance(value, tuple) and len(value) == 2:
                    fg, bg = value
                elif isinstance(value, str):
                    fg, bg = value, None
                else:
                    fg, bg = None, None
                
                fg = _parse_color(fg or self.FG_COLOR, self.FG_ALPHA)
                bg = _parse_color(bg or self.BG_COLOR, self.BG_ALPHA)
                res['color'] = (fg, bg)
            
            elif key_lower == 'tooltip':
                res['tooltip'] = str(value)
            
            elif key_lower == 'label':
                res['label'] = str(value)
            
            elif key_lower == 'group':
                if isinstance(value, tuple) and len(value) == 2:
                    x, fg = value
                elif isinstance(value, str):
                    x, fg = value, None
                else:
                    x, fg = str(value), None
                
                if not isinstance(x, str): 
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Group name must be str.")
                fg = QColor(fg).setAlpha(self.FG_ALPHA) if fg and str(fg).startswith('#') else None
                if 'group' in self.INSPECTOR_KEYS:
                    lst.append(('group', (x, fg)))
                else:
                    res['group'] = (x, fg)
            
            elif key_lower == 'header':
                if isinstance(value, tuple) and len(value) == 2:
                    x, fg = value
                elif isinstance(value, str):
                    x, fg = value, None
                else:
                    x, fg = str(value), None
                
                if not isinstance(x, str): 
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Header name must be str.")
                fg = QColor(fg).setAlpha(self.FG_ALPHA) if fg and str(fg).startswith('#') else None
                if 'header' in self.INSPECTOR_KEYS:
                    lst.append(('header', (x, fg)))
                else:
                    res['header'] = (x, fg)
            
            elif key_lower == 'title':
                if isinstance(value, tuple) and len(value) == 2:
                    x, fg = value
                elif isinstance(value, str):
                    x, fg = value, None
                else:
                    x, fg = str(value), None
                
                if not isinstance(x, str): 
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Title name must be str.")
                fg = QColor(fg).setAlpha(self.FG_ALPHA) if fg and str(fg).startswith('#') else None
                if 'title' in self.INSPECTOR_KEYS:
                    lst.append(('title', (x, fg)))
                else:
                    res['title'] = (x, fg)
            
            elif key_lower == 'readonly':
                res['readonly'] = bool(value)
            
            elif key_lower == 'separator':
                if 'separator' in self.INSPECTOR_KEYS:
                    lst.append(('separator', True))
                else:
                    res['separator'] = True
            
            elif key_lower == 'space':
                if not isinstance(value, int): 
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Space height must be int.")
                if 'space' in self.INSPECTOR_KEYS:
                    lst.append(('space', value))
                else:
                    res['space'] = value

        # 设置基本属性
        res['name'] = monoa.name
        res['value'] = monoa.value

        # 设置默认值（type现在为None，会自动判断）
        for k, v in self.DEFAULTS.items():
            if k not in res:
                res[k] = v

        # 自动根据value判断类型
        if res['type'] is None:
            if monoa.value is None:
                res['type'] = str
                monoa.value = ""
            else:
                # 首先检查是否是可调用对象（函数按钮类型）
                if callable(monoa.value) and not isinstance(monoa.value, type) and monoa.value.__class__.__name__ in ('function', 'method'):
                    res['type'] = 'function'
                else:
                    # 根据value的实际类型自动判断
                    value_type = type(monoa.value)
                    if value_type in (int, float, str, bool, complex, datetime, list, dict):
                        res['type'] = value_type
                    else:
                        # 对于不支持的类型，使用str
                        res['type'] = str
        
        # 确保我们保留用户明确设置的类型
        # 检查MonoAttr对象中是否有明确设置的type属性
        if hasattr(monoa, '_attrs') and 'type' in monoa._attrs:
            # 从_attrs中获取type值并设置到res中
            user_type = monoa._attrs['type']
            if user_type in (int, float, str, bool, complex, datetime, list, dict):
                res['type'] = user_type
        elif hasattr(monoa, 'attrs') and 'type' in monoa.attrs:
            user_type = monoa.attrs['type']
            if user_type in (int, float, str, bool, complex, datetime, list, dict):
                res['type'] = user_type
        
        # 类型转换
        try:
            # 特殊处理function类型，不需要转换
            if res['type'] == 'function':
                # 确保button_name和function参数被添加到res字典中
                if hasattr(monoa, '_attrs') and 'button_name' in monoa._attrs:
                    res['button_name'] = monoa._attrs['button_name']
                else:
                    # 如果没有设置button_name，使用name作为默认值
                    res['button_name'] = res.get('name', 'Button')
                     
                if hasattr(monoa, '_attrs') and 'function' in monoa._attrs:
                    res['function'] = monoa._attrs['function']
                else:
                    # 如果没有设置function，使用value作为默认值
                    res['function'] = monoa.value
                 
                # 确保args和kwargs参数被添加到res字典中
                if hasattr(monoa, '_attrs') and 'args' in monoa._attrs:
                    res['args'] = monoa._attrs['args']
                else:
                    # 默认使用空列表
                    res['args'] = []
                 
                if hasattr(monoa, '_attrs') and 'kwargs' in monoa._attrs:
                    res['kwargs'] = monoa._attrs['kwargs']
                else:
                    # 默认使用空字典
                    res['kwargs'] = {}
                 
                # 确保function是可调用的
                if not callable(res['function']):
                    raise MonoaRuntimeEvalError(self.cmonoa, f"Function must be callable, got {type(res['function'])}.")
            elif res['type'] == complex and isinstance(monoa.value, str):
                monoa.value = complex(monoa.value.replace(' ', ''))
            elif res['type'] == datetime and isinstance(monoa.value, datetime):
                # datetime类型已经是datetime对象，无需转换
                pass
            else:
                monoa.value = res['type'](monoa.value)
        except Exception as e:
            raise MonoaRuntimeEvalError(self.cmonoa, f"Cannot convert value '{monoa.value}' to type '{res['type']}'.")

        # 对于function类型，跳过range和enum检查
        if res['type'] != 'function':
            self._check_range_with_type(res['range'], res['type'])
            self._check_enum_with_type(res['enum'], res['type'], monoa.value)

        return res, lst