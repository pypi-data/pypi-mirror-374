from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

class KeyVaultEncryptor:
    def __init__(self, vault_url: str, key_name: str):
        self.vault_url = vault_url
        self.key_name = key_name
        self.credential = DefaultAzureCredential()

        # Create clients
        self.secret_client = SecretClient(vault_url=self.vault_url, credential=self.credential)
        self.key_client = KeyClient(vault_url=self.vault_url, credential=self.credential)

        # Load encryption key
        key = self.key_client.get_key(self.key_name)
        self.crypto_client = CryptographyClient(key, credential=self.credential)

    def get_encrypted_secret(self, secret_name: str) -> bytes:
        """
        Retrieve a secret from Key Vault and return its encrypted form.
        """
        # Retrieve the secret value
        secret = self.secret_client.get_secret(secret_name)

        # Encrypt the secret
        encrypt_result = self.crypto_client.encrypt(
            algorithm=EncryptionAlgorithm.rsa_oaep,
            plaintext=secret.value.encode()
        )

        return encrypt_result.ciphertext

    def decrypt_secret(self, encrypted_secret: bytes) -> str:
        """
        Decrypt an encrypted secret and return its plaintext value.
        """
        decrypt_result = self.crypto_client.decrypt(
            algorithm=EncryptionAlgorithm.rsa_oaep,
            ciphertext=encrypted_secret
        )
        return decrypt_result.plaintext.decode()
