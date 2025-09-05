import secrets
import pytest
from gd_sm import *

"""
对gd_sm库进行测试，cd test进入本目录，执行pytest test.py
"""


class TestSM2:
    def setup_class(self):
        pass

    def test_01(self):
        """ 测试对16进制类型的数据、bytes类型的数据进行签名和验签 """
        m2 = sm2.SM2()
        test_data_hex = secrets.token_hex(128)
        test_data_bytes = bytes.fromhex(test_data_hex)
        sign_data1 = m2.sign(test_data_hex)
        sign_data2 = m2.sign(test_data_bytes)
        sign_data_bytes = bytes.fromhex(sign_data2)
        assert m2.verify(test_data_hex, sign_data1)
        assert m2.verify(test_data_bytes, sign_data1)
        assert m2.verify(test_data_bytes, sign_data_bytes)
        assert m2.verify(test_data_hex, sign_data_bytes)

    def test_02(self):
        """ 测试对16进制类型的数据、bytes类型的数据进行加密和解密 """
        m2 = sm2.SM2()
        test_data_hex = secrets.token_hex(128).upper()
        test_data_bytes = bytes.fromhex(test_data_hex)
        d1 = m2.encrypt(test_data_hex)
        d2 = m2.encrypt(test_data_bytes)
        d2_bytes = bytes.fromhex(d2)
        assert m2.decrypt(d1) == test_data_hex
        assert m2.decrypt(d2_bytes) == test_data_hex

    def test_03(self):
        """ 测试传入的数据必须是16进制字符串或者bytes类型 """
        m2 = sm2.SM2()
        with pytest.raises(TypeError):
            m2.sign(123123)
            m2.sign([1, 2, 3])
            m2.sign("zzzz")

    def test_04(self):
        """ 测试公钥格式x+y转换成非压缩格式 """
        m2 = sm2.SM2()
        key = m2.nor_compressed_pubkey()
        assert key.startswith("04") and len(key) == 130
        assert key[2:] == m2.public_key

    def test_05(self):
        """ 测试公钥格式x+y转换成压缩格式 """
        m2 = sm2.SM2()
        key = m2.compressed_pubkey()
        assert key[0:2] in ("02", "03") and len(key) == 66
        assert key[2:] == m2.public_key[0:64]

    def test_06(self):
        """ 测试公钥格式压缩格式与非压缩格式转换 """
        m2 = sm2.SM2()
        compress_key = m2.compressed_pubkey()
        nor_compress_key = m2.nor_compressed_pubkey(compress_key)
        assert "04" + m2.public_key == nor_compress_key
        assert compress_key == m2.compressed_pubkey(nor_compress_key)


class TestSM3:
    def setup_class(self):
        pass

    def test_01(self):
        """ 测试对16进制类型的数据、bytes类型的数据进行hash计算和验证 """
        test_data_hex = secrets.token_hex(128)
        test_data_bytes = bytes.fromhex(test_data_hex)
        h1 = sm3.sm3_hash(test_data_hex)
        h2 = sm3.sm3_hash(test_data_bytes)
        h2_bytes = bytes.fromhex(h2)
        assert sm3.check_sm3(test_data_hex, h1)
        assert sm3.check_sm3(test_data_hex, h2_bytes)
        assert sm3.check_sm3(test_data_bytes, h2_bytes)
        assert sm3.check_sm3(test_data_bytes, h1)

    def test_02(self):
        """ 测试传入的数据必须是16进制字符串或者bytes类型 """
        with pytest.raises(TypeError):
            sm3.sm3_hash(123123)
            sm3.sm3_hash([1, 2, 3])
            sm3.sm3_hash("zzzz")
        with pytest.raises(TypeError):
            sm3.check_sm3(123123, "11")
            sm3.check_sm3([1, 2, 3], "11")
            sm3.check_sm3("zzzz", "11")
            sm3.check_sm3("11", 123123)
            sm3.check_sm3("11", [1, 2, 3])
            sm3.check_sm3("11", "zzzz")


class TestSM4:
    def setup_class(self):
        pass

    def test_01(self):
        """ 测试对16进制类型的数据、bytes类型的数据进行加密和解密验证（cbc模式） """
        test_data_hex = secrets.token_hex(128).upper()
        test_data_bytes = bytes.fromhex(test_data_hex)
        key = secrets.token_hex(16)
        key_bytes = bytes.fromhex(key)
        h1 = sm4.encrypt(key, test_data_hex)
        h2 = sm4.encrypt(key_bytes, test_data_bytes)
        h2_bytes = bytes.fromhex(h2)
        assert sm4.decrypt(key, h1) == test_data_hex
        assert sm4.decrypt(key_bytes, h2_bytes) == test_data_hex

    def test_02(self):
        """ 测试cbc模式加密 """
        test_data = secrets.token_hex(128).upper()
        key = secrets.token_hex(16)
        iv = secrets.token_hex(16)
        enc_data = sm4.encrypt(key=key, plain_data=test_data, mode="cbc", iv=iv)
        assert sm4.decrypt(key, enc_data, mode="cbc", iv=iv) == test_data

    def test_03(self):
        """ 测试加密传入的密钥key，iv和数据必须是16进制字符串或者bytes类型 """
        test_data = secrets.token_hex(128)
        key = secrets.token_hex(16)
        iv = secrets.token_hex(16)
        with pytest.raises(TypeError):
            key = secrets.token_hex(16)
            sm4.encrypt(1231233, test_data)
            sm4.encrypt([1, 3, 4], test_data)
            sm4.encrypt("123", test_data)
            sm4.encrypt(key, 1231233)
            sm4.encrypt(key, [1, 3, 4])
            sm4.encrypt(key, "123")
            sm4.encrypt(key, test_data, mode="cbc", iv=1231233)
            sm4.encrypt(key, test_data, mode="cbc", iv=[1, 3, 4])
            sm4.encrypt(key, test_data, mode="cbc", iv="123")

    def test_04(self):
        """ 测试解密传入的密钥key，iv和数据必须是16进制字符串或者bytes类型 """
        test_data = secrets.token_hex(128)
        key = secrets.token_hex(16)
        iv = secrets.token_hex(16)
        with pytest.raises(TypeError):
            key = secrets.token_hex(16)
            sm4.decrypt(1231233, test_data)
            sm4.decrypt([1, 3, 4], test_data)
            sm4.decrypt("123", test_data)
            sm4.decrypt(key, 1231233)
            sm4.decrypt(key, [1, 3, 4])
            sm4.decrypt(key, "123")
            sm4.decrypt(key, test_data, mode="cbc", iv=1231233)
            sm4.decrypt(key, test_data, mode="cbc", iv=[1, 3, 4])
            sm4.decrypt(key, test_data, mode="cbc", iv="123")

    def test_05(self):
        """ 测试加密解密只支持ecb/cbc模式 """
        test_data = secrets.token_hex(128)
        key = secrets.token_hex(16)
        enc_data = sm4.encrypt(key, test_data, mode="Ecb")
        sm4.decrypt(key, enc_data, mode="EcB")
        enc_data = sm4.encrypt(key, test_data, mode="CbC")
        sm4.decrypt(key, enc_data, mode="cbC")
        with pytest.raises(ValueError):
            sm4.encrypt(key, test_data, mode="test")
            sm4.encrypt(key, test_data, mode="c bc")
            sm4.decrypt(key, test_data, mode=["c", "b", "c"])
            sm4.decrypt(key, test_data, mode="cb c")

    def test_06(self):
        """ 测试pkcs7填充"""
        key = secrets.token_hex(16)
        for i in range(16):
            test_data = secrets.token_hex(128 + i).upper()
            enc_data = sm4.encrypt(key, test_data, is_pad=True)
            data = sm4.decrypt(key, enc_data, is_pad=True)
            assert data == test_data
            assert len(enc_data) == 288
