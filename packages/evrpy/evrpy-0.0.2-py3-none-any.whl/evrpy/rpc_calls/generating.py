from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class GeneratingRPC:

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

    def generate(self, nblocks, maxtries=None):
        """
        Mine up to `nblocks` blocks immediately to an address in the wallet.

        Args:
            nblocks (int):
                Number of blocks to generate immediately.
            maxtries (int, optional):
                Maximum number of iterations to try. Defaults to 1,000,000.

        Returns:
            list:
                A list of block hashes generated.
                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.generate(11)
            ['0000000000000000000a7d3...', '0000000000000000001b8c4...']
        """
        optional_spec = [maxtries]

        command_list = self._build_command() + ["generate", str(nblocks)]
        for arg in optional_spec:
            command_list.append(str(arg) if arg is not None else "")

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout.strip())
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def generatetoaddress(self, nblocks, address, maxtries=None):
        """
        Mine blocks immediately to a specified address.

        Args:
            nblocks (int):
                Number of blocks to generate immediately.
            address (str):
                The Evrmore address that will receive the newly generated coins.
            maxtries (int, optional):
                Maximum number of iterations to try. Defaults to 1,000,000.

        Returns:
            list:
                A list of block hashes generated.
                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.generatetoaddress(11, "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
            ['0000000000000000000a7d3...', '0000000000000000001b8c4...']
        """
        optional_spec = [maxtries]

        command_list = self._build_command() + ["generatetoaddress", str(nblocks), str(address)]
        for arg in optional_spec:
            command_list.append(str(arg) if arg is not None else "")

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout.strip())
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getgenerate(self):
        """
        Check if the server is set to generate coins.

        Returns:
            bool:
                True if the server is set to generate coins, False otherwise.
                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.getgenerate()
            False
        """
        command_list = self._build_command() + ["getgenerate"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout.strip())
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def setgenerate(self, generate: bool, genproclimit: int = None):
        """
        Set coin generation on or off, with optional processor limit.

        Args:
            generate (bool): True to enable generation, False to disable.
            genproclimit (int, optional): Number of processors to use. -1 for unlimited. Defaults to None.

        Returns:
            str: Command output if successful, or "Error: <message>" if it fails.

        Example:
            >>> rpc.setgenerate(True, 1)
            'Generation enabled with 1 processor'
            >>> rpc.setgenerate(False)
            'Generation disabled'
        """
        optional_spec = [genproclimit]
        args = [str(generate).lower()] + [str(arg) if arg is not None else "" for arg in optional_spec]

        command_list = self._build_command() + ["setgenerate"] + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


