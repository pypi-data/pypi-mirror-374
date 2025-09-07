import subprocess

class Commands:
    def __init__(self, settings: dict[str, str] | None = None) -> None:
        self.valid_params = {"host", "port", "user", "from", "to", "pem"}

        self.params: dict[str, str] = {}
        self.params["port"] = "22"

        if settings:
            for key, value in settings.items():
                if key in self.valid_params:
                    self.params[key] = value

    def set_params(self, params: dict[str, str]) -> None:
        for key, value in params.items():
            if key not in self.valid_params:
                raise ValueError(f"Not valid parameter: {key}")
            self.params[key] = value
    
    def get_params(self) -> dict[str, str] :
        return self.params

    def command_not_valid(self) -> bool:
        required = ["host", "user", "from", "to"]
        return not all(self.params.get(k) for k in required)

    def pull(self) -> None:
        if self.command_not_valid():
            raise ConnectionAbortedError(
                "Not enough parameters! You need at least HOST, USER, from, to."
            )

        options = "-r -o StrictHostKeyChecking=no"
        if pem := self.params.get("pem"):
            options += f" -i {pem}"

        subprocess.run(
            f"scp {options} -P {self.params['port']} {self.params['user']}@{self.params['host']}:{self.params['from']} {self.params['to']}",
            # stderr=subprocess.DEVNULL,
            shell=True
        )

    def push(self) -> None:
        if self.command_not_valid():
            raise ConnectionAbortedError(
                "Not enough parameters! You need at least HOST, USER, from, to."
            )

        options = "-r -o StrictHostKeyChecking=no"
        if pem := self.params.get("pem"):
            options += f" -i {pem}"

        subprocess.run(
            f"scp {options} -P {self.params['port']} {self.params['from']} {self.params['user']}@{self.params['host']}:{self.params['to']}",
            # stderr=subprocess.DEVNULL,
            shell=True
        )
