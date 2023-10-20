from cryptography.fernet import Fernet


class CryptoService:
    """Сервис для шифрования пароля."""

    def __init__(self, secret_key: str):
        self.cipher_suite = Fernet(secret_key.encode())

    def encrypt_password(self, password: str) -> str:
        """Зашифровка пароля."""
        encrypted_text = self.cipher_suite.encrypt(password.encode())
        return encrypted_text.decode()

    def decrypt_password(self, encrypted_password: str) -> str:
        """Расшифровка пароля."""
        decrypted_text = self.cipher_suite.decrypt(encrypted_password.encode())
        return decrypted_text.decode()
