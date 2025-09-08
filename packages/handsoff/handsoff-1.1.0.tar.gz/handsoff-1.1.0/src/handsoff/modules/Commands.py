import subprocess, dotenv, os

class Commands:
    def __init__(self, settings: dict[str, str] | None = None) -> None:
        self.valid_params = {"host", "port", "user", "server", "client", "pem", "env"}

        self.params: dict[str, str] = {}

        if settings:
            for key, value in settings.items():
                if key in self.valid_params:
                    self.params[key] = value

    def set_params(self, params: dict[str, str] = {}) -> None:
        """
        - self : Command object.
        - params : parameters, it requires at least host, port, user, server, client.
        """

        for key, value in params.items():
            if key not in self.valid_params:
                raise ValueError(f"Not valid parameter: {key}")
            self.params[key] = value
    
    def get_params(self) -> dict[str, str] :
        return self.params

    def command_not_valid(self) -> bool:
        required = ["host", "user", "server", "client"]
        return not all(self.params.get(k) for k in required)

    def pull(self, client: str = "", server: str = "") -> None:

        if self.params.get("env"):
            dotenv.load_dotenv(self.params["env"])

            for key in self.valid_params:
                value = os.getenv(key.upper())
                if not (value is None or self.params.get(key, False)):
                    self.params[key] = value

        if self.command_not_valid():
            raise ConnectionAbortedError(
                "Not enough parameters! You need at least HOST, USER, server, client."
            )

        options = "-r -o StrictHostKeyChecking=no"
        if pem := self.params.get("pem"):
            options += f" -i {pem}"

        subprocess.run(
            f"scp {options} \
                -P {self.params['port']} \
                    {self.params['user']}@{self.params['host']}:{server or self.params['server']} \
                    {client or self.params['client']}",
            # stderr=subprocess.DEVNULL,
            shell=True
        )

    def push(self, client: str = "", server: str = "") -> None:

        if self.params.get("env"):
            dotenv.load_dotenv(self.params["env"])

            for key in self.valid_params:
                value = os.getenv(key.upper())
                if not (value is None or self.params.get(key, False)):
                    self.params[key] = value
        
        if self.command_not_valid():
            raise ConnectionAbortedError(
                "Not enough parameters! You need at least HOST, USER, server, client."
            )

        options = "-r -o StrictHostKeyChecking=no"
        if pem := self.params.get("pem"):
            options += f" -i {pem}"

        subprocess.run(
            f"scp {options} \
                -P {self.params['port']} \
                    {client or self.params['client']} \
                    {self.params['user']}@{self.params['host']}:{server or self.params['server']}",
            # stderr=subprocess.DEVNULL,
            shell=True
        )
