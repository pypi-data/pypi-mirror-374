from cryptography.hazmat.primitives import hashes
from math import ceil
import binascii
import hmac
import base64


def sm3_hash(msg):  # msg可以是16进制字符串或者bytes
    if not isinstance(msg, (str, bytes)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    try:
        msg = msg if isinstance(msg, bytes) else bytes.fromhex(msg)
    except ValueError:
        raise ValueError("不是合法的十六进制字符串，无法转换为bytes")
    d = hashes.Hash(hashes.SM3())
    d.update(msg)
    value = d.finalize()
    return value.hex().upper()


def check_sm3(msg, hash_data):  # msg/hash_data可以是16进制字符串或者bytes
    if not isinstance(msg, (str, bytes)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    if not isinstance(hash_data, (str, bytes)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    try:
        msg = msg.lower() if isinstance(msg, str) else msg.hex()
        hash_data = hash_data.lower() if isinstance(hash_data, str) else hash_data.hex()
    except ValueError:
        raise ValueError("不是合法的十六进制字符串，无法转换为bytes")
    return True if sm3_hash(msg).lower() == hash_data.lower() else False


def sm3_kdf(z, key_len):  # z为16进制字符串（str），key_len为密钥长度（单位byte），这个方法是sm2算法使用
    key_len = int(key_len)
    ct = 0x00000001  # 计数器，标准要求不能超过2的32次方
    count = ceil(key_len / 32)  # 迭代次数
    zin = [i for i in bytes.fromhex(z.decode('utf8'))]
    ha = ""
    for i in range(count):
        msg = zin + [i for i in binascii.a2b_hex(('%08x' % ct).encode('utf8'))]
        ha = ha + sm3_hash(bytes(msg))
        ct += 1
    return ha[0: key_len * 2]


def sm3_hmac(key, msg, rt="hex"):
    #  使用sm3算法进行h_mac计算
    if not isinstance(msg, (str, bytes)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    if not isinstance(key, (str, bytes)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    key = key if isinstance(key, bytes) else bytes.fromhex(key)
    msg = msg if isinstance(msg, bytes) else bytes.fromhex(msg)
    try:
        h = hmac.new(key, msg, digestmod="sm3")
        if rt == "hex":
            return h.hexdigest()
        elif rt == "base64":
            return base64.urlsafe_b64encode(h.digest()).decode('utf-8')
    except ValueError:
        raise ValueError("不是合法的十六进制字符串，无法转换为bytes")
