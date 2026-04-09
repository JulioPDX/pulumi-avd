import pyeapi
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)


class EosConfigProvider(ResourceProvider):
    def _apply_config(self, host, username, password, config_text):
        """
        Connect to EOS and apply config using config replace.
        """
        # Create a connection to the switch
        connection = pyeapi.connect(
            transport="https",
            host=host,
            username=username,
            password=password,
            return_node=True,
        )

        # Use config replace via session
        # First, create a unique session name
        import time

        session_name = f"pulumi-replace-{int(time.time())}"

        # Start a config session
        connection.config([f"configure session {session_name}"])

        # Rollback to clean slate (removes all config)
        connection.config(
            [f"configure session {session_name}", "rollback clean-config"]
        )

        # pyeapi expects a list of commands, so we split the AVD text file
        commands = [line.strip() for line in config_text.splitlines() if line.strip()]

        # Apply the new configuration in the session
        try:
            # Build session config commands
            session_commands = [f"configure session {session_name}"] + commands

            # Apply config to session
            connection.config(session_commands)

            # Commit the session (this replaces the running config)
            connection.config([f"configure session {session_name}", "commit"])

        except Exception as e:
            # If anything fails, abort the session
            try:
                connection.config(
                    [f"configure session {session_name}", "abort"], format="text"
                )
            except Exception:
                pass
            raise e

    def diff(self, id: str, olds: dict, news: dict) -> DiffResult:
        """Tells Pulumi if the AVD config has changed since the last run."""
        # Compare config text stored in Pulumi's state (olds)
        # vs the new AVD file (news)
        changed = olds.get("config_text") != news.get("config_text")
        return DiffResult(changes=changed)

    def create(self, props: dict) -> CreateResult:
        """First time pushing config to this switch."""
        self._apply_config(
            props["host"], props["username"], props["password"], props["config_text"]
        )
        # The 'id' tells Pulumi how to track this resource in its state file
        return CreateResult(id_=props["host"], outs=props)

    def update(self, id: str, olds: dict, news: dict) -> UpdateResult:
        """When AVD generates a new config, this updates the switch."""
        self._apply_config(
            news["host"], news["username"], news["password"], news["config_text"]
        )
        return UpdateResult(outs=news)


# This is the actual Pulumi Resource class you will call in your main program
class EosDeviceConfig(Resource):
    def __init__(
        self,
        name: str,
        host: str,
        username: str,
        password: str,
        config_text: str,
        opts=None,
    ):
        super().__init__(
            EosConfigProvider(),
            name,
            {
                "host": host,
                "username": username,
                "password": password,
                "config_text": config_text,
            },
            opts,
        )
