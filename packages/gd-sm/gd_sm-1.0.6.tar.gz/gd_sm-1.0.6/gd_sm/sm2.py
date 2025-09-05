from . import _sm2
import logging

logger = logging.getLogger(__name__)


class SM2(_sm2.CryptSM2):

    def __init__(self, private_key=None):
        super().__init__(private_key)

    def sign(self, data):  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        if not isinstance(data, (str, bytes)):
            raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
        return self._sign_with_sm3(data)

    def verify(self, data, sign):  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        if not isinstance(data, (str, bytes)):
            raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
        return self._verify_with_sm3(sign, data)

    def encrypt(self, data):
        if not isinstance(data, (str, bytes)):
            raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
        return self._encrypt(data)  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理

    def decrypt(self, data):  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        if not isinstance(data, (str, bytes)):
            raise TypeError("传入了非法的数据类型，传入的数据必须是16进制字符串或者bytes类型")
        return self._decrypt(data)
