from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class RestrictedRPC:

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

    def viewmyrestrictedaddresses(self):
        """
        View all addresses this wallet owns that have been restricted.

        Returns:
            list[dict] | dict | str:
                - List of restriction dictionaries on success (parsed JSON),
                - raw text if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.viewmyrestrictedaddresses()
            [
                {
                    "Address": "address1",
                    "Asset Name": "$ASSET1",
                    "Restricted": "25-09-04 12:00:00"
                },
                {
                    "Address": "address2",
                    "Asset Name": "$ASSET2",
                    "Derestricted": "25-09-03 09:30:00"
                }
            ]
        """
        command = self._build_command() + ["viewmyrestrictedaddresses"]

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

    def viewmytaggedaddresses(self):
        """
        View all addresses this wallet owns that have been tagged.

        Args:
            None

        Returns:
            list[dict] | dict | str:
                - Parsed JSON (list/dict) on success,
                - raw text if the daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.viewmytaggedaddresses()
            [
                {
                    "Address": "EVR...abc",
                    "Tag Name": "#CUSTOMER",
                    "Assigned": "25-09-04 12:00:00"
                },
                {
                    "Address": "EVR...xyz",
                    "Tag Name": "#ALLOWLIST",
                    "Removed": "25-09-03 09:30:00"
                }
            ]
        """
        command = self._build_command() + ["viewmytaggedaddresses"]

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

