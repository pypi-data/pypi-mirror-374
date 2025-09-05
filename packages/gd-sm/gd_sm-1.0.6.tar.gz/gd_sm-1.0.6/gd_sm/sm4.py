import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


def encrypt(key, plain_data, mode='ecb', iv='00' * 16, is_pad=False):  # key/plain_data/iv可以传入16进制字符串或者bytes
    if not all(isinstance(i, (bytes, str)) for i in (key, plain_data, iv)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    try:
        plain_data = plain_data if isinstance(plain_data, bytes) else bytes.fromhex(plain_data)
        key = key if isinstance(key, bytes) else bytes.fromhex(key)
        iv = iv if isinstance(iv, bytes) else bytes.fromhex(iv)
    except ValueError:
        raise ValueError("不是合法的十六进制字符串，无法转换为bytes")
    mode = mode.lower()
    if mode == 'cbc':
        mode = modes.CBC(iv)
    elif mode == 'ecb':
        mode = modes.ECB()
    else:
        raise ValueError("不支持的模式,当前sm4只支持cbc/ecb模式")
    if is_pad:  # 使用PKCS7进行填充
        pad = padding.PKCS7(algorithms.SM4.block_size).padder()
        padded_plain_data = pad.update(plain_data) + pad.finalize()
    else:  # 不进行任何填充，要求数据必须是16字节整倍数
        if len(plain_data) % 16 != 0:
            raise ValueError("由于采用不填充模式，要求传入的数据需是16字节整倍数")
        padded_plain_data = plain_data
    # 创建SM4对象
    cipher = Cipher(algorithms.SM4(key), mode, backend=default_backend())
    encryptor = cipher.encryptor()  # 加密
    logger.debug(f"开始进行sm4加密计算,算法模式{mode.name},加密密钥:{key.hex()},加密数据长度:{len(plain_data) / 2}字节")
    cipher_data = encryptor.update(padded_plain_data)
    logger.debug(f"完成sm4加密计算")
    return cipher_data.hex().upper()


def decrypt(key, cipher_data, mode='ecb', iv='00' * 16, is_pad=False):  # key/cipher_data/iv可以传入16进制字符串或者bytes
    if not all(isinstance(i, (bytes, str)) for i in (key, cipher_data, iv)):
        raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
    try:
        cipher_data = cipher_data if isinstance(cipher_data, bytes) else bytes.fromhex(cipher_data)
        key = key if isinstance(key, bytes) else bytes.fromhex(key)
        iv = iv if isinstance(iv, bytes) else bytes.fromhex(iv)
    except ValueError:
        raise ValueError("不是合法的十六进制字符串，无法转换为bytes")
    mode = mode.lower()
    if mode == 'cbc':
        mode = modes.CBC(iv)
    elif mode == 'ecb':
        mode = modes.ECB()
    else:
        raise ValueError("不支持的模式,当前sm4只支持cbc/ecb模式")
    # 创建SM4对象
    cipher = Cipher(algorithms.SM4(key), mode, backend=default_backend())
    decryptor = cipher.decryptor()  # 解密
    logger.debug(f"开始进行sm4解密计算,算法模式{mode.name},解密密钥:{key.hex()}")
    padded_plain_data = decryptor.update(cipher_data)
    # 去除填充
    if is_pad:  # 使用PKCS7进行填充
        unpad = padding.PKCS7(algorithms.SM4.block_size).unpadder()
        plain_data = unpad.update(padded_plain_data) + unpad.finalize()
    else:   # 非填充模式
        plain_data = padded_plain_data
    logger.debug(f"完成sm4解密计算,解密后的数据长度:{len(plain_data)}字节")
    return plain_data.hex().upper()
