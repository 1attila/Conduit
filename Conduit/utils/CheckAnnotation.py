from typing import Callable


def check_annotation(fn: Callable, param_type: object) -> bool:

    annotation = fn.__annotations__

    if "return" in annotation.keys():
        annotation.pop("return")

    for item in annotation.values():
        param = item
        
    return param == param_type