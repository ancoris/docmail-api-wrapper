def split_caps(key):
    """ splits a string using capital letters as separator
        eg split_caps('ExampleString') returns ['Example', 'String']
     """
    b = False
    lst = []
    x = 0
    for i, ch in enumerate(key):
        if i > 0 and ch.isupper():
            temp = key[x:i]
            if b and not temp.isupper():
                lst.append(key[x:i-1])
                x = i-1
            b = True
        elif b:
            lst.append(key[x:i-1])
            b = False
            x = i-1
    lst.append(key[x:])
    return lst