import random


def is_valid_account_number(account_number):
    """
    check if given account number is valid
    :param account_number:
    :return: bool
    """

    if len(str(account_number)) != 42:
        return False

    #try:
        #bytes.fromhex(account_number)
    #except Exception:
        #return False
    if not str(account_number).startswith('0x'):
        return False

    return True
