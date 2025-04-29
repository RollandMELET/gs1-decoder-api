AI_TABLE = {
    '00': ('SSCC', 18, False),
    '01': ('GTIN', 14, False),
    '10': ('Batch/Lot', 20, True),
    '17': ('ExpirationDate', 6, False),
    '21': ('SerialNumber', 20, True),
    '90': ('InternalInformation', 30, True),
}

def parse_gs1(data, verbose=False):
    parsed = []
    simple_parsed = {}
    i = 0
    while i < len(data):
        ai = data[i:i+2]
        if ai not in AI_TABLE:
            ai = data[i:i+3]
            if ai not in AI_TABLE:
                ai = data[i:i+4]
                if ai not in AI_TABLE:
                    break

        name, length, is_variable = AI_TABLE[ai]
        i += len(ai)

        if is_variable:
            fnc1_pos = data.find('\x1d', i)
            if fnc1_pos == -1:
                value = data[i:]
                i = len(data)
            else:
                value = data[i:fnc1_pos]
                i = fnc1_pos + 1
        else:
            value = data[i:i+length]
            i += length

        if verbose:
            parsed.append({"ai": ai, "name": name, "value": value})
        else:
            simple_parsed[name] = value

    return parsed if verbose else simple_parsed
