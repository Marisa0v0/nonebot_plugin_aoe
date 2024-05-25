"""辅助函数"""

from typing import Callable

"""
call = 调用
callable = 可调用的 = 函数

Callable = function 函数
Callable[[参数], 返回值]

Callable[[str, bool], any]:
def function(arg1: str, arg2: bool) -> any: ...
"""
def verify(message: str, arg_length: int, processor: Callable[[str, bool], any]) -> tuple[bool, dict]:
    """
    不知道怎么写出来的，但这个函数可以一键验证所有格式为

    .指令 名词 数字

    格式的指令是否合法,并且将名词和数字分别以两个返回值返回回去。
    使用时只需要通过 if 鉴定 profession 的返回值是否是 false 就可以了

    :param message:     要处理的参数信息
    :param arg_length:  参数的数量
    :param processor:   对参数进行处理的函数，第一个参数是要处理的信息，第二个参数规定正常返回与否，返回用
    """
    if not message:
        """
        通用化/接口化处理，自定义 processor 函数
        processor = verify_recruiting_pop
        processor(message, False)
          -> profession, number  # 满足条件时   (flag=True)
          -> None, 0             # 不满足条件时 (flag=False)
        """
        # processor(message, False) =
        # verify_recruiting_pop(message, False) -> None, 0
        # return False, None, 0
        # .分配人口
        return False, processor(message, False)

    args: list[str] = message.split()  # .分配人口 铁匠  -->> args = ['铁匠']
    if len(args) != arg_length:
        # processor(message, False) =
        # verify_recruiting_pop(message, False) -> None, 0
        # return False, None, 0
        # .分配人口 铁匠
        # .分配人口 铁匠 1 莎莎是猪
        return False, processor(message, False)

    profession, number = args
    if not number.isdigit():
        # processor(message, False) =
        # verify_recruiting_pop(message, False) -> None, 0
        # return False, None, 0
        # .分配人口 铁匠 a
        return False, processor(message, False)

    # processor(message) =
    # verify_recruiting_pop(message, True) -> profession, number
    # -> return True, profession, number
    # .分配人口 铁匠 1
    return True, processor(message)


def verify_recruiting_pop(message: str, flag: bool = True) -> tuple[str|None, int]:
    """返回职业和人口"""
    """
    if flag:
        profession = message.split()[0]
        number = message.split()[1]
        number = int(number)
        return profession, number
    else:
        return None, 0
    """
    return (message.split()[0], int(message.split()[1])) if flag else (None, 0)


__all__ = [
    "verify",
    "verify_recruiting_pop",
]