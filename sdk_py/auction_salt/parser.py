from typing import Union

def getStartTime(salt: Union[int, str]) -> int:
    if isinstance(salt, int):
        val = int(hex(salt)[:10], 16)
    elif isinstance(salt, str):
        if salt.startswith('0x'):
            val = int(salt[:10], 16)
        else:
            val = int(hex(int(salt))[:10], 16)
    else:
        raise ValueError(f'Unsupported type: {type(salt)}')
    return val  

def getDuration(salt: Union[int, str]) -> int:
    if isinstance(salt, int):
        val = int('0x' + hex(salt)[10:16], 16)
    elif isinstance(salt, str):
        if salt.startswith('0x'):
            val = int('0x' + salt[10:16], 16)
        else:
            val = int('0x' + hex(int(salt))[10:16], 16)
    else:
        raise ValueError(f'Unsupported type: {type(salt)}')
    return val

def getInitialRateBump(salt: Union[int, str]) -> int:
    if isinstance(salt, int):
        val = int('0x' + hex(salt)[16:22], 16)
    elif isinstance(salt, str):
        if salt.startswith('0x'):
            val = int('0x' + salt[16:22], 16)
        else:
            val = int('0x' + hex(int(salt))[16:22], 16)
    else:
        raise ValueError(f'Unsupported type: {type(salt)}')
    return val

def getFee(salt: Union[int, str]) -> int:
    if isinstance(salt, int):
        val = int('0x' + hex(salt)[22:30], 16)
    elif isinstance(salt, str):
        if salt.startswith('0x'):
            val = int('0x' + salt[22:30], 16)
        else:
            val = int('0x' + hex(int(salt))[22:30], 16)
    else:
        raise ValueError(f'Unsupported type: {type(salt)}')
    return val

def getSalt(salt: Union[int, str]) -> int:
    if isinstance(salt, int):
        val = int('0x' + hex(salt)[30:], 16)
    elif isinstance(salt, str):
        if salt.startswith('0x'):
            val = int('0x' + salt[30:], 16)
        else:
            val = int('0x' + hex(int(salt))[30:], 16)
    else:
        raise ValueError(f'Unsupported type: {type(salt)}')
    return val
