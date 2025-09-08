import os, sys, json

from handsoff import modules

def main():

    settings = {}
    SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
    
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        settings: dict[str, str] = json.load(file)

    cmd = modules.Commands(settings)

    # print(sys.argv)

    if sys.argv[1] == "set":
        params = modules.split(sys.argv)
        cmd.set_params(params)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as file: # type: ignore
            params = cmd.get_params()
            json.dump(params, file, ensure_ascii=False, indent=4)
        return
    
    if sys.argv[1] == "params":
        params = cmd.get_params()
        for key, val in params.items():
            print(f"{key} : {val}")
        return

    elif sys.argv[1] == "pull":
        if len(sys.argv) > 4:
            raise ValueError("This command requires at most 4 attributes!")
        
        cmd.pull(*sys.argv[2:])
        print("Pull complete!")
        return

    elif sys.argv[1] == "push":
        if len(sys.argv) > 4:
            raise ValueError("This command requires at most 4 attributes!")
        
        cmd.push(*sys.argv[2:])
        print("Push complete!")
        return
    
    elif sys.argv[1] == "help" or sys.argv[1] == "-h":
        print("Handsoff commands list")
        print("handsoff")
        print(" set : set a parameter within command, You need parameters at least HOST, USER, server, client (like ssh or scp)")
        print(" pull : execute pull command by running scp command.")
        print(" push : execute push command by running scp command.")

    
    else:
        raise ValueError("Not valid command! handsoff help to get available command list.")




if __name__ == "__main__":
    main()
