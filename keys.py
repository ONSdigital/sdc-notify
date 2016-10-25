import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey, _RSAPrivateKey


def new_key():
    """ Generates a random RSA key pair. Key size is 4096 bits and the public exponent is 65537. """
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )


def read_private(filename, password):
    """ Reads a private key from filename in PEM format, using KEY_PASSWORD to recover the key. """
    with open(filename, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=password.encode("utf8"),
            backend=default_backend()
        )


def write_private(key, filename, password):
    """ Writes a private key to filename in PEM format, using KEY_PASSWORD to protect the key. """
    with open(filename, "wb") as key_file:
        key_file.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf8"))
        ))


def read_public(filename):
    """ Reads a public key from the given filename in PEM format. """
    with open(filename, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )


def write_public(key, filename):
    """ Writes a public key to the given filename in PEM format. """
    with open(filename, "wb") as key_file:
        key_file.write(key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def to_pem_string(key):
    """ Converts a public or private key to a PEM format string, suitable for passing to JWT calls.
     Don't use this method to store a private key. Call write_private(...) (and write_public(...) for consistency). """

    if type(key) is _RSAPrivateKey:
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("ascii")
    elif type(key) is _RSAPublicKey:
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("ascii")
    raise ValueError("Expecting a public or private key.")


if __name__ == '__main__':
    """ Generates a keypair, overwriting the one in the ./keys/ directory. """

    key_password = "Prototype"

    # Generate a random key pair:
    #private_key = new_key()
    #public_key = private_key.public_key()

    # Save the private key and check we can read it in again:
    #write_private(private_key, "key/key.pem", key_password)
    read_private("key/key.pem", key_password)

    # Save the public key and check we can read it in again:
    #write_public(public_key, "key/key.pub")
    print(to_pem_string(read_public("key/key.pub")))
