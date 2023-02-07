import base64
import hashlib
import json
import zlib
from uuid import UUID

import time
import datetime
from calendar import EPOCH
from werkzeug.http import parse_date

from flask.json.tag import TaggedJSONSerializer
from itsdangerous import BadSignature, TimestampSigner, URLSafeTimedSerializer

from vial import DEFAULT_SALT


class LegacyTimestampSigner(TimestampSigner):
    def get_timestamp(self) -> int:
        return int(time.time() - EPOCH)

    def get_timestamp_to_datetime(self, ts):
        return datetime.utcfromtimestamp(ts + EPOCH)


def verify(
    value: str, secret: str, legacy: bool = False, salt: str = DEFAULT_SALT
) -> bool:
    """
    Verifies if a given value matches the signed signature
    :param value: Session cookie string to verify
    :param secret: Secret key
    :param salt: Salt (default: 'cookie-session')
    :param legacy: Should the legacy timestamp generator be used?
    :return: True if the secret key is valid
    """
    if not isinstance(secret, (bytes, str)):
        raise ValueError(
            f"Secret must be a string-type (bytes, str) and received "
            f"{type(secret).__name__}. To fix this, either add quotes to the "
            f"secret {secret} or use the --no-literal-eval argument."
        )

    try:
        get_serializer(secret, legacy, salt).loads(value)
    except BadSignature:
        return False

    return True


def decode(value: str) -> dict:
    """
    Flask uses a custom JSON serializer so they can encode other data types.
    This code is based on theirs, but we cast everything to strings because
    we don't need them to survive a round trip if we're just decoding them.

    Sourced from : https://www.kirsle.net/wizards/flask-session.cgi#source
    """
    try:
        compressed = False
        payload = value

        if payload.startswith("."):
            compressed = True
            payload = payload[1:]

        data = payload.split(".")[0]

        data = base64.b64decode(data)

        if compressed:
            data = zlib.decompress(data)

        data = data.decode("utf-8")

    except Exception as e:
        raise ValueError(
            f"Failed to decode cookie, are you sure this was a Flask session cookie? {e}"
        )

    def hook(obj):
        if len(obj) != 1:
            return obj

        key, value = next(iter(obj.items()))

        match key:
            case " t":
                return tuple(value)
            case " u":
                return UUID(value)
            case " b":
                return base64.b64decode(value)
            case " d":
                return parse_date(value)

        return obj

    try:
        return json.loads(data, object_hook=hook)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to decode cookie, are you sure this was a Flask session cookie? {e}"
        )


def sign(
    value: dict, secret: str, legacy: bool = False, salt: str = DEFAULT_SALT
) -> str | bytes:
    """
    Signs a custom session value with a known secret
    :param value: Raw Python object (generally a dictionary) to serialize
    :param secret: secret key
    :param salt: Salt (default: 'cookie-session')
    :param legacy: Wether or not to use the legacy timestamp generator
    :return: Encoded string
    """
    if not isinstance(secret, (bytes, str)):
        raise ValueError(
            f"Secret must be a string-type (bytes, str) and received {type(secret).__name__!r}."
        )

    return get_serializer(secret, legacy, salt).dumps(value)


def get_serializer(
    secret: str, legacy: bool = False, salt: str = DEFAULT_SALT
) -> URLSafeTimedSerializer:
    """
    Returns a URLSafeTimedSerializer instance
    :param secret: Secret key
    :param salt: Salt (default: 'cookie-session')
    :param legacy: Should the legacy timestamp generator be used?
    :return: URLSafeTimedSerializer instance (Flask session serializer)
    """
    signer = LegacyTimestampSigner if legacy else TimestampSigner

    return URLSafeTimedSerializer(
        secret,
        salt=salt,
        serializer=TaggedJSONSerializer(),
        signer=signer,
        signer_kwargs=dict(key_derivation="hmac", digest_method=hashlib.sha1),
    )
