import os
from secrets import token_bytes


class Crypt:

    def __init__(self, file_path: str, sk_len = 4) -> None:
        self.__file_path = file_path
        self.__secret_key = self.__generate_secret_key(sk_len)


    def __repr__(self) -> str:
        return f"Crypt(file_path={self.__file_path})"


    def __rename_file(self, ori_file: str, new_ext: str) -> str:
        ori_ext = "." + ori_file.split(".")[-1]
        new_file = ori_file.replace(ori_ext, new_ext)
        return new_file


    def __generate_secret_key(self, length: int) -> int:
        tb: bytes = token_bytes(length)
        return int.from_bytes(tb, "big")


    def __enc(self, original: str) -> int:
        original_bytes: bytes = original.encode()
        original_key: int = int.from_bytes(original_bytes, "big")
        encrypted: int = original_key ^ self.__secret_key
        return encrypted


    def __dec(self, k1: int, k2: int) -> str:
        decrypted: int = k1 ^ k2
        temp: bytes = decrypted.to_bytes((decrypted.bit_length()+ 7) // 8, "big")
        return temp.decode()


    @property
    def secret(self) -> int:
        return self.__secret_key


    def encrypt(
        self,
        enc_file_ext: str = ".tom",
        ret_enc_path: bool = True,
        del_ori: bool = True
    ) -> None|str:

        with open(self.__file_path, "r") as f:
            ori = f.read().splitlines()
        enc_ori = [self.__enc(o) for o in ori]

        enc_file_path = self.__rename_file(self.__file_path, enc_file_ext)
        with open(enc_file_path, "w") as f:
          f.write('\n'.join(str(i) for i in enc_ori))

        if del_ori and os.path.exists(self.__file_path):
            os.remove(self.__file_path)

        if ret_enc_path:
            return enc_file_path


    def decrypt(
        self,
        enc_file_path: str,
        secret_key: int,
        dec_file_ext: str = ".py",
        ret_dec_path: bool = True,
        del_enc: bool = True
    ) -> None|str:

        with open(enc_file_path, "r") as f:
            enc = f.read().splitlines()
        dec = [self.__dec(int(e), secret_key) for e in enc]

        dec_file_path = self.__rename_file(enc_file_path, dec_file_ext)
        with open(dec_file_path, "w") as f:
            f.write('\n'.join(str(i) for i in dec))

        if del_enc and os.path.exists(enc_file_path):
            os.remove(enc_file_path)

        if ret_dec_path:
            return dec_file_path
