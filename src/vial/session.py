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


def sign(
    value: dict, secret: str, legacy: bool = False, salt: str = DEFAULT_SALT
) -> str:
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
