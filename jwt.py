import os
import json
from jose import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from keys import read_private, read_public, to_pem_string

JWT_ALGORITHM = "RS256"
KEY_PASSWORD = None

private_key = None
public_key = None


def key_password():
    """ Lazily gets the configured key password (if available) or a default key password for development. """
    global KEY_PASSWORD

    if KEY_PASSWORD is None:
        # Use configured password if available:
        KEY_PASSWORD = "Prototype"
        if "KEY_PASSWORD" in os.environ:
            KEY_PASSWORD = os.environ["KEY_PASSWORD"]
            print("Info: using configured password")
        else:
            print("Warn: using default key password.")

    return KEY_PASSWORD


def encode(data):
    return jwt.encode(data, private_pem(), algorithm=JWT_ALGORITHM)


def decode(token):
    return jwt.decode(token, public_pem(), algorithms=JWT_ALGORITHM)


def private_pem():
    """ Loads the private key and returns it as a string in PEM format """
    global private_key

    if private_key is None:
        filename = "key/key.pem"
        key = read_private(filename, key_password())
        private_key = to_pem_string(key)

    return private_key


def public_pem():
    """ Loads the public key and returns it as a string in PEM format """
    global public_key

    if public_key is None:

        if "CLIENT_PUBLIC_KEY" in os.environ:
            # Deserialise the key from the configured value
            pem = os.environ["CLIENT_PUBLIC_KEY"]
            key = serialization.load_pem_public_key(
                pem,
                backend=default_backend()
            )
        else:
            # Load the saved key
            filename = "key/key.pub"
            key = read_public(filename)

        public_key = to_pem_string(key)

    return public_key


def main():
    data = {"key": "value"}
    print(json.dumps(data))

    token = encode(data)
    print(token)

    recovered = decode(token)
    print(json.dumps(recovered))


if __name__ == "__main__":
    main()
