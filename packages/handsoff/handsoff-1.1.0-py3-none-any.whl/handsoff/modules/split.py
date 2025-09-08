def split(commands: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for elem in commands[2:]:
        if '=' not in elem:
            continue
        key, value = elem.split('=', 1)
        params[key] = value
    return params
    