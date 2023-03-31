def add0x(data: str) -> str:
    if data.startswith('0x'):
        return data
    
    return '0x' + data

def padStart(string, length, pad='0'):
    if '0x' in string:
        return (pad * (length - len(string[2:]))) + string[2:]
    return (pad * (length - len(string))) + string[2:]