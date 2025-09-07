from binascii import unhexlify
from Crypto.Cipher import AES, DES, DES3
from hashlib import md5, sha256
import hmac
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad


class AESCipher:
    """
    AES/CBC/PKCS5Padding
    """

    def __init__(self, key: str, iv: str):
        self.key = key
        self.iv = iv
        self.size = AES.block_size

    def encrypt(self, text: str, is_hex: bool = False) -> str:
        """
        加密
        """
        text = text.encode("utf-8")
        if len(text) % self.size:
            text = pad(text, self.size)
        cipher = AES.new(key=self.key.encode(), mode=AES.MODE_CBC, IV=self.iv.encode())
        encrypted_text = cipher.encrypt(text)
        if is_hex:
            return encrypted_text.hex()
        else:
            return b64encode(encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text: str, is_hex: bool = False) -> str:
        """
        解密
        """
        if is_hex:
            encrypted_text = unhexlify(encrypted_text)
        else:
            encrypted_text = encrypted_text.encode("utf-8")
            encrypted_text = b64decode(encrypted_text)
        if len(encrypted_text) % self.size:
            encrypted_text = pad(encrypted_text, self.size)
        cipher = AES.new(key=self.key.encode(), mode=AES.MODE_CBC, IV=self.iv.encode())
        decrypted_text = cipher.decrypt(encrypted_text)
        return unpad(decrypted_text, self.size).decode("utf-8")


class DESCipher:
    """
    DES
    """

    def __init__(self, key: str, iv: str):
        self.key = key
        self.iv = iv
        self.size = DES.block_size

    def __pad__(self, text: str):
        return text + (self.size - len(text.encode()) % self.size) * chr(self.size - len(text.encode()) % self.size)

    def __unpad__(self, text: str):
        return text[: -ord(text[len(text) - 1 :])]

    def encrypt(self, text):
        """
        加密
        """
        text = self.__pad__(text).encode()
        cipher = DES.new(key=self.key.encode(), mode=DES.MODE_CBC, IV=self.iv.encode())
        encrypted_text = cipher.encrypt(text)
        return b64encode(encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text: str):
        """
        解密
        """
        encrypted_text = encrypted_text.encode("utf-8")
        encrypted_text = b64encode(encrypted_text)
        cipher = DES.new(key=self.key.encode(), mode=DES.MODE_CBC, IV=self.iv.encode())
        decrypted_text = cipher.decrypt(encrypted_text)
        return self.__unpad__(decrypted_text).decode("utf-8")


class DES3Cipher:
    """
    DES3
    """

    def __init__(self, key: str, iv: str):
        self.key = key
        self.iv = iv
        self.size = DES3.block_size

    def pad(self, text: str):
        return text + (self.size - len(text.encode()) % self.size) * chr(self.size - len(text.encode()) % self.size)

    def un_pad(self, text: str):
        return text[: -ord(text[len(text) - 1 :])]

    def encrypt(self, text):
        """
        加密
        """
        text = self.pad(text).encode()
        cipher = DES3.new(key=self.key.encode(), mode=DES3.MODE_CBC, IV=self.iv.encode())
        encrypted_text = cipher.encrypt(text)
        return b64encode(encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text):
        """
        解密
        """
        encrypted_text = b64decode(encrypted_text)
        cipher = DES3.new(key=self.key.encode(), mode=DES3.MODE_CBC, IV=self.iv.encode())
        decrypted_text = cipher.decrypt(encrypted_text)
        return self.un_pad(decrypted_text).decode("utf-8")


class RSACipher:
    """
    RSA-PKCS1
    """

    def __init__(self, publicKey: str = "", privateKey: str = "") -> None:
        if publicKey and not publicKey.startswith("-----BEGIN PUBLIC KEY-----"):
            publicKey = "-----BEGIN PUBLIC KEY-----\n" + publicKey + "\n-----END PUBLIC KEY-----"
        if privateKey and not privateKey.startswith("-----BEGIN PRIVATE KEY-----"):
            privateKey = "-----BEGIN PRIVATE KEY-----\n" + privateKey + "\n-----END PRIVATE KEY-----"
        if publicKey:
            self.publicKey = RSA.importKey(publicKey)
        if privateKey:
            self.privateKey = RSA.importKey(privateKey)

    def encrypt(self, data) -> str:
        """
        加密
        """
        clipher = PKCS1_v1_5.new(self.publicKey)
        encryptText = b64encode(clipher.encrypt(data.encode()))
        return encryptText.decode()

    def decrypt(self, data) -> str:
        """
        解密
        """
        clipher = PKCS1_v1_5.new(self.privateKey)
        decryptText = clipher.decrypt(b64decode(data), None)
        return decryptText.decode()


def MD5(data: str) -> str:
    """
    md5加密字符串
    """
    if not data:
        return ""
    obj = md5()
    obj.update(data.encode())
    return obj.hexdigest()


def hmacSha256(message: str, secret: str):
    message = message.encode()
    secret = secret.encode()
    hash = hmac.new(secret, message, sha256)
    return hash.hexdigest()
