#!/usr/bin/env python
#--coding:utf-8--

# @author: Vector Ouyang
# @date: 2022-03-20

import base64
import re
from gmssl import sm3, sm4, func

DEFAULT_CHARSET = "utf-8"

ENCODING_B64 = 0
ENCODING_HEX = 1
# 未实现
ENCODING_B58 = 2

SM4_ECB = 0
SM4_CBC = 1


def sm3_sign(data, encoding = ENCODING_B64):
    """SM3摘要算法
    Args:
        @data       : 要进行摘要的数据，字符
        @encoding   : 摘要结果的编码格式，ENCODING_B64：Base64；ENCODING_HEX：Hex
    Returns:
        Base64或Hex编码的签名结果
    """

    signature_hex = sm3.sm3_hash(func.bytes_to_list(data.encode(DEFAULT_CHARSET)))
    if encoding == ENCODING_HEX:
        return signature_hex
    # BASE64编码
    return base64.b64encode(bytes.fromhex(signature_hex)).decode()

def sm3_verify(data, sign, encoding = ENCODING_B64):
    """SM3签名验证
    Args:
        @data       : 源数据
        @sign       : 计算出来的签名
        @encoding   : sign的编码格式，ENCODING_B64：Base64；ENCODING_HEX：Hex
    Returns:
        True：成功，False：失败
    """

    signature_hex = sm3.sm3_hash(func.bytes_to_list(data.encode(DEFAULT_CHARSET)))
    if encoding == ENCODING_HEX:
        return signature_hex == sign
    # BASE64编码
    return sign == base64.b64encode(bytes.fromhex(signature_hex)).decode()



def sm4_encrypt(key, text, mode = SM4_ECB, iv = "0000000000000000", encoding = ENCODING_B64):
    """SM3摘要算法
    Args:
        @key        : 密钥，str格式，16个字符
        @text       : 要加密的数据
        @iv         : CBC模式的初始向量
        @encoding   : 加密结果的编码格式，ENCODING_B64：Base64；ENCODING_HEX：Hex
    Returns:
        Base64或Hex编码的加密结果
    """


    sm4_cryptor = sm4.CryptSM4()
    sm4_cryptor.set_key(key.encode(DEFAULT_CHARSET), sm4.SM4_ENCRYPT)
   
    if mode == SM4_ECB:
        encrypt_bytes = sm4_cryptor.crypt_ecb(text.encode(DEFAULT_CHARSET))
    
    if mode == SM4_CBC:
        encrypt_bytes = sm4_cryptor.crypt_cbc(iv.encode(DEFAULT_CHARSET), text.encode(DEFAULT_CHARSET))

    if encoding == ENCODING_HEX:
        return encrypt_bytes.hex()
        
    # BASE64编码
    return base64.b64encode(encrypt_bytes).decode()



def sm4_decrypt(key, text, mode = SM4_ECB, iv = "0000000000000000", encoding = ENCODING_B64):
    """SM3摘要算法
    Args:
        @key        : 密钥，str格式，16个字符
        @text       : 加密的数据
        @mode       : 加密的模式，ECB/CBC
        @iv         : CBC模式的初始向量
        @encoding   : text的编码格式，ENCODING_B64：Base64；ENCODING_HEX：Hex
    Returns:
        Base64或Hex编码的加密结果
    """


    sm4_cryptor = sm4.CryptSM4()
    sm4_cryptor.set_key(key.encode(DEFAULT_CHARSET), sm4.SM4_DECRYPT)
   
    if mode == SM4_ECB:
        if encoding == ENCODING_B64:
            decrypt_bytes = sm4_cryptor.crypt_ecb(base64.b64decode(text))
            return decrypt_bytes.decode(DEFAULT_CHARSET)
        if encoding == ENCODING_HEX:
            decrypt_bytes = sm4_cryptor.crypt_ecb(bytes.fromhex(text))
            return decrypt_bytes.decode(DEFAULT_CHARSET)
    
    if mode == SM4_CBC:
        iv_bytes = iv.encode(DEFAULT_CHARSET)
        if encoding == ENCODING_B64:
            decrypt_bytes = sm4_cryptor.crypt_cbc(iv_bytes, base64.b64decode(text))
            return decrypt_bytes.decode(DEFAULT_CHARSET)
        if encoding == ENCODING_HEX:
            decrypt_bytes = sm4_cryptor.crypt_cbc(iv_bytes, bytes.fromhex(text))
            return decrypt_bytes.decode(DEFAULT_CHARSET)


if __name__ == "__main__":
    sign_text = "123456789"
    sign = sm3_sign(sign_text)
    print(sign)
    print(sm3_verify(sign_text, sign))

    text = "hello world"
    key = "1234567890123456"
    # result = sm4_encrypt(key, text, mode=SM4_CBC)
    result = sm4_encrypt(key, text)
    print(result)
    # print(sm4_decrypt(key, result, mode=SM4_CBC))
    print(sm4_decrypt(key, result))

