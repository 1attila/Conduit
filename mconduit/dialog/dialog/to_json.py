from typing import Dict, Optional, Tuple, Any


def to_json(fields: Dict[str, Any | Tuple[Any, Any] | Optional[Any]]) -> Dict[str, Any]:
    """
    Docstring for to_json
    
    :param fields: Description
    :type fields: Dict[str, Any | Optional[Any]]
    :return: Description
    :rtype: Dict[str, Any]
    """

    if type(fields.copy().popitem()[1]) in [tuple, Tuple]:

        return {
            k: v[1]
            for k, v in fields.items()
            if (v[1] not in v[0] if type(v[0]) != list else v[1] != v[0])
        }

    return {
        k: v
        for k, v in fields.items()
        if v is not None
    }