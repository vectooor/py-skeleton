# encoding:utf-8
import datetime
import math
import random
import string

def format_now(pattern):
    """格式化当前时间

    Args:
        @pattern: 参考格式：%Y-%m-%d %H:%M:%S

    Returns:
        格式化以后的时间字符串
    """
    return datetime.datetime.now().strftime(pattern)

def get_random(len, contain_char = False, upcase = False):
    """生成指定长度的随机数

    Args:
        @len          : 随机生成字符串的长度
        @contain_char : 是否包含字母
        @upcase       : 包含字母时，返回的字母是否转为大写

    Returns:
        长度为len的字符串
    """
    if contain_char:
        result = ""
        factors = string.ascii_letters + string.digits
        for i in range(len):
            result += random.choice(factors)
        return (result.upper() if upcase else result)
    else:
        rd = random.randint(1, math.pow(10, len))
        return str(rd).zfill(len)

if __name__ == '__main__':
    print("now =", format_now('%Y-%m-%d %H:%M:%S'))
    print("random =", get_random(32, True))
