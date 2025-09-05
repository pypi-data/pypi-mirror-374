from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class NetworkRPC:

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

    def addnode(self, node, command):
        """
        Attempts to add or remove a node from the addnode list, or try connecting once.

        Nodes added with addnode (or -connect) are protected from DoS disconnection
        and are not required to be full nodes/support SegWit (though such peers will not
        be synced from).

        Args:
            node (str): The node address (see getpeerinfo for nodes).
            command (str): One of:
                - "add" to add a node to the list
                - "remove" to remove a node from the list
                - "onetry" to try a connection once

        Returns:
            dict | list | str:
                - parsed JSON (dict or list) on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.addnode("192.168.0.6:8819", "onetry")
        """
        args = ["addnode", str(node), str(command)]
        command_list = self._build_command() + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def clearbanned(self):
        """
        Clear all banned IPs.

        Returns:
            dict | list | str:
                - parsed JSON (dict or list) on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.clearbanned()
        """
        args = ["clearbanned"]
        command_list = self._build_command() + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def disconnectnode(self, address=None, nodeid=None):
        """
        Immediately disconnect from the specified peer node.

        Strictly one out of 'address' and 'nodeid' can be provided to identify the node.

        Args:
            address (str | None):
                The IP address/port of the node. Use "" if specifying by nodeid.
            nodeid (int | None):
                The node ID (see getpeerinfo). Use with address="" or alone.

        Returns:
            dict | list | str:
                - parsed JSON (dict or list) on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.disconnectnode("192.168.0.6:8819")
            >>> rpc.disconnectnode("", 1)
        """
        args = ["disconnectnode"]
        optional_spec = [address, nodeid]

        for o in optional_spec:
            if o is not None:
                args.append(str(o))

        command_list = self._build_command() + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaddednodeinfo(self, node=None):
        """
        Returns information about the given added node, or all added nodes.
        (Note: onetry addnodes are not listed here.)

        Args:
            node (str | None):
                If provided, return information about this specific node.
                If None, information on all added nodes is returned.

        Returns:
            list | dict | str:
                - list or dict (parsed JSON) on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.getaddednodeinfo("192.168.0.201")
            >>> rpc.getaddednodeinfo()
        """
        args = ["getaddednodeinfo"]

        if node is not None:
            args.append(str(node))

        command_list = self._build_command() + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getconnectioncount(self):
        """
        Returns the number of connections to other nodes.

        Returns:
            int | str:
                - integer connection count on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.getconnectioncount()
            8
        """
        command_list = self._build_command() + ["getconnectioncount"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return int(out)
            except ValueError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getnettotals(self):
        """
        Returns information about network traffic, including bytes in, bytes out, and current time.

        Returns:
            dict | str:
                - dict with keys like "totalbytesrecv", "totalbytessent", "timemillis", "uploadtarget" on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.getnettotals()
            {
                "totalbytesrecv": 123456,
                "totalbytessent": 654321,
                "timemillis": 1672531200000,
                "uploadtarget": {
                    "timeframe": 86400,
                    "target": 0,
                    "target_reached": False,
                    "serve_historical_blocks": True,
                    "bytes_left_in_cycle": 0,
                    "time_left_in_cycle": 0
                }
            }
        """
        command_list = self._build_command() + ["getnettotals"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getnetworkinfo(self):
        """
        Returns an object containing various state info regarding P2P networking.

        Returns:
            dict | str:
                - dict with keys like "version", "subversion", "protocolversion", "connections", etc. on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.getnetworkinfo()
            {
                "version": 2000000,
                "subversion": "/Evrmore:2.0.0/",
                "protocolversion": 70015,
                "localservices": "000000000000040d",
                "localrelay": True,
                "timeoffset": 0,
                "connections": 8,
                "networkactive": True,
                "networks": [
                    {
                        "name": "ipv4",
                        "limited": False,
                        "reachable": True,
                        "proxy": "",
                        "proxy_randomize_credentials": False
                    }
                ],
                "relayfee": 0.00001000,
                "incrementalfee": 0.00001000,
                "localaddresses": [],
                "warnings": ""
            }
        """
        command_list = self._build_command() + ["getnetworkinfo"]

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getpeerinfo(self):
        """
        Return data about each connected peer.

        Returns:
            list | str:
                - list of peer objects on success (parsed JSON)
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.getpeerinfo()
        """
        command = self._build_command() + ["getpeerinfo"]

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

    def listbanned(self):
        """
        List all banned IPs/Subnets.

        Returns:
            list | str:
                - list of banned IP/subnet entries on success (parsed JSON)
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.listbanned()
        """
        command = self._build_command() + ["listbanned"]

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

    def ping(self):
        """
        Requests that a ping be sent to all other nodes, to measure ping time.

        Results are reflected in `getpeerinfo` under the fields `pingtime` and `pingwait`.

        Returns:
            str:
                - Empty string "" on success (daemon does not return JSON here, only an ack)
                - raw string if daemon produces other stdout
                - or "Error: ..." on failure

        Example:
            >>> rpc.ping()
            ''
        """
        command = self._build_command() + ["ping"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def setban(self, subnet, command, bantime=None, absolute=None):
        """
        Attempts to add or remove an IP/Subnet from the banned list.

        Args:
            subnet (str):
                The IP/Subnet (optionally with netmask, default /32 for single IP).
            command (str):
                'add' to add an IP/Subnet, 'remove' to remove.
            bantime (int | None, optional):
                Ban duration in seconds. 0 or None means default 24h (overridden by -bantime).
            absolute (bool | None, optional):
                If True, bantime is treated as an absolute UNIX timestamp.

        Returns:
            str | dict:
                - "" or daemon response string if successful
                - dict if JSON is returned
                - "Error: ..." on failure

        Example:
            >>> rpc.setban("192.168.0.6", "add", 86400)
            ''
        """
        args = ["setban", str(subnet), str(command)]

        if bantime is not None:
            args.append(str(int(bantime)))
            if absolute is not None:
                args.append("true" if absolute else "false")

        command_list = self._build_command() + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return ""
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def setnetworkactive(self, state):
        """
        Disable or enable all P2P network activity.

        Args:
            state (bool):
                True to enable networking, False to disable.

        Returns:
            str | dict:
                - Daemon response if available (empty string on success)
                - Parsed JSON if returned
                - "Error: ..." on failure

        Example:
            >>> rpc.setnetworkactive(True)
            ''
        """
        args = ["setnetworkactive", "true" if state else "false"]

        command_list = self._build_command() + args

        try:
            result = run(command_list, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return ""
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


