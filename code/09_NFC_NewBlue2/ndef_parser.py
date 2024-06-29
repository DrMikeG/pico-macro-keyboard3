def parse_uid(uid):
    """
    Parse the UID bytes and return a string representation.

    :param uid: The UID bytes.
    :return: The string representation of the UID.
    """
    return ":".join([hex(byte)[2:].zfill(2) for byte in uid])