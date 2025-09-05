from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class MessagesRPC:

    def __init__(self, cli_path, datadir, rpc_user, rpc_pass, testnet=True):
        """
                Initialize a new AssetRPC client instance with connection and authentication details.

                Parameters:
                    cli_path (str): Full path to the `evrmore-cli` executable.
                    datadir (str): Path to the Evrmore node's data directory.
                    rpc_user (str): Username for RPC authentication.
                    rpc_pass (str): Password for RPC authentication.
                    testnet (bool, optional): If True, use Evrmore testnet; uses mainnet by default.
                """

        # Store the path to the Evrmore CLI executable
        self.cli_path = cli_path

        # Store the directory where blockchain data is located
        self.datadir = datadir

        # Store the RPC username for authentication
        self.rpc_user = rpc_user

        # Store the RPC password for authentication
        self.rpc_pass = rpc_pass

        # Specify whether to use the testnet network
        self.testnet = testnet


    def _build_command(self):
        """
        Create the base command-line argument list to invoke `evrmore-cli` with the current client configuration.

        Returns:
            list: Command-line arguments representing the base CLI call, including authentication and network mode.
        """

        # Call the function to construct the base CLI command for Evrmore,
        # passing in all required configuration parameters from the instance
        return build_base_command(
            self.cli_path,  # Path to the Evrmore CLI binary
            self.datadir,  # Directory where blockchain data is stored
            self.rpc_user,  # RPC username
            self.rpc_pass,  # RPC password
            self.testnet  # Boolean: use testnet or not
        )

    def clearmessages(self):
        """
        Delete the current database of messages.

        Returns:
            str: Command output if successful, or "Error: <message>" if it fails.

        Example:
            >>> rpc.clearmessages()
            ''
        """
        command_list = self._build_command() + ["clearmessages"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def sendmessage(self, channel_name, ipfs_hash, expire_time=0):
        """
        Creates and broadcasts a message transaction to the network for a channel this wallet owns.

        Args:
            channel_name (str): Name of the channel to send a message with.
                                If a non-administrator asset name is given, the administrator '!' will be added automatically.
            ipfs_hash (str): The IPFS hash of the message.
            expire_time (int, optional): UTC timestamp of when the message expires.
                                         Use 0 (default) for no expiration.

        Returns:
            list | str:
                - list containing the transaction ID(s) on success (parsed JSON)
                - raw text if daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc.sendmessage("ASSET_NAME!", "QmTqu3Lk3gmTsQVtjU7rYYM37EAW4xNmbuEAp2Mjr4AV7E", 15863654)
            ['txid']
        """
        optional_spec = [expire_time]
        params = [channel_name, ipfs_hash] + [o if o is not None else 0 for o in optional_spec]

        command_list = self._build_command() + ["sendmessage"] + list(map(str, params))

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # handles list/dict output
            except json.JSONDecodeError:
                return out  # raw text fallback
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def subscribetochannel(self, channel_name):
        """
        Subscribe to a certain message channel.

        Args:
            channel_name (str): The channel name to subscribe to.
                                Must end with '!' or contain '~'.

        Returns:
            str: The result message from the subscription.

        Example:
            >>> rpc.subscribetochannel("ASSET_NAME!")
            ''
        """
        command_list = self._build_command() + ["subscribetochannel", channel_name]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def unsubscribefromchannel(self, channel_name):
        """
        Unsubscribe from a certain message channel.

        Args:
            channel_name (str): The channel name to unsubscribe from.
                                Must end with '!' or contain '~'.

        Returns:
            str: The result message from the unsubscription.

        Example:
            >>> rpc.unsubscribefromchannel("ASSET_NAME!")
            ''
        """
        command_list = self._build_command() + ["unsubscribefromchannel", channel_name]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def viewallmessagechannels(self):
        """
        View all message channels the wallet is subscribed to.

        Returns:
            list: A list of asset channel names.

        Example:
            >>> rpc.viewallmessagechannels()
            ['ASSET_NAME!', 'OTHER_ASSET~channel']
        """
        command_list = self._build_command() + ["viewallmessagechannels"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return result.stdout.strip().splitlines()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def viewallmessages(self):
        """
        View all messages that the wallet contains.

        Args:
            None

        Returns:
            dict | list | str:
                - parsed JSON (dict or list) on success when daemon returns JSON
                - raw text if daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc.viewallmessages()
        """
        args = ["viewallmessages"]
        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


