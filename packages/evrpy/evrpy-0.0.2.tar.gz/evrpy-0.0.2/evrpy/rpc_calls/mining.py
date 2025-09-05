from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json


class MiningRPC:

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

    def getblocktemplate(self, template_request=None):
        """
        Return data needed to construct a block to work on.

        Args:
            template_request (dict | None):
                Optional JSON-compatible dict with fields like:
                  - "mode": "template" | "proposal"
                  - "capabilities": [ ... ]
                  - "rules": [ ... ]
                Omit to use node defaults.

        Returns:
            dict | list | str:
                - parsed JSON (dict or list) on success when daemon returns JSON
                - raw text if daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc.getblocktemplate({"mode": "template", "capabilities": ["longpoll"], "rules": []})
        """
        args = ["getblocktemplate"]
        if template_request is not None:
            # Pass the JSON object as a single CLI argument
            try:
                args.append(json.dumps(template_request))
            except Exception as enc_err:
                return f"Error: Failed to encode template_request: {enc_err}".strip()

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

    def getevrprogpowhash(self, header_hash, mix_hash, nonce, height, target=None):
        """
        Compute the EvrProgPow hash for a block given its data.

        Args:
            header_hash (str): The ProgPow header hash the miner received.
            mix_hash (str):    The mix hash mined by the GPU miner.
            nonce (str):       Hex nonce for the block (e.g., "0x100000").
            height (int):      Block height for which the hash is computed.
            target (str | None, optional): Target threshold the hash must meet.

        Returns:
            dict | list | str:
                - Parsed JSON if daemon returns JSON
                - Raw text if non-JSON
                - Or "Error: ..." on failure

        Example:
            >>> rpc.getevrprogpowhash("header_hash", "mix_hash", "0x100000", 2456)
        """
        args = [
            "getevrprogpowhash",
            str(header_hash),
            str(mix_hash),
            str(nonce),
            str(int(height)),
        ]

        # Optional trailing arg: include only if explicitly provided
        if target is not None:
            args.append(str(target))

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

    def getmininginfo(self):
        """
        Return mining-related information.

        Returns:
            dict | list | str:
                - Parsed JSON object with mining info on success
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure

        Example:
            >>> rpc.getmininginfo()
        """
        command = self._build_command() + ["getmininginfo"]

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

    def getnetworkhashps(self, nblocks=None, height=None):
        """
        Return estimated network hashes per second.

        Args:
            nblocks (int | None):
                Number of blocks to average over. Default = 120.
                Use -1 for blocks since last difficulty change.
            height (int | None):
                Block height to estimate at. Default = -1 (latest).

        Returns:
            int | str:
                - Estimated hashes per second (numeric)
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure

        Example:
            >>> rpc.getnetworkhashps()
            >>> rpc.getnetworkhashps(240, -1)
        """
        args = ["getnetworkhashps"]

        provided = [
            nblocks is not None,
            height is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) nblocks (default = 120)
            args.append(str(120 if nblocks is None else nblocks))

            # 2) height (default = -1)
            if last_idx >= 1:
                args.append(str(-1 if height is None else height))

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return int(out)
            except ValueError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def pprpcsb(self, header_hash, mix_hash, nonce):
        """
        Submit a new block mined by evrprogpow GPU miner via RPC.

        Args:
            header_hash (str): The prog_pow header hash given to the GPU miner from this RPC client.
            mix_hash (str): The mix hash mined by the GPU miner via RPC.
            nonce (str): The nonce of the block that hashed the valid block.

        Returns:
            str:
                - Daemon response (often empty or success indicator)
                - Or "Error: ..." on failure

        Example:
            >>> rpc.pprpcsb("header_hash", "mix_hash", "100000")
        """
        args = self._build_command() + [
            "pprpcsb",
            str(header_hash),
            str(mix_hash),
            str(nonce),
        ]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def prioritisetransaction(self, txid, dummy=None, fee_delta=None):
        """
        Accept a transaction into mined blocks at a higher (or lower) priority.

        Args:
            txid (str): The transaction ID.
            dummy (float | None): API compatibility placeholder. Must be zero or null (deprecated).
            fee_delta (int | None): The fee delta in satoshis to add (positive) or subtract (negative).
                                    This affects block selection but is not actually paid.

        Returns:
            bool | str:
                - True if successful
                - raw text if daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc.prioritisetransaction("txid", 0.0, 10000)
        """
        provided = [
            txid is not None,
            dummy is not None,
            fee_delta is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        args = ["prioritisetransaction"]

        if last_idx >= 0:
            args.append(str(txid))

            if last_idx >= 1:
                d = 0.0 if dummy is None else dummy
                args.append(str(d))

            if last_idx >= 2:
                f = 0 if fee_delta is None else int(fee_delta)
                args.append(str(f))

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

    def submitblock(self, hexdata, dummy=None):
        """
        Attempts to submit a new block to the network.

        See BIP22 for full specification: https://en.bitcoin.it/wiki/BIP_0022

        Args:
            hexdata (str): Hex-encoded block data to submit.
            dummy (str | None, optional): Ignored. Only for compatibility with BIP22.

        Returns:
            dict | list | str:
                - parsed JSON (dict or list) on success
                - raw string if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - or "Error: ..." on failure

        Example:
            >>> rpc.submitblock("mydata")
        """
        args = ["submitblock", str(hexdata)]
        if dummy is not None:
            args.append(str(dummy))

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

