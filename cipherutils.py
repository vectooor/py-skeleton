#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: jcouyang
# date: 2021-09-26

from Crypto.Cipher import AES
import base64
import hashlib

from umsexception import UmsException

ENCODING = 'utf-8'

def byte2hexstr(byte):
    return byte.hex().upper()

def pkcs5_padding(value, BS):
    """PKCS5Pading

    意思就是长度必须是BS的倍数，如果不是，则进行填充。
    例如，如果长度是12，BS=16，需要补 4 个 0x04
    """
    return value + (BS - len(value) % BS) * chr(BS - len(value) % BS)

class AESUtils(object):
    """AES加解密，但是这里的key进行过运算，所以key可以是任意长度
    """

    def __init__(self, mode=AES.MODE_ECB):
        self.mode = mode

    def _pkcs5_padding(self, value):
        return pkcs5_padding(value, AES.block_size)

    def _sha1png_key(self, key):
        """等同于Java中SHA1PRNG算法获取安全随机数

        ```
            SecureRandom secureRandom = SecureRandom.getInstance("SHA1PRNG");
            secureRandom.setSeed(toHash256(seed));
            # 如果Java中这里设置256，Python中这个函数就失效了
            # 时间紧迫，抽时间再来研究
            keyGenerator.init(128, secureRandom);
            SecretKey secretKey = keyGenerator.generateKey();
            byte[] encode = secretKey.getEncoded();
            SecretKeySpec secretKeySpec = new SecretKeySpec(encode, "AES");
        ```

        """
        if str == type(key):
            key = key.encode(ENCODING)
        else:
            raise UmsException("key must be a string")

        digest = hashlib.sha256()
        digest.update(key)
        sha256 = digest.digest()

        key = hashlib.sha1(sha256).digest()
        key = hashlib.sha1(key).digest()

        return key[:16]

    def encrypt(self, data, key):
        """AES加密

        Args:
            @param data : 要加密的字符串，str类型
            @param key  : 加密密钥，32位，str类型

        Returns:
            base64加密的字符串
        """
        if str == type(key):
            # key = key.encode(ENCODING)
            key = self._sha1png_key(key)
        else:
            raise UmsException("key must be a string")

        aes = AES.new(key, self.mode)
        cipherbytes = aes.encrypt(self._pkcs5_padding(data).encode(ENCODING))
        # b64encode返回的是bytes类型，通过decode转为string类型
        return base64.b64encode(cipherbytes).decode(ENCODING)

    def decrypt(self, data, key):
        """AES解密

        Args:
            @param data : 密文，base64编码
            @param key  : 解密密钥，32位，str类型

        Returns:
            解密成功后的明文
        """
        if str == type(key):
            # key = key.encode(ENCODING)
            key = self._sha1png_key(key)
        else:
            raise UmsException("key must be a string")

        aes = AES.new(key, self.mode)
        # 解密后返回的是bytes，通过decode转为string类型
        paddingtext = aes.decrypt(base64.b64decode(data)).decode(ENCODING)
        # ord和chr是配对函数：ord('a')=97 chr(97)='a'
        # 解密出来的明文也是pkcs5padding，这里是反向padding
        return paddingtext[:-ord(paddingtext[-1])]

if __name__ == '__main__':

    aes = AESUtils()

    text = '123456'
    key = '28637AAC596048ABB6C265B608E523FEvectooor'
    print("text=[{}];key=[{}]".format(text, key))

    # 加密
    ciphertext = aes.encrypt(text, key)
    print("ciphertext=[{}]".format(ciphertext))

    # 解密
    plaintext = aes.decrypt(ciphertext, key)
    print("plaintext=[{}]".format(plaintext))
