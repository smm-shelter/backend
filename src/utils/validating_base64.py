import base64
import binascii


def is_valid_base64(value: str) -> bool:
    try:
        value = value.split(";base64,")[1]
        base64.decodebytes(value.encode("ascii"))
        return True
    except binascii.Error:
        return False
    except IndexError:
        return False
