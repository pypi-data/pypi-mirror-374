from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class RewardsRPC:

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

        self.cli_path = cli_path
        self.datadir = datadir
        self.rpc_user = rpc_user
        self.rpc_pass = rpc_pass
        self.testnet = testnet

    def _build_command(self):
        """
        Create the base command-line argument list to invoke `evrmore-cli` with the current client configuration.

        Returns:
            list: Command-line arguments representing the base CLI call, including authentication and network mode.
        """

        return build_base_command(
            self.cli_path,
            self.datadir,
            self.rpc_user,
            self.rpc_pass,
            self.testnet
        )

    def cancelsnapshotrequest(self, asset_name, block_height):
        """
        Cancel a previously requested asset snapshot at a specific block height.

        Args:
            asset_name (str): The asset name for which the snapshot was scheduled.
            block_height (int): The block height at which the snapshot would be taken.

        Returns:
            dict | str:
                - Parsed JSON dict like {"request_status": "..."} on success,
                - raw text if the daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.cancelsnapshotrequest("TRONCO", 12345)
        """
        command = self._build_command() + ["cancelsnapshotrequest", str(asset_name), str(int(block_height))]

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

    def distributereward(
            self,
            asset_name,
            snapshot_height,
            distribution_asset_name,
            gross_distribution_amount,
            exception_addresses=None,
            change_address=None,
            dry_run=None,
    ):
        """
        Distribute an amount of an asset (or EVR) to all owners of another asset at a snapshot height.

        Args:
            asset_name (str): Asset whose owners receive the distribution.
            snapshot_height (int): Block height of the ownership snapshot.
            distribution_asset_name (str): The asset to distribute (or "EVR").
            gross_distribution_amount (int | float): Total amount to split among owners.
            exception_addresses (str | None): Comma-separated addresses to exclude. Defaults to "" when needed.
            change_address (str | None): Address to receive undistributed change. Defaults to "" when needed.
            dry_run (bool | None): If True, simulate only. Defaults to False when needed.

        Returns:
            dict | str:
                - Parsed JSON dict on success,
                - raw text if the daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.distributereward("TRONCO", 12345, "EVR", 1000)
        """
        args = [
            "distributereward",
            str(asset_name),
            str(int(snapshot_height)),
            str(distribution_asset_name),
            str(gross_distribution_amount),
        ]

        provided = [
            exception_addresses is not None,
            change_address is not None,
            dry_run is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 5) exception_addresses (default "")
            exc = "" if exception_addresses is None else str(exception_addresses)
            args.append(exc)

            # 6) change_address (default "")
            if last_idx >= 1:
                chg = "" if change_address is None else str(change_address)
                args.append(chg)

            # 7) dry_run (default false)
            if last_idx >= 2:
                dr = False if dry_run is None else bool(dry_run)
                args.append("true" if dr else "false")

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

    def getdistributestatus(
            self,
            asset_name,
            snapshot_height,
            distribution_asset_name,
            gross_distribution_amount,
            exception_addresses=None,
    ):
        """
        Get the status/details of a pending or completed distribution.

        Args:
            asset_name (str): Asset whose owners receive the distribution.
            snapshot_height (int): Block height of the ownership snapshot.
            distribution_asset_name (str): The asset to distribute (or "EVR").
            gross_distribution_amount (int | float): Total amount to split among owners.
            exception_addresses (str | None): Comma-separated addresses to exclude.
                                              Defaults to "" when needed for position.

        Returns:
            dict | str:
                - Parsed JSON dict on success,
                - raw text if the daemon returns non-JSON,
                - or "Error: ..." on failure.

        Examples:
            >>> rpc.getdistributestatus("TRONCO", 12345, "EVR", 1000)
            >>> rpc.getdistributestatus("PHATSTACKS", 12345, "DIVIDENDS", 1000,
            ...     "mwN7xC3...,n4Rf18e...")
        """
        args = [
            "getdistributestatus",
            str(asset_name),
            str(int(snapshot_height)),
            str(distribution_asset_name),
            str(gross_distribution_amount),
        ]

        # optional_spec pattern to preserve positional parsing
        provided = [exception_addresses is not None]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 5) exception_addresses (default "")
            exc = "" if exception_addresses is None else str(exception_addresses)
            args.append(exc)

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

    def getsnapshotrequest(self, asset_name, block_height):
        """
        Retrieve details of a specific snapshot request.

        Args:
            asset_name (str): The asset name for which the snapshot was requested.
            block_height (int): The block height of the snapshot.

        Returns:
            dict | str:
                - Parsed JSON dict on success,
                - raw text if the daemon returns non-JSON,
                - or "Error: ..." on failure.

        Examples:
            >>> rpc.getsnapshotrequest("TRONCO", 12345)
        """
        args = [
            "getsnapshotrequest",
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

    def listsnapshotrequests(self, asset_name=None, block_height=None):
        """
        List snapshot request details.

        Args:
            asset_name (str | None):
                Asset name to filter requests for.
                Defaults to "" (all assets) if not provided.
            block_height (int | None):
                Block height to filter requests for.
                Defaults to 0 (all heights) if not provided.

        Returns:
            list | dict | str:
                - Parsed JSON list/dict on success,
                - raw text if the daemon returns non-JSON,
                - or "Error: ..." on failure.

        Examples:
            >>> rpc.listsnapshotrequests()
            >>> rpc.listsnapshotrequests("TRONCO", 345333)
        """
        args = ["listsnapshotrequests"]

        if asset_name is not None:
            args.append(str(asset_name))
            if block_height is not None:
                args.append(str(int(block_height)))
        elif block_height is not None:
            # If asset_name is not specified but block_height is,
            # must pass "" as placeholder for asset_name.
            args.append("")
            args.append(str(int(block_height)))

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

    def requestsnapshot(self, asset_name, block_height):
        """
        Schedule a snapshot of the specified asset at the specified block height.

        Args:
            asset_name (str): The asset name for which the snapshot will be taken.
            block_height (int): The block height at which the snapshot will be taken.

        Returns:
            dict | str:
                - dict with the snapshot request status on success,
                - raw text if daemon returns non-JSON,
                - or "Error: ..." on failure.

        Examples:
            >>> rpc.requestsnapshot("TRONCO", 12345)
            >>> rpc.requestsnapshot("PHATSTACKS", 34987)
        """
        command = self._build_command() + [
            "requestsnapshot",
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

