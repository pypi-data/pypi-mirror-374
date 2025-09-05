from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class UtilRPC:

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

    def createmultisig(self, nrequired, keys):
        """
        Create a multi-signature address with n signatures of m keys required.

        Args:
            nrequired (int): The number of required signatures out of the provided keys.
            keys (list[str]): A list of Evrmore addresses or hex-encoded public keys.

        Returns:
            dict | str:
                - dict with 'address' and 'redeemScript' on success,
                - raw text if daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.createmultisig(2, [
            ...     "16sSauSf5pF2UkUwvKGq4qjNRzBZYqgEL5",
            ...     "171sgjn4YtPu27adkKGrdDwzRTxnRkBfKV"
            ... ])
            {'address': 'multisigaddress', 'redeemScript': 'script'}
        """
        command = self._build_command() + [
            "createmultisig",
            str(int(nrequired)),
            json.dumps(keys),
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

    def estimatefee(self, nblocks):
        """
        Estimate the approximate fee per kilobyte needed for a transaction to begin
        confirmation within a certain number of blocks.

        Note:
            DEPRECATED. Use `estimatesmartfee` for more intelligent estimates.

        Args:
            nblocks (int): The target number of blocks for confirmation.

        Returns:
            float | str:
                - estimated fee per kilobyte (numeric),
                - raw text if daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.estimatefee(6)
            0.00012345
        """
        command = self._build_command() + ["estimatefee", str(int(nblocks))]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return float(out)
            except ValueError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def estimatesmartfee(self, conf_target, estimate_mode=None):
        """
        Estimate the approximate fee per kilobyte needed for a transaction to begin
        confirmation within a target number of blocks.

        Uses virtual transaction size as defined in BIP 141 (witness data is discounted).

        Args:
            conf_target (int): Confirmation target in blocks (1–1008).
            estimate_mode (str, optional): Fee estimate mode.
                Must be one of:
                    "UNSET" (defaults to CONSERVATIVE)
                    "ECONOMICAL"
                    "CONSERVATIVE"
                Default: None (server uses CONSERVATIVE).

        Returns:
            dict | str:
                - dict with fields like "feerate", "errors", "blocks" (parsed JSON) on success,
                - raw text if daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.estimatesmartfee(6)
            {'feerate': 0.00012, 'blocks': 6}
        """
        command = self._build_command() + ["estimatesmartfee", str(int(conf_target))]
        if estimate_mode is not None:
            command.append(str(estimate_mode))

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

    def signmessagewithprivkey(self, privkey, message):
        """
        Sign a message with the private key of an address.

        Args:
            privkey (str): The private key to sign the message with.
            message (str): The message to create a signature of.

        Returns:
            str:
                - The base64-encoded signature string on success,
                - raw text if daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.signmessagewithprivkey("cUcf7t...", "my message")
            "H5aKc8K..."
        """
        command = self._build_command() + ["signmessagewithprivkey", str(privkey), str(message)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def validateaddress(self, address):
        """
        Return information about the given Evrmore address.

        Args:
            address (str): The Evrmore address to validate.

        Returns:
            dict | str:
                - Parsed JSON dict with validation details on success,
                - raw text if the daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.validateaddress("1PSSGeFHDnKNxiEyFrD1wcEaHr9hrQDDWc")
        """
        command = self._build_command() + ["validateaddress", str(address)]

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

    def verifymessage(self, address, signature, message):
        """
        Verify a signed message.

        Args:
            address (str): Evrmore address used for the signature.
            signature (str): Base64-encoded signature.
            message (str): The signed message.

        Returns:
            bool | str:
                - True/False on success (parsed from daemon output),
                - raw text if the daemon returns non-JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.verifymessage("1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX", "signature", "my message")
        """
        command = self._build_command() + ["verifymessage", str(address), str(signature), str(message)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                # "true"/"false" is valid JSON and will parse to bool
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

