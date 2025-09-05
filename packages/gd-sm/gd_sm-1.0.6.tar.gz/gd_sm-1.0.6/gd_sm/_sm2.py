from . import sm3
import logging
import secrets

logger = logging.getLogger(__name__)


class CryptSM2(object):
    ecc_table = {  # 选择素域，设置椭圆曲线参数
        'n': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123',
        'p': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF',
        'g': '32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7'
             'bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0',
        'a': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC',
        'b': '28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93',
    }

    n = int(ecc_table['n'], base=16)
    p = int(ecc_table['p'], base=16)
    a = int(ecc_table['a'], base=16)
    b = int(ecc_table['b'], base=16)

    @staticmethod
    def generate_private_key():  # 16进制字符串格式
        while True:
            key = secrets.token_hex(32)
            if CryptSM2.is_valid_private_key(key):
                return key

    @staticmethod
    def is_valid_private_key(d):  # 检查私钥或者过程中的k是否满足在[1, n-1]区间内
        n = int('FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123', 16)
        number = int(d, 16)
        return 1 <= number <= n - 1

    @staticmethod
    def is_compress_pubkey(key: str):  # 检查传入的公钥是不是压缩格式，即02/03开头+x，要求传入类型为16进制字符串
        return len(key) == 66 and key[:2] in {"02", "03"}

    @staticmethod
    def is_nor_compress_pubkey(key: str):  # 检查传入的公钥是不是非压缩格式，即04开头+x+y，要求传入类型为16进制字符串
        return len(key) == 130 and key[:2] == "04"

    def __init__(self, private_key=None):
        if isinstance(private_key, bytes):
            private_key = private_key.hex()
        self.private_key = private_key if private_key is not None else self.generate_private_key()
        logger.debug(f"SM2对象的私钥:{self.private_key}")
        self.para_len = len(self.ecc_table['n'])
        self.ecc_a3 = (self.a + 3) % self.p
        self.ecc_table = CryptSM2.ecc_table
        self.public_key = self.private_key_export_pubkey()

    def private_key_export_pubkey(self, private_key=None):  # 输出的公钥是x+y格式
        if private_key is None:
            private_key = self.private_key
        pubkey = self._kg(int(private_key, 16), self.ecc_table['g'])
        logger.debug(f"通过私钥{private_key}导出sm2公钥{pubkey}")
        return pubkey

    def nor_compressed_pubkey(self, key=None):  # 将公钥（默认使用实例的公钥）转成不压缩格式输出, 要求传入类型为16进制字符串
        if key is None:
            return "04" + self.public_key
        elif self.is_nor_compress_pubkey(key):
            return key
        elif self.is_compress_pubkey(key):
            prefix = key[:2]
            x_hex = key[2:]
            x_int = int(x_hex, 16)
            y2 = (pow(x_int, 3, self.p) + self.a * x_int + self.b) % self.p
            y_int = pow(y2, (self.p + 1) // 4, self.p)
            if (y_int % 2 == 0 and prefix == "03") or (y_int % 2 == 1 and prefix == "02"):
                p_int = self.p
                y_int = p_int - y_int  # 取对称点
            y_hex = f"{y_int:064x}"
            return "04" + x_hex + y_hex

    def compressed_pubkey(self, key=None):  # 将公钥（默认使用实例的公钥）转成压缩格式输出, 要求传入类型为16进制字符串
        if key is None:
            public_key = self.public_key
        elif self.is_compress_pubkey(key):
            return key
        elif self.is_nor_compress_pubkey(key):
            public_key = key[2:]
        else:
            public_key = key
        x_hex = public_key[:64]
        y_hex = public_key[64:]
        y_int = int(y_hex, 16)
        prefix = "02" if y_int % 2 == 0 else "03"
        return prefix + x_hex

    def _kg(self, k, point):  # kP运算
        point = '%s%s' % (point, '1')
        mask_str = '8'
        for i in range(self.para_len - 1):
            mask_str += '0'
        mask = int(mask_str, 16)
        temp = point
        flag = False
        for n in range(self.para_len * 4):
            if flag and isinstance(temp, str):
                temp = self._double_point(temp)
            if (k & mask) != 0:
                if flag:
                    temp = self._add_point(temp, point)
                else:
                    flag = True
                    temp = point
            k = k << 1
        return self._convert_jacb_to_nor(temp)

    def _double_point(self, point):  # 倍点
        try:
            l_p = len(point)
        except Exception as e:
            raise ValueError(f"传入的point非法:{e}")
        len_2 = 2 * self.para_len
        if l_p < self.para_len * 2:
            return None
        else:
            x1 = int(point[0:self.para_len], 16)
            y1 = int(point[self.para_len:len_2], 16)
            if l_p == len_2:
                z1 = 1
            else:
                z1 = int(point[len_2:], 16)
            t6 = (z1 * z1) % self.p
            t2 = (y1 * y1) % self.p
            t3 = (x1 + t6) % self.p
            t4 = (x1 - t6) % self.p
            t1 = (t3 * t4) % self.p
            t3 = (y1 * z1) % self.p
            t4 = (t2 * 8) % self.p
            t5 = (x1 * t4) % self.p
            t1 = (t1 * 3) % self.p
            t6 = (t6 * t6) % self.p
            t6 = (self.ecc_a3 * t6) % self.p
            t1 = (t1 + t6) % self.p
            z3 = (t3 + t3) % self.p
            t3 = (t1 * t1) % self.p
            t2 = (t2 * t4) % self.p
            x3 = (t3 - t5) % self.p
            if (t5 % 2) == 1:
                t4 = (t5 + ((t5 + self.p) >> 1) - t3) % self.p
            else:
                t4 = (t5 + (t5 >> 1) - t3) % self.p
            t1 = (t1 * t4) % self.p
            y3 = (t1 - t2) % self.p
            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (x3, y3, z3)

    def _add_point(self, p1, p2):  # 点加函数，P2点为仿射坐标即z=1，P1为Jacobi加重射影坐标
        len_2 = 2 * self.para_len
        l1 = len(p1)
        l2 = len(p2)
        if (l1 < len_2) or (l2 < len_2):
            return None
        else:
            x1 = int(p1[0:self.para_len], 16)
            y1 = int(p1[self.para_len:len_2], 16)
            if l1 == len_2:
                z1 = 1
            else:
                z1 = int(p1[len_2:], 16)
            x2 = int(p2[0:self.para_len], 16)
            y2 = int(p2[self.para_len:len_2], 16)
            t1 = (z1 * z1) % self.p
            t2 = (y2 * z1) % self.p
            t3 = (x2 * t1) % self.p
            t1 = (t1 * t2) % self.p
            t2 = (t3 - x1) % self.p
            t3 = (t3 + x1) % self.p
            t4 = (t2 * t2) % self.p
            t1 = (t1 - y1) % self.p
            z3 = (z1 * t2) % self.p
            t2 = (t2 * t4) % self.p
            t3 = (t3 * t4) % self.p
            t5 = (t1 * t1) % self.p
            t4 = (x1 * t4) % self.p
            x3 = (t5 - t3) % self.p
            t2 = (y1 * t2) % self.p
            t3 = (t4 - x3) % self.p
            t1 = (t1 * t3) % self.p
            y3 = (t1 - t2) % self.p
            form = '%%0%dx' % self.para_len
            form = form * 3
            return form % (x3, y3, z3)

    def _convert_jacb_to_nor(self, point):  # Jacobi加重射影坐标转换成仿射坐标
        len_2 = 2 * self.para_len
        x = int(point[0:self.para_len], 16)
        y = int(point[self.para_len:len_2], 16)
        z = int(point[len_2:], 16)
        z_inv = pow(z, self.p - 2, self.p)
        z_inv_squar = (z_inv * z_inv) % self.p
        z_inv_qube = (z_inv_squar * z_inv) % self.p
        x_new = (x * z_inv_squar) % self.p
        y_new = (y * z_inv_qube) % self.p
        z_new = (z * z_inv) % self.p
        if z_new == 1:
            form = '%%0%dx' % self.para_len
            form = form * 2
            return form % (x_new, y_new)
        else:
            return None

    def _verify(self, sign, data):  # 签名sign和数据data都是16进制字符串格式
        # 验签函数，sign签名r||s，E消息hash，public_key公钥
        r = int(sign[0:self.para_len], 16)
        s = int(sign[self.para_len:2 * self.para_len], 16)
        e = int(data, 16)
        t = (r + s) % self.n
        if t == 0:
            return 0
        p1 = self._kg(s, self.ecc_table['g'])
        p2 = self._kg(t, self.public_key)
        if p1 == p2:
            p1 = '%s%s' % (p1, 1)
            p1 = self._double_point(p1)
        else:
            p1 = '%s%s' % (p1, 1)
            p1 = self._add_point(p1, p2)
            p1 = self._convert_jacb_to_nor(p1)
        x = int(p1[0:self.para_len], 16)
        return r == ((e + x) % self.n)

    def _sign(self, data, k):  # data/k 均为16进制字符串
        e = int(data, 16)  # 消息转化为16进制字符串
        d = int(self.private_key, 16)
        k = int(k, 16)
        p1 = self._kg(k, self.ecc_table['g'])
        x = int(p1[0:self.para_len], 16)
        r = ((e + x) % self.n)
        if r == 0 or r + k == self.n:
            return None
        d_1 = pow(d + 1, self.n - 2, self.n)
        s = (d_1 * (k + r) - r) % self.n
        if s == 0:
            return None
        else:
            return '%064X%064X' % (r, s)

    def _encrypt(self, data):  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        # 加密函数，data消息(bytes)
        if isinstance(data, bytes):
            msg = data.hex()  # 消息转化为16进制字符串
        else:
            msg = data
        k = self.generate_private_key()
        c1 = self._kg(int(k, 16), self.ecc_table['g'])
        xy = self._kg(int(k, 16), self.public_key)
        x2 = xy[0:self.para_len]
        y2 = xy[self.para_len:2 * self.para_len]
        ml = len(msg)
        t = sm3.sm3_kdf(xy.encode('utf8'), ml / 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % ml
            c2 = form % (int(msg, 16) ^ int(t, 16))
            c3 = sm3.sm3_hash(bytes.fromhex(x2 + msg + y2))
            return (c1 + c3 + c2).upper()

    def _decrypt(self, data):  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        # 解密函数，data密文（bytes）
        if isinstance(data, bytes):
            data = data.hex()  # 消息转化为16进制字符串
        len_2 = 2 * self.para_len
        len_3 = len_2 + 64
        c1 = data[0:len_2]
        c3 = data[len_2:len_3]
        c2 = data[len_3:]
        xy = self._kg(int(self.private_key, 16), c1)
        x2 = xy[0:self.para_len]
        y2 = xy[self.para_len:len_2]
        cl = len(c2)
        t = sm3.sm3_kdf(xy.encode('utf8'), cl / 2)
        if int(t, 16) == 0:
            return None
        else:
            form = '%%0%dx' % cl
            m = form % (int(c2, 16) ^ int(t, 16))
            u = sm3.sm3_hash(bytes.fromhex(x2 + m + y2))
            return m.upper()

    def _sm3_z(self, data):
        z = '0080' + '31323334353637383132333435363738' + \
            self.ecc_table['a'] + self.ecc_table['b'] + self.ecc_table['g'] + self.public_key
        za = sm3.sm3_hash(z)
        m_ = za + data
        e = sm3.sm3_hash(m_)
        return e

    def _sign_with_sm3(self, data):  # data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        if isinstance(data, bytes):
            data = data.hex()
        sign_data = self._sm3_z(data)
        random_hex_str = self.generate_private_key()
        sign = self._sign(sign_data, random_hex_str)  # 16进制
        return sign

    def _verify_with_sm3(self, sign, data):  # sign、data可以是16进制字符串或者bytes，统一转成16进制字符串处理
        if isinstance(sign, bytes):
            sign = sign.hex()
        if isinstance(data, bytes):
            data = data.hex()
        sign_data = self._sm3_z(data)
        return self._verify(sign, sign_data)
