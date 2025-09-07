import sys, json
from importlib.resources import files


from handsoff import modules

def main():

    settings = {}
    SETTINGS = files("handsoff") / "settings.json"
    with SETTINGS.open("r", encoding="utf-8") as file:
        settings: dict[str, str] = json.load(file)

    cmd = modules.Commands(settings)

    # print(sys.argv)

    if sys.argv[1] == "set":
        params = modules.split(sys.argv)
        cmd.set_params(params)
        with SETTINGS.open("w", encoding="utf-8") as file: # type: ignore
            params = cmd.get_params()
            json.dump(params, file, ensure_ascii=False, indent=4)
        return
    
    if sys.argv[1] == "params":
        params = cmd.get_params()
        for key, val in params.items():
            print(f"{key} : {val}")
        return

    elif sys.argv[1] == "pull":
        cmd.pull()
        print("Pull complete!")
        return

    elif sys.argv[1] == "push":
        cmd.push()
        print("Push complete!")
        return
    
    elif sys.argv[1] == "help" or sys.argv[1] == "-h":
        print("Handsoff commands list")
        print("handsoff")
        print(" set : set a parameter within command, You need parameters at least HOST, USER, from, to (like ssh or scp)")
        print(" pull : execute pull command by running scp command.")
        print(" push : execute push command by running scp command.")

    
    else:
        raise ValueError("Not valid command! handsoff help to get available command list.")




if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()