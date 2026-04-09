import pulumi
from pulumi.dynamic import Resource, ResourceProvider, CreateResult, UpdateResult, DiffResult
import pyeapi

class EosConfigProvider(ResourceProvider):
    def _apply_config(self, host, username, password, config_text):
        """Helper method to connect to EOS and apply config via pyeapi."""
        # Create a connection to the switch
        connection = pyeapi.connect(
            transport='https',
            host=host, 
            username=username, 
            password=password, 
            return_node=True
        )
        
        # pyeapi expects a list of commands, so we split the AVD text file
        commands = [line.strip() for line in config_text.splitlines() if line.strip()]
        
        # Push the configuration to the running-config
        connection.config(commands)

    def diff(self, id: str, olds: dict, news: dict) -> DiffResult:
        """Tells Pulumi if the AVD config has changed since the last run."""
        # Compare the config text stored in Pulumi's state (olds) vs the new AVD file (news)
        changed = olds.get("config_text") != news.get("config_text")
        return DiffResult(changes=changed)

    def create(self, props: dict) -> CreateResult:
        """First time pushing config to this switch."""
        self._apply_config(props['host'], props['username'], props['password'], props['config_text'])
        # The 'id' tells Pulumi how to track this resource in its state file
        return CreateResult(id_=props['host'], outs=props)

    def update(self, id: str, olds: dict, news: dict) -> UpdateResult:
        """When AVD generates a new config, this updates the switch."""
        self._apply_config(news['host'], news['username'], news['password'], news['config_text'])
        return UpdateResult(outs=news)

# This is the actual Pulumi Resource class you will call in your main program
class EosDeviceConfig(Resource):
    def __init__(self, name: str, host: str, username: str, password: str, config_text: str, opts=None):
        super().__init__(EosConfigProvider(), name, {
            'host': host,
            'username': username,
            'password': password,
            'config_text': config_text,
        }, opts)
