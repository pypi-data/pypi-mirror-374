# noinspection SpellCheckingInspection
"""
AssetRPC module for Evrmore CLI asset operations.

This class provides a high-level wrapper for asset-related commands
using `evrmore-cli`, including transfers and asset issuance functions.
"""

from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


# noinspection DuplicatedCode,SpellCheckingInspection,GrazieInspection
class AssetsRPC:
    """
    AssetRPC provides an interface for interacting with the Evrmore blockchain assets via the `evrmore-cli` command-line tool.

    This class wraps common asset-related RPC commands and parses their responses, allowing you to manage, query, and transfer assets on the Evrmore blockchain. It handles command construction, execution, and result parsing, with support for both mainnet and testnet modes.

    Attributes:
        cli_path (str): Path to the `evrmore-cli` binary.
        datadir (str): Path to the Evrmore node data directory.
        rpc_user (str): RPC authentication username.
        rpc_pass (str): RPC authentication password.
        testnet (bool): Run commands on testnet if True; mainnet otherwise.

    Example:
        rpc = AssetRPC(
            cli_path="/path/to/evrmore-cli",
            datadir="/path/to/data",
            rpc_user="user",
            rpc_pass="password",
            testnet=True
        )

        asset_info = rpc.getassetdata("ASSETNAME")

    Methods provide access to:
        - Checking if an address has a specified asset balance.
        - Querying asset metadata.
        - Getting burn addresses.
        - Retrieving cache information.
        - Calculating tolls for asset transactions.
        - Issuing, reissuing, transferring, and updating asset metadata.
        - Listing assets and balances.
        - Other asset operations supported by Evrmore CLI.
    """


    def __init__(self, cli_path, datadir, rpc_user, rpc_pass, testnet=True):
        """
        Initialize a new AssetRPC client instance with connection and authentication details.

        Parameters:
            cli_path (str): Full path to the `evrmore-cli` executable.
            datadir (str): Path to the Evrmore node's data directory.
            rpc_user (str): Username for RPC authentication.
            rpc_pass (str): Password for RPC authentication.`
            testnet (bool, optional): If True, use Evrmore testnet; uses mainnet by default.
        """

        self.cli_path = cli_path     # Path to the Evrmore CLI executable binary
        self.datadir = datadir       # Directory where Evrmore blockchain data is stored
        self.rpc_user = rpc_user     # Username for RPC authentication with the node
        self.rpc_pass = rpc_pass     # Password for RPC authentication with the node
        self.testnet = testnet       # Boolean indicating whether to use testnet mode


    def _build_command(self):
        """
        Create the base command-line argument list to invoke `evrmore-cli` with the current client configuration.

        Returns:
            list: Command-line arguments representing the base CLI call, including authentication and network mode.
        """

        # Build and return the base command-line argument list for Evrmore CLI,
        # using the stored configuration parameters from the instance
        return build_base_command(
            self.cli_path,   # Path to the Evrmore CLI executable
            self.datadir,    # Blockchain data directory
            self.rpc_user,   # RPC username for authentication
            self.rpc_pass,   # RPC password for authentication
            self.testnet     # Boolean to indicate testnet usage
        )


    def addresshasasset(self, address, asset_name, required_quantity=1):
        """
        Check whether a given address holds at least a specified quantity of a particular asset.

        Args:
            address (str): Address to query for asset balance.
            asset_name (str): Name of the asset to check the balance for.
            required_quantity (int or float, optional): The minimum quantity required. Defaults to 1.

        Returns:
            bool: True if the address holds at least the required quantity of the asset, False otherwise.

        """

        command = self._build_command() + [
            "listassetbalancesbyaddress",
            address
        ]

        try:
            # Execute the command and capture the output
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)

            # Parse the output JSON into a Python dictionary of asset balances
            balances = json.loads(result.stdout.strip())

            # Return True if the specified asset meets or exceeds required_quantity, else False
            return float(balances.get(asset_name, 0)) >= float(required_quantity)
        except Exception as e:
            # Print and handle any errors during execution or parsing
            print(f"Error checking asset balance: {e}")
            return False  # On error, treat as asset not present

    def getassetdata(self, asset_name):
        """
        Retrieve metadata for a given asset if it exists.

        Args:
            asset_name (str): The exact name of the asset to look up.

        Returns:
            dict | str:
                - On success: a dictionary of asset metadata (e.g., name, amount, units, reissuable flags,
                  optional IPFS/txid hashes, verifier string, toll settings, burn/remint totals, etc.).
                - If no output: "No data returned."
                - On error: "Error: <node stderr or exception message>"

        Examples:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/home/user/.evrmore-test/testnet1",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.getassetdata("ASSET_NAME")
        """
        import json
        from subprocess import run, PIPE

        command = self._build_command() + ["getassetdata", str(asset_name)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try to parse JSON to a Python dict; fall back to raw text if not JSON.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out

        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getburnaddresses(self):
        """
        Returns a dictionary of all burn addresses used by the Evrmore blockchain.

        Args:
            None

        Returns:
            dict | str:
                - On success: dictionary mapping nickname → burn address.
                - If the daemon returns non-JSON output, the raw string is returned.
                - On error: "Error: <message>" with stderr or exception text.

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> burn_addrs = rpc.getburnaddresses()
        """
        command = self._build_command() + ["getburnaddresses"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = result.stdout.strip()

            if not out:
                return "No data returned."

            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getcacheinfo(self):
        """
        Returns current node cache metrics (e.g., UTXO cache, asset maps, dirty cache estimates).

        Args:
            None

        Returns:
            list | str:
                - On success: a list (if the daemon returns JSON) with cache metric entries.
                - If the daemon returns non-JSON text, the raw string is returned.
                - On error: "Error: <message>" with stderr or exception text.

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> info = rpc.getcacheinfo()
        """
        command = self._build_command() + ["getcacheinfo"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."

            # Try to parse JSON first; if it fails, return raw text.
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getcalculatedtoll(
            self,
            asset_name: str | None = None,
            amount: int | float | str | None = None,
            change_amount: int | float | str | None = None,
            overwrite_toll_fee: int | float | str | None = None,
    ):
        """
        Calculate the toll for transferring an asset.

        Args:
            asset_name (str | None, optional): Asset name. Defaults to "".
            amount (int | float | str | None, optional): Amount being sent. Defaults to 100.
            change_amount (int | float | str | None, optional): Change amount. Defaults to 0.
            overwrite_toll_fee (int | float | str | None, optional): Explicit toll fee. Defaults to "".

        Returns:
            dict | str: Parsed JSON on success, raw string if non-JSON, or standardized error string.
        """
        # Convert None into daemon-expected defaults
        asset_name = "" if asset_name is None else str(asset_name)
        amount = "100" if amount is None else str(amount)
        change_amount = "0" if change_amount is None else str(change_amount)
        overwrite_toll_fee = "" if overwrite_toll_fee is None else str(overwrite_toll_fee)

        args = [
            "getcalculatedtoll",
            asset_name,
            amount,
            change_amount,
            overwrite_toll_fee,
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

    def getsnapshot(self, asset_name, block_height):
        """
        Get details for an asset snapshot taken at a specific block height.

        Args:
            asset_name (str): Asset name to inspect.
            block_height (int | str): Block height at which the snapshot was taken.

        Returns:
            dict | str:
                - On success: a dict (e.g., {"name": ..., "height": ..., "owners": [...]})
                  if the node returns JSON.
                - If the node returns plain text, the raw string is returned.
                - On error: "Error: <message>" with stderr or exception text.

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore",
            ...                 rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.getsnapshot("ASSET_NAME", 28546)
        """
        args = [
            "getsnapshot",
            str(asset_name),
            str(int(block_height)),
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

    def issue(
            self,
            asset_name,
            qty=None,
            to_address=None,
            change_address=None,
            units=None,
            reissuable=None,
            has_ipfs=None,
            ipfs_hash=None,
            permanent_ipfs_hash=None,
            toll_amount=None,
            toll_address=None,
            toll_amount_mutability=None,
            toll_address_mutability=None,
            remintable=None,
    ):
        """
        Issue a new asset, sub-asset, or unique asset.

        Args:
            asset_name (str): Unique asset name (e.g., "ASSET", "ASSET/SUB", or "ASSET#unique").
            qty (int | float | str | None): Quantity to issue (default 1 if omitted but a later arg is used).
            to_address (str | None): Destination address for the issued asset.
            change_address (str | None): Address to receive EVR change.
            units (int | None): Decimal precision (0–8). Defaults to 0 if omitted but later args are used.
            reissuable (bool | None): Whether future reissuance is allowed (default True).
            has_ipfs (bool | None): Attach IPFS/txid metadata (default False). If `ipfs_hash` is provided and
                this is None, it will be treated as True to keep parameters consistent.
            ipfs_hash (str | None): IPFS/txid hash (required if `has_ipfs` is True).
            permanent_ipfs_hash (str | None): Permanent IPFS/txid hash for the asset.
            toll_amount (int | float | str | None): Toll fee assigned to the asset (default 0).
            toll_address (str | None): Address to receive the toll fee (defaults per node if omitted).
            toll_amount_mutability (bool | None): Whether toll amount can be changed later (default False).
            toll_address_mutability (bool | None): Whether toll address can be changed later (default False).
            remintable (bool | None): Whether burned tokens can be reminted (default True).

        Returns:
            str: txid on success, "No data returned." if empty, or "Error: <message>" on failure.

        Example:
            >>> rpc.issue("ASSET_NAME", 1000, "myaddress", "changeaddress", 2, True)
        """
        import json
        from subprocess import run, PIPE

        args = ["issue", str(asset_name)]

        # If ipfs_hash is supplied but has_ipfs wasn't, force has_ipfs=True to align semantics/slots.
        if ipfs_hash is not None and has_ipfs is None:
            has_ipfs = True

        # Optional slots in exact order after asset_name.
        # Each entry: (kind, value, default_placeholder)
        # kind -> how we stringify placeholder: 'num', 'str', 'bool'
        option_spec = [
            ("num", qty, "1"),  # default 1
            ("str", to_address, ""),  # empty string placeholder
            ("str", change_address, ""),  # empty string placeholder
            ("num", (None if units is None else int(units)), "0"),  # default 0
            ("bool", reissuable, True),  # default True
            ("bool", has_ipfs, False),  # default False
            ("str", ipfs_hash, ""),  # empty string placeholder
            ("str", permanent_ipfs_hash, ""),  # empty string placeholder
            ("num", toll_amount, "0"),  # default 0
            ("str", toll_address, ""),  # empty string placeholder
            ("bool", toll_amount_mutability, False),  # default False
            ("bool", toll_address_mutability, False),  # default False
            ("bool", remintable, True),  # default True
        ]

        # Find the last provided index
        last_idx = -1
        for i, (_, val, _) in enumerate(option_spec):
            if val is not None:
                last_idx = i

        # Append placeholders/values up to last provided slot
        for i in range(last_idx + 1):
            kind, val, default_placeholder = option_spec[i]
            if val is None:
                # Insert typed placeholder
                if kind == "str":
                    args.append("")
                elif kind == "num":
                    args.append(str(default_placeholder))
                elif kind == "bool":
                    args.append("true" if bool(default_placeholder) else "false")
            else:
                # Insert actual value (stringify with correct type)
                if kind == "str":
                    args.append(str(val))
                elif kind == "num":
                    args.append(str(val))
                elif kind == "bool":
                    args.append("true" if bool(val) else "false")

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def issueunique(
            self,
            root_name,
            asset_tags,
            ipfs_hashes=None,
            to_address=None,
            change_address=None,
            permanent_ipfs_hashes=None,
            toll_address=None,
            toll_amount=None,
            toll_amount_mutability=None,
            toll_address_mutability=None,
    ):
        """
        Issue one or more **unique assets** under a given root asset.

        Args:
            root_name (str):
                Root asset you own (e.g., "MY_ASSET"). Each unique will be issued under this root.
            asset_tags (list[str] | tuple[str, ...]):
                Tags for each unique (e.g., ["ALPHA", "BETA"]). One asset is created per tag.
            ipfs_hashes (list[str] | tuple[str, ...] | None):
                Optional IPFS/txid hashes aligned to `asset_tags`. Default daemon behavior: empty list.
            to_address (str | None):
                Destination address for the uniques. Default daemon behavior: "" (node generates one).
            change_address (str | None):
                EVR change address. Default daemon behavior: "" (node generates one).
            permanent_ipfs_hashes (list[str] | tuple[str, ...] | None):
                Optional *permanent* IPFS/txid hashes aligned to `asset_tags`. Default: empty list.
            toll_address (str | None):
                Address to receive transfer tolls. Default daemon behavior: "" (use default toll address).
            toll_amount (int | float | str | None):
                Toll amount applied to the assets. Default daemon behavior: 0.
            toll_amount_mutability (bool | None):
                Whether toll amount can be changed in the future. Default daemon behavior: false.
            toll_address_mutability (bool | None):
                Whether toll address can be changed in the future. Default daemon behavior: false.

        Returns:
            str: On success, the transaction id (txid). On error, a standardized error string.

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> txid = rpc.issueunique("MY_ASSET", ["ALPHA", "BETA"])
        """
        # Required base
        args = [
            "issueunique",
            str(root_name),
            json.dumps(list(asset_tags)),  # CLI expects a JSON array
        ]

        # Determine if any optional argument was explicitly provided
        provided_flags = [
            ipfs_hashes is not None,
            to_address is not None,
            change_address is not None,
            permanent_ipfs_hashes is not None,
            toll_address is not None,
            toll_amount is not None,
            toll_amount_mutability is not None,
            toll_address_mutability is not None,
        ]
        last_idx = -1
        for i, f in enumerate(provided_flags):
            if f:
                last_idx = i

        if last_idx >= 0:
            # 1) ipfs_hashes (array) — default []
            if last_idx >= 0:
                if ipfs_hashes is None:
                    args.append("[]")
                else:
                    args.append(json.dumps(list(ipfs_hashes)) if not isinstance(ipfs_hashes, str) else ipfs_hashes)

            # 2) to_address (string) — default ""
            if last_idx >= 1:
                args.append("" if to_address is None else str(to_address))

            # 3) change_address (string) — default ""
            if last_idx >= 2:
                args.append("" if change_address is None else str(change_address))

            # 4) permanent_ipfs_hashes (array) — default []
            if last_idx >= 3:
                if permanent_ipfs_hashes is None:
                    args.append("[]")
                else:
                    args.append(
                        json.dumps(list(permanent_ipfs_hashes))
                        if not isinstance(permanent_ipfs_hashes, str)
                        else permanent_ipfs_hashes
                    )

            # 5) toll_address (string) — default ""
            if last_idx >= 4:
                args.append("" if toll_address is None else str(toll_address))

            # 6) toll_amount (number) — default 0
            if last_idx >= 5:
                args.append("0" if toll_amount is None else str(toll_amount))

            # 7) toll_amount_mutability (bool) — default false
            if last_idx >= 6:
                tam = False if toll_amount_mutability is None else bool(toll_amount_mutability)
                args.append("true" if tam else "false")

            # 8) toll_address_mutability (bool) — default false
            if last_idx >= 7:
                tdm = False if toll_address_mutability is None else bool(toll_address_mutability)
                args.append("true" if tdm else "false")

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else out
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaddressesbyasset(self, asset_name, onlytotal=None, count=None, start=None):
        """
        List owners of an asset (with balances) or return only the total owner count.

        Args:
            asset_name (str):
                The asset name to query.
            onlytotal (bool | None):
                If True, return just the total number of addresses holding the asset.
                If False/None, return a mapping of address → balance. (Default: False)
            count (int | None):
                Max number of results (cap 50,000). (Default: 50000)
            start (int | None):
                Offset to skip the first N results (negative = from the end). (Default: 0)

        Returns:
            dict | int | str:
                - dict[address] -> balance (when onlytotal is False/None)
                - int total count (when onlytotal is True)
                - or raw text on non-JSON daemon output
                - or "Error: ..." on failure

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> owners = rpc.listaddressesbyasset("ASSET_NAME", False, 100, 0)
        """
        # Base args
        args = ["listaddressesbyasset", str(asset_name)]

        # Determine how far we need to fill optional positional args
        provided = [onlytotal is not None, count is not None, start is not None]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # Slot 1: onlytotal (default false)
            if last_idx >= 0:
                ot = False if onlytotal is None else bool(onlytotal)
                args.append("true" if ot else "false")

            # Slot 2: count (default 50000)
            if last_idx >= 1:
                c = 50000 if count is None else int(count)
                args.append(str(c))

            # Slot 3: start (default 0)
            if last_idx >= 2:
                s = 0 if start is None else int(start)
                args.append(str(s))

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

    def listassetbalancesbyaddress(self, address, onlytotal=None, count=None, start=None):
        """
        Return all asset balances for a given address, or only the total number of assets.

        Args:
            address (str):
                Evrmore address to query.
            onlytotal (bool | None):
                If True, return just the total number of distinct assets held.
                If False/None, return a mapping of asset_name → quantity. (Default: False)
            count (int | None):
                Limit the number of returned assets (max 50,000). (Default: 50000)
            start (int | None):
                Skip the first N results (negative = skip from end). (Default: 0)

        Returns:
            dict | int | str:
                - dict[asset_name] -> quantity (when onlytotal is False/None)
                - int total count (when onlytotal is True)
                - or raw text on non-JSON output
                - or "Error: ..." on failure

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.listassetbalancesbyaddress("myaddress", False, 100, 0)
        """
        args = ["listassetbalancesbyaddress", str(address)]

        # Determine which optional slots must be filled (to preserve positional order).
        provided = [onlytotal is not None, count is not None, start is not None]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # Slot 1: onlytotal (default false)
            ot = False if onlytotal is None else bool(onlytotal)
            args.append("true" if ot else "false")

            # Slot 2: count (default 50000)
            if last_idx >= 1:
                c = 50000 if count is None else int(count)
                args.append(str(c))

            # Slot 3: start (default 0)
            if last_idx >= 2:
                s = 0 if start is None else int(start)
                args.append(str(s))

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

    def listassets(self, asset=None, verbose=None, count=None, start=None):
        """
        List asset names or (optionally) detailed metadata filtered by a pattern.

        Args:
            asset (str | None):
                Filter (exact name or prefix with '*'). Defaults to "*" (all) when needed for position.
            verbose (bool | None):
                If True, return a mapping of asset_name → metadata; if False/None, return a list of names.
            count (int | None):
                Max number of results. If omitted but a later arg is provided, a large default is used.
            start (int | None):
                Offset into the results (negative = count back from end). Defaults to 0 when needed.

        Returns:
            list | dict | str:
                - list[str] of asset names when verbose is False/None
                - dict[str, dict] of asset metadata when verbose is True
                - raw text if daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.listassets("ASSET*", True, 10, 0)
        """
        args = ["listassets"]

        # Figure out how many optional slots we must fill (to preserve positional order).
        provided = [asset is not None, verbose is not None, count is not None, start is not None]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # Slot 1: asset filter (default "*")
            args.append(str("*" if asset is None else asset))

            # Slot 2: verbose (default false)
            if last_idx >= 1:
                v = False if verbose is None else bool(verbose)
                args.append("true" if v else "false")

            # Slot 3: count (use a very large default if needed to represent "ALL")
            if last_idx >= 2:
                c = (2 ** 31 - 1) if count is None else int(count)
                args.append(str(c))

            # Slot 4: start (default 0)
            if last_idx >= 3:
                s = 0 if start is None else int(start)
                args.append(str(s))

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

    def listmyassets(self, asset=None, verbose=None, count=None, start=None, confs=None):
        """
        List assets owned by this wallet (optionally with outpoints).

        Args:
            asset (str | None):
                Filter (exact name or prefix with '*'). Defaults to "*" when needed for position.
            verbose (bool | None):
                If True, include outpoints; if False/None, return balances only.
            count (int | None):
                Max number of results. If omitted but a later arg is provided, a large default is used.
            start (int | None):
                Offset into the results (negative = count back from end). Defaults to 0 when needed.
            confs (int | None):
                Minimum confirmations required for results. Defaults to 0 when needed.

        Returns:
            dict | str:
                - dict of balances (and possibly outpoints) on success (parsed JSON)
                - raw text if daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.listmyassets("ASSET*", True, 10, 20, 1)
        """
        args = ["listmyassets"]

        provided = [
            asset is not None,
            verbose is not None,
            count is not None,
            start is not None,
            confs is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) asset (default "*")
            args.append(str("*" if asset is None else asset))

            # 2) verbose (default false)
            if last_idx >= 1:
                v = False if verbose is None else bool(verbose)
                args.append("true" if v else "false")

            # 3) count (use a very large default to represent "ALL")
            if last_idx >= 2:
                c = (2 ** 31 - 1) if count is None else int(count)
                args.append(str(c))

            # 4) start (default 0)
            if last_idx >= 3:
                s = 0 if start is None else int(start)
                args.append(str(s))

            # 5) confs (default 0)
            if last_idx >= 4:
                cf = 0 if confs is None else int(confs)
                args.append(str(cf))

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

    def purgesnapshot(self, asset_name, block_height):
        """
        Remove stored snapshot details for an asset at a specific block height.

        Args:
            asset_name (str):
                Asset name.
            block_height (int):
                Block height of the snapshot to purge.

        Returns:
            dict | str:
                - Parsed JSON object on success (e.g., {"name": "...", "height": ...}).
                - Raw text if the daemon returns non-JSON.
                - Or "Error: ..." on failure.

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.purgesnapshot("ASSET_NAME", 28546)
        """
        command = self._build_command() + [
            "purgesnapshot",
            str(asset_name),
            str(int(block_height)),
        ]

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

    def reissue(
            self,
            asset_name,
            qty,
            to_address,
            change_address=None,
            reissuable=None,
            new_units=None,
            new_ipfs=None,
            new_permanent_ipfs=None,
            change_toll_amount=None,
            new_toll_amount=None,
            new_toll_address=None,
            toll_amount_mutability=None,
            toll_address_mutability=None,
    ):
        """
        Reissue additional quantity of an existing asset you control (via the owner token).
        You may also update reissuable flag, display units, IPFS hashes, and toll settings.

        Args:
            asset_name (str): Asset to reissue.
            qty (int | str | float): Quantity to add.
            to_address (str): Destination address for the reissued amount.
            change_address (str | None): EVR change address. Defaults to "" (node chooses).
            reissuable (bool | None): Whether future reissuance remains allowed. Defaults to True.
            new_units (int | None): New display units; Defaults to -1 (no change).
            new_ipfs (str | None): New IPFS/txid metadata (RIP5). Defaults to "" (no change).
            new_permanent_ipfs (str | None): New permanent IPFS hash. Defaults to "" (no change).
            change_toll_amount (bool | None): Whether toll amount is being changed. Defaults to False.
            new_toll_amount (int | float | None): New toll amount. Defaults to 0.
            new_toll_address (str | None): New toll address. Defaults to "".
            toll_amount_mutability (bool | None): Future toll amount changes allowed. Defaults to True.
            toll_address_mutability (bool | None): Future toll address changes allowed. Defaults to True.

        Returns:
            dict | str:
                Parsed JSON on success (usually a txid string), or raw text if not JSON.
                On failure: "Error: <message>".

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.reissue("ASSET_NAME", 20, "to_address")
        """
        # Fill all positional params, converting None to RPC's expected defaults/placeholders.
        # Order per RPC help:
        # 1 asset_name, 2 qty, 3 to_address, 4 change_address,
        # 5 reissuable, 6 new_units, 7 new_ipfs, 8 new_permanent_ipfs,
        # 9 change_toll_amount, 10 new_toll_amount, 11 new_toll_address,
        # 12 toll_amount_mutability, 13 toll_address_mutability
        args = [
            "reissue",
            str(asset_name),
            str(qty),
            str(to_address),
            "" if change_address is None else str(change_address),
            "true" if (reissuable is None or bool(reissuable)) else "false",
            str(-1 if new_units is None else int(new_units)),
            "" if new_ipfs is None else str(new_ipfs),
            "" if new_permanent_ipfs is None else str(new_permanent_ipfs),
            "false" if (change_toll_amount is None) else ("true" if bool(change_toll_amount) else "false"),
            str(0 if new_toll_amount is None else new_toll_amount),
            "" if new_toll_address is None else str(new_toll_address),
            # Defaults for the two *mutability flags* are True per help
            "true" if (toll_amount_mutability is None or bool(toll_amount_mutability)) else "false",
            "true" if (toll_address_mutability is None or bool(toll_address_mutability)) else "false",
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

    def remint(
            self,
            asset_name,
            qty,
            to_address,
            change_address=None,
            update_remintable=None,
    ):
        """
        Remint previously burned units of an asset you control (owner token required).
        Optionally toggle whether future reminting is permitted.

        Args:
            asset_name (str): Asset to remint.
            qty (int | float | str): Amount to remint.
            to_address (str): Destination address for reminted units.
            change_address (str | None): EVR change address. Defaults to "" (node chooses).
            update_remintable (bool | None): Whether to update the asset's “remintable” flag.
                Defaults to True.

        Returns:
            dict | str:
                Parsed JSON on success (often a txid string), or raw text if not JSON.
                On failure: "Error: <message>".

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.remint("ASSET_NAME", 10, "to_address")
        """
        # RPC positional order:
        # 1 asset_name, 2 qty, 3 to_address, 4 change_address, 5 update_remintable
        args = [
            "remint",
            str(asset_name),
            str(qty),
            str(to_address),
            "" if change_address is None else str(change_address),
            "true" if (update_remintable is None or bool(update_remintable)) else "false",
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


    def transfer(
            self,
            asset_name,
            qty,
            to_address,
            message=None,
            expire_time=None,
            change_address=None,
            asset_change_address=None,
    ):
        """
        Transfer a quantity of an owned asset to a destination address.

        Args:
            asset_name (str): Asset name to send.
            qty (int | float | str): Quantity to transfer.
            to_address (str): Recipient Evrmore address.
            message (str | None): Optional IPFS/txid hash (RIP-5) to attach.
            expire_time (int | None): Optional UNIX timestamp when `message` expires.
            change_address (str | None): EVR change address ("" lets node choose).
            asset_change_address (str | None): Asset change address ("" lets node choose).

        Returns:
            dict | list | str:
                Parsed JSON on success (txid string or list), or raw text if not JSON.
                On failure: "Error: <message>".

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.transfer("ASSET_NAME", 20, "n2ReceiverAddress...")
        """
        # Positional order is strict; supply placeholders for omitted optionals.
        args = [
            "transfer",
            str(asset_name),
            str(qty),
            str(to_address),
            "" if message is None else str(message),
            "" if expire_time is None else str(int(expire_time)),
            "" if change_address is None else str(change_address),
            "" if asset_change_address is None else str(asset_change_address),
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

    def transferfromaddress(
            self,
            asset_name,
            from_address,
            qty,
            to_address,
            message=None,
            expire_time=None,
            evr_change_address=None,
            asset_change_address=None,
    ):
        """
        Transfer a quantity of an owned asset **from a specific address** to a destination.

        Args:
            asset_name (str): Asset name to send.
            from_address (str): Source address holding the asset UTXO(s).
            qty (int | float | str): Quantity to transfer.
            to_address (str): Recipient Evrmore address.
            message (str | None): Optional IPFS/txid hash (RIP-5) to attach.
            expire_time (int | None): Optional UNIX timestamp when `message` expires.
            evr_change_address (str | None): EVR change address ("" lets node choose).
            asset_change_address (str | None): Asset change address ("" lets node choose).

        Returns:
            dict | list | str:
                Parsed JSON on success (txid string or list), or raw text if not JSON.
                On failure: "Error: <message>".

        Example:
            >>> rpc = AssetsRPC(cli_path="evrmore-cli", datadir="/evrmore", rpc_user="user", rpc_pass="pass", testnet=True)
            >>> rpc.transferfromaddress("ASSET_NAME", "n2FromAddr...", 20, "n2ToAddr...")
        """
        # Positional order is strict; supply placeholders for omitted optionals.
        args = [
            "transferfromaddress",
            str(asset_name),
            str(from_address),
            str(qty),
            str(to_address),
            "" if message is None else str(message),
            str(0) if expire_time is None else str(int(expire_time)),
            "" if evr_change_address is None else str(evr_change_address),
            "" if asset_change_address is None else str(asset_change_address),
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

    def transferfromaddresses(
            self,
            asset_name,
            from_addresses,
            qty,
            to_address,
            message=None,
            expire_time=None,
            evr_change_address=None,
            asset_change_address=None,
    ):
        """
        Transfer a quantity of an owned asset **from multiple specific addresses** to one destination.

        Args:
            asset_name (str): Asset name to send.
            from_addresses (list[str]): One or more source addresses to draw asset inputs from.
            qty (int | float | str): Quantity to transfer.
            to_address (str): Recipient Evrmore address.
            message (str | None): Optional IPFS/txid hash (RIP-5) to attach.
            expire_time (int | None): Optional UNIX timestamp when `message` expires.
            evr_change_address (str | None): EVR change address ("" lets node choose).
            asset_change_address (str | None): Asset change address ("" lets node choose).

        Returns:
            dict | list | str:
                Parsed JSON on success (txid string or list), or raw text if not JSON.
                On failure: "Error: <message>".

        Example:
            >>> rpc.transferfromaddresses("ASSET_NAME", ["n2From1...", "n2From2..."], 20, "n2To...")
        """
        # RPC expects a JSON array string for from_addresses
        from_addrs_arg = json.dumps([str(a) for a in (from_addresses or [])])

        # Positional order is strict; supply placeholders for omitted optionals.
        args = [
            "transferfromaddresses",
            str(asset_name),
            from_addrs_arg,
            str(qty),
            str(to_address),
            "" if message is None else str(message),
            "" if expire_time is None else str(int(expire_time)),
            "" if evr_change_address is None else str(evr_change_address),
            "" if asset_change_address is None else str(asset_change_address),
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

    def updatemetadata(
            self,
            asset_name,
            change_address=None,
            ipfs_hash=None,
            permanent_ipfs=None,
            toll_address=None,
            change_toll_amount=None,
            toll_amount=None,
            toll_amount_mutability=None,
            toll_address_mutability=None,
    ):
        """
        Update on-chain metadata for an asset you own (owner token required).

        Args:
            asset_name (str): Asset to update.
            change_address (str | None): EVR change address. Default "" (node chooses).
            ipfs_hash (str | None): New IPFS/txid hash for metadata. Default "" (no change).
            permanent_ipfs (str | None): Permanent IPFS/txid hash. Default "" (unset). Irreversible once set.
            toll_address (str | None): Address to collect toll fees. Default "" (use default toll addr / no change).
            change_toll_amount (bool | None): Whether to change toll amount. Default False.
            toll_amount (int | float | None): New toll amount. Default -1 (no change).
            toll_amount_mutability (bool | None): Whether toll amount can be changed later. Default True.
            toll_address_mutability (bool | None): Whether toll address can be changed later. Default True.

        Returns:
            dict | list | str:
                Parsed JSON/primitive on success (often a txid string), or raw text if not JSON.
                On failure: "Error: <message>".

        Example:
            >>> rpc.updatemetadata("ASSET_NAME", "", "QmHash...", "", "tollAddr...", True, 10, True, False)
        """
        # Convert None -> RPC defaults and ensure all positional args are sent.
        change_address = "" if change_address is None else str(change_address)
        ipfs_hash = "" if ipfs_hash is None else str(ipfs_hash)
        permanent_ipfs = "" if permanent_ipfs is None else str(permanent_ipfs)
        toll_address = "" if toll_address is None else str(toll_address)
        change_toll_amount = False if change_toll_amount is None else bool(change_toll_amount)
        toll_amount = -1 if toll_amount is None else toll_amount
        toll_amount_mutability = True if toll_amount_mutability is None else bool(toll_amount_mutability)
        toll_address_mutability = True if toll_address_mutability is None else bool(toll_address_mutability)

        args = [
            "updatemetadata",
            str(asset_name),
            change_address,
            ipfs_hash,
            permanent_ipfs,
            toll_address,
            "true" if change_toll_amount else "false",
            str(toll_amount),
            "true" if toll_amount_mutability else "false",
            "true" if toll_address_mutability else "false",
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


