import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey, _RSAPrivateKey

# Use configured password if available:
KEY_PASSWORD = "Prototype"
if "KEY_PASSWORD" in os.environ:
    KEY_PASSWORD = os.environ["KEY_PASSWORD"]
    print("Info: using configured password")
else:
    print("Warn: using default key password.")


def new_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=4094,
        backend=default_backend()
    )


def read_private(filename, password):
    with open(filename, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=password.encode("utf8"),
            backend=default_backend()
        )


def write_private(key, filename, password):
    with open(filename, "wb") as key_file:
        key_file.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf8"))
        ))


def read_public(filename):
    with open(filename, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )


def write_public(key, filename):
    with open(filename, "wb") as key_file:
        key_file.write(key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def to_pem_string(key):
    if type(key) is _RSAPrivateKey:
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("ascii")
    elif type(key) is _RSAPublicKey:
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("ascii")
    raise ValueError("Expecting a public or private key.")


if __name__ == '__main__':
    private_key = new_key()
    public_key = private_key.public_key()

    write_private(private_key, "generated_keys/key.pem", KEY_PASSWORD)
    print(to_pem_string(read_private("generated_keys/key.pem", KEY_PASSWORD)))

    write_public(public_key, "generated_keys/key.pub")
    print(to_pem_string(read_public("generated_keys/key.pub")))
