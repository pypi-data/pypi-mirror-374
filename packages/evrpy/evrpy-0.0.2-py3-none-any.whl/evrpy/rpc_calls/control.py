from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class ControlRPC:

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

    def getinfo(self):
        """
        Get general state info about the Evrmore node.

        Note: This command is **deprecated** and may be removed in future versions.

        Returns:
            dict:
                A dictionary with node state information such as version, protocol version,
                wallet balance, block count, network details, difficulty, and any errors.
                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.getinfo()
        """
        command = self._build_command() + ["getinfo"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return json.loads(out)
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getmemoryinfo(self, mode=None):
        """
        Get information about memory usage from the Evrmore node.

        Args:
            mode (str, optional):
                Determines the type of information returned.
                  - "stats" (default): General statistics about memory usage.
                  - "mallocinfo": Returns an XML string describing low-level heap state.

        Returns:
            dict or str:
                - If `mode="stats"`, returns a dictionary with memory statistics.
                - If `mode="mallocinfo"`, returns an XML string describing heap state.
                - Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.getmemoryinfo("stats")
            >>> rpc.getmemoryinfo("mallocinfo")
        """
        command = self._build_command() + ["getmemoryinfo"]

        if mode is not None:
            command.append(str(mode))

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getrpcinfo(self):
        """
        Get details about the active RPC server and currently running commands.

        Returns:
            dict:
                A dictionary containing details of the RPC server, including:
                  - "active_commands" (list): Information about all active commands.
                    Each entry includes:
                      - "method" (str): The RPC command name.
                      - "duration" (int): The running time in microseconds.

                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.getrpcinfo()
        """
        command = self._build_command() + ["getrpcinfo"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads((result.stdout or "").strip())
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def help(self, command=None):
        """
        List all available RPC commands, or get help text for a specific command.

        Args:
            command (str, optional):
                The name of the RPC command to get detailed help for.
                If omitted, returns a list of all available commands.

        Returns:
            str:
                Help text as a string. If no command is provided, returns a list of all commands.
                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.help()
            >>> rpc.help("getblock")
        """
        command_list = self._build_command() + ["help"]
        if command is not None:
            command_list.append(str(command))

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def stop(self):
        """
        Stop the Evrmore server.

        This will safely shut down the running Evrmore daemon.

        Args:
            None

        Returns:
            str:
                Confirmation message from the server if the shutdown was initiated successfully.
                Returns "Error: <message>" if the command fails.

        Example:
            >>> rpc.stop()
        """
        command_list = self._build_command() + ["stop"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def uptime(self):
        """
        Return the total uptime of the Evrmore server in dd:hh:mm:ss format.

        Executes the `uptime` RPC command via the Evrmore CLI. The command returns the number
        of seconds the Evrmore node has been running. This function converts that into a
        human-readable `dd:hh:mm:ss` string.

        Returns:
            str: Uptime formatted as "dd:hh:mm:ss".

            On failure, returns:
                - {"error": "No uptime received."}
                - {"error": <exception message>} if the subprocess fails
                - {"error": "Non-integer output", "raw": <raw output>} if the CLI returns non-numeric text

        Example:
            >>> rpc = EvrmoreRPC(cli_path="evrmore-cli", datadir="/home/aethyn/.evrmore-test/testnet1", rpc_user="neubtrino_testnet", rpc_pass="pass_testnet", testnet=True)
            >>> uptime_val = rpc.uptime()
            >>> isinstance(uptime_val, str)
            True
            >>> len(uptime_val.split(":")) == 4 or "error" in uptime_val
            True
        """

        def seconds_to_dhms(seconds):
            """Convert seconds to dd:hh:mm:ss format with leading zeros."""
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{days:02}:{hours:02}:{minutes:02}:{secs:02}"

        # Build CLI command to query uptime
        command = self._build_command() + ["uptime"]

        try:
            # Execute command and capture output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            if result.stdout:
                try:
                    # Parse output to int and format as dd:hh:mm:ss
                    seconds = int(result.stdout.strip())
                    return seconds_to_dhms(seconds)
                except ValueError:
                    return {"error": "Non-integer output", "raw": result.stdout.strip()}
            else:
                return {"error": "No uptime received."}
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

