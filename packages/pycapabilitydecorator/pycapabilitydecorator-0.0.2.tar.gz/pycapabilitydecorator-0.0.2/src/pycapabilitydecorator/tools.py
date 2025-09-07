import json
import types
from typing import Any, Dict, List

class tools:
    
    @staticmethod
    def clean_capabilities_meta(capabilities: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清理 capabilities 元数据，移除不可序列化的函数对象"""
        capabilities_meta = []
        for cap in capabilities.values():
            cap_copy = tools.deep_clean_dict(cap)
            capabilities_meta.append(cap_copy)
        return capabilities_meta

    @staticmethod
    def deep_clean_dict(obj: Any) -> Any:
        """深度清理字典，移除所有不可序列化的对象"""
        if isinstance(obj, dict):
            cleaned = {}
            for key, value in obj.items():
                # 跳过函数类型的值
                if callable(value) or isinstance(value, (types.FunctionType, types.MethodType)):
                    continue
                # 递归清理嵌套字典和列表
                elif isinstance(value, dict):
                    cleaned[key] = tools.deep_clean_dict(value)
                elif isinstance(value, list):
                    cleaned[key] = tools.deep_clean_list(value)
                else:
                    # 只保留可序列化的值
                    try:
                        json.dumps(value)
                        cleaned[key] = value
                    except (TypeError, ValueError):
                        # 如果不能序列化，转换为字符串
                        cleaned[key] = str(value)
            return cleaned
        return obj

    @staticmethod
    def deep_clean_list(obj: Any) -> Any:
        """深度清理列表，移除所有不可序列化的对象"""
        if isinstance(obj, list):
            cleaned = []
            for item in obj:
                # 跳过函数类型的值
                if callable(item) or isinstance(item, (types.FunctionType, types.MethodType)):
                    continue
                # 递归清理嵌套字典和列表
                elif isinstance(item, dict):
                    cleaned.append(tools.deep_clean_dict(item))
                elif isinstance(item, list):
                    cleaned.append(tools.deep_clean_list(item))
                else:
                    # 只保留可序列化的值
                    try:
                        json.dumps(item)
                        cleaned.append(item)
                    except (TypeError, ValueError):
                        # 如果不能序列化，转换为字符串
                        cleaned.append(str(item))
            return cleaned
        return obj