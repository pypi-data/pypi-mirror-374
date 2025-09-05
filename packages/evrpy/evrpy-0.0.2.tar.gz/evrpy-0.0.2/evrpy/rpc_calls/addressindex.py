from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class AddressindexRPC:
    """
    A client for interacting with the Evrmore node's address index RPC commands via the `evrmore-cli` command-line interface.

    This class provides functions for querying indexed blockchain data by address, such as balance, UTXO sets, mempool data,
    and transaction IDs associated with given addresses. It is designed to work with an Evrmore node that has address index
    functionality enabled.

    Attributes:
        cli_path (str): Path to the `evrmore-cli` binary.
        datadir (str): Directory containing the Evrmore blockchain data.
        rpc_user (str): RPC username for node authentication.
        rpc_pass (str): RPC password for node authentication.
        testnet (bool): If True, connects to Evrmore testnet instead of mainnet.

    Typical usage example:
        rpc = AddressindexRPC(
            cli_path="/usr/bin/evrmore-cli",
            datadir="/home/user/.evrmore",
            rpc_user="rpcusername",
            rpc_pass="rpcpassword",
            testnet=True
        )
        balance = rpc.getaddressbalance("EVRaddress")
    """

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
            self.cli_path,   # Path to the Evrmore CLI binary
            self.datadir,    # Directory where blockchain data is stored
            self.rpc_user,   # RPC username
            self.rpc_pass,   # RPC password
            self.testnet     # Boolean: use testnet or not
        )

    def getaddressbalance(self, addresses, include_assets=False):
        """
        Returns the balance for one or more addresses (requires addressindex).


        Args:
            addresses (str | list[str] | dict):
                - Single base58check address string, OR
                - List of base58check addresses, OR
                - Dict of the form {"addresses": [...]}.
            include_assets (bool, optional):
                If True, expanded result includes asset balances.
                Default is False (returns only EVR summary).

        Returns:
            dict | list[dict] | str:
                - If include_assets=False:
                  {"balance": "<satoshis>", "received": "<satoshis>"}
                - If include_assets=True:
                  [{"assetName": "EVR"|"ASSET", "balance": "<satoshis>", "received": "<satoshis>"}, ...]
                - If unexpected shape: raw string.
                - If no output: "No data returned."
                - On error: "Error: <stderr or exception>"

        Example:
            >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                       rpc_user="user", rpc_pass="pass", testnet=True)
            >>> result = rpc.getaddressbalance("n3pUp4uT58hTtATHGvmkBsGP9tzMn8ZAQs")
        """
        # Shape addresses into the JSON object required by RPC
        if isinstance(addresses, dict):
            payload = addresses
        elif isinstance(addresses, str):
            payload = {"addresses": [addresses]}
        else:
            payload = {"addresses": list(addresses)}

        # Build base command
        command = self._build_command() + ["getaddressbalance", json.dumps(payload)]

        # Append includeAssets if requested
        if include_assets:
            command.append("true")

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            try:
                parsed = json.loads(out)
                return parsed
            except json.JSONDecodeError:
                # fallback: plain text / line-based
                if "\n" in out:
                    return [line.strip() for line in out.splitlines() if line.strip()]
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


    def getaddressdeltas(self, addresses, start=None, end=None, chain_info=None, asset_name=None):
        """
        Return all balance/asset deltas for the given address list (addressindex must be enabled).

        Args:
            addresses (list[str]): One or more base58check addresses.
            start (int | None): Start block height (inclusive).
            end (int | None): End block height (inclusive).
            chain_info (bool | None): Include chain info in results (only applied when both
                `start` and `end` are provided).
            asset_name (str | None): Limit deltas to a particular asset (use e.g. "EVR" for EVR).

        Returns:
            list | dict | str: Parsed JSON result on success, "No data returned." if empty,
            or "Error: <message>" on failure.

        Example:
            >>> rpc.getaddressdeltas(
            ...     ["12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"],
            ...     start=100000, end=101000, chain_info=True
            ... )
        """

        if not addresses or not isinstance(addresses, (list, tuple)):
            return 'Error: "addresses" must be a non-empty list of strings'

        payload = {"addresses": [str(a) for a in addresses]}

        # Optional height window
        if start is not None:
            payload["start"] = int(start)
        if end is not None:
            payload["end"] = int(end)

        # chainInfo is only meaningful if both start and end are set
        if (start is not None) and (end is not None) and (chain_info is not None):
            payload["chainInfo"] = bool(chain_info)

        # Optional asset filter
        if asset_name is not None:
            payload["assetName"] = str(asset_name)

        args = [
            "getaddressdeltas",
            json.dumps(payload, separators=(",", ":")),
        ]
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


    def getaddressmempool(self, addresses, include_assets=None):
        """
        Returns all mempool deltas for the given address(es).
        (Requires addressindex to be enabled.)


        Args:
            addresses (list): List of base58check-encoded addresses.
            include_assets (bool | None, optional): If True, return an expanded result
                that includes asset deltas.

        Returns:
            list | str:
                - On success: a list of mempool delta objects (parsed from JSON).
                - If daemon returns plain text: that text.
                - On error: "Error: <node stderr or exception message>"

        Example:
            >>> rpc = AddressindexRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                       rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.getaddressmempool(["12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"])
            >>> rpc.getaddressmempool(["12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"], include_assets=True)
        """
        try:
            # Build positional args exactly like the CLI expects:
            # 1) JSON object: {"addresses": [...]}
            # 2) Optional boolean: includeAssets
            addr_obj = {"addresses": list(addresses)}
            args = [
                "getaddressmempool",
                json.dumps(addr_obj),
            ]

            if include_assets is not None:
                args.append("true" if include_assets else "false")

            command = self._build_command() + args

            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try to parse JSON; if it isn't JSON, return the raw text.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaddresstxids(self, addresses, start=None, end=None, include_assets=None):
        """
        Return transaction IDs involving the given address(es) (addressindex must be enabled).

        Args:
            addresses (list[str]): One or more base58check addresses.
            start (int | None): Optional start block height.
            end (int | None): Optional end block height.
            include_assets (bool | None): If True, return an expanded result including asset txs.

        Returns:
            list | str:
                - Parsed JSON list of txids (or expanded objects when include_assets=True) on success.
                - "No data returned." if the node returns empty stdout.
                - "Error: <message>" on failure.

        Example:
            >>> rpc.getaddresstxids(
            ...     ["12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"],
            ...     start=100000, end=101000, include_assets=True
            ... )
        """

        # Basic validation to avoid confusing node errors
        if not addresses or not isinstance(addresses, (list, tuple)):
            return 'Error: "addresses" must be a non-empty list of strings'

        # Required payload
        payload = {"addresses": [str(a) for a in addresses]}

        # Optional fields (apply only when provided)
        optional_spec = [
            ("start", start, int),
            ("end", end, int),
        ]
        for key, value, caster in optional_spec:
            if value is not None:
                try:
                    payload[key] = caster(value)
                except Exception:
                    payload[key] = str(value)

        args = [
            "getaddresstxids",
            json.dumps(payload, separators=(",", ":")),
        ]

        # Optional second positional param
        if include_assets is not None:
            args.append("true" if bool(include_assets) else "false")

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

    def getaddressutxos(
            self,
            addresses: list[str],
            chain_info: bool = False,
            asset_name: str = "",
    ):
        """
        Return all unspent outputs for one or more addresses (addressindex required).

        Args:
            addresses (list[str]): Base58check addresses to query.
            chain_info (bool, optional): Include chain info in results. Defaults to False.
            asset_name (str, optional): Specific asset name to filter by; use "" for EVR, "*" for all assets.
                Defaults to "".

        Returns:
            list | dict | str: Parsed JSON (list of UTXOs or object with chain info), raw text if non-JSON,
            or standardized error string on failure.

        Example:
            >>> rpc.getaddressutxos(["12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"], chain_info=True, asset_name="MY_ASSET")
        """
        # Build the single JSON argument the daemon expects; always include keys to avoid ambiguity.
        payload = {
            "addresses": [str(a) for a in addresses],
            "chainInfo": bool(chain_info),
            "assetName": str(asset_name),  # "" for EVR, "*" for all, or a specific asset
        }

        args = ["getaddressutxos", json.dumps(payload)]
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


