import inspect
from functools import wraps

def validate_or(param_dict:dict, invalid_return, target_name = 'validation'):
    """
    只要有一种校验通过，就算通过
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            flag = False
            # 获取函数签名
            sig = inspect.signature(func)
            # 提取位置参数与关键字参数的映射
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            # 从 bound_args 中获取 validation 参数
            target = bound_args.arguments.get(target_name, None)
            if isinstance(target, dict):
                for param_key, param_value in param_dict.items():
                    if target.get(param_key, "") == param_value:
                        flag = True
                        break
            if not flag:
                raise invalid_return
            return func(*args, **kwargs)
        return wrapper
    return decorator