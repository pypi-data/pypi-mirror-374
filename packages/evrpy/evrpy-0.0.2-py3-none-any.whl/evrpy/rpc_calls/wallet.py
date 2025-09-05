from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json
from decimal import Decimal




class WalletRPC:

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

    def abandontransaction(self, txid):
        """
        Mark an in-wallet transaction as abandoned.

        This will mark the transaction and all its in-wallet descendants as abandoned,
        allowing their inputs to be respent. It can only be used for transactions that:
        - are not included in a block,
        - are not in the mempool,
        - and are not already conflicted or abandoned.

        Args:
            txid (str): The transaction ID to abandon.

        Returns:
            str:
                - Empty string on success (daemon returns no data),
                - raw text if daemon outputs something,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.abandontransaction("1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d")
        """
        command = self._build_command() + ["abandontransaction", str(txid)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def abortrescan(self):
        """
        Stop the current wallet rescan.

        Typically used to halt a rescan triggered by commands like `importprivkey`.

        Returns:
            str:
                - Empty string on success (daemon returns no data),
                - raw text if daemon outputs something,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.abortrescan()
        """
        command = self._build_command() + ["abortrescan"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def addmultisigaddress(self, nrequired, keys, account=""):
        """
        Add an nrequired-to-sign multisignature address to the wallet.

        Each key must be a Evrmore address or a hex-encoded public key.
        Optionally, an account can be specified (deprecated).

        Args:
            nrequired (int): The number of required signatures out of the n keys or addresses.
            keys (list[str]): A list of Evrmore addresses or hex-encoded public keys.
            account (str, optional): Deprecated. An account to assign the address to. Default is "".

        Returns:
            str | dict:
                - string Evrmore address associated with the keys,
                - dict if the daemon returns structured output,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.addmultisigaddress(2, ["16sSauSf5pF2UkUwvKGq4qjNRzBZYqgEL5", "171sgjn4YtPu27adkKGrdDwzRTxnRkBfKV"])
            'address'
        """
        args = ["addmultisigaddress", str(nrequired), json.dumps(keys)]
        if account != "":
            args.append(str(account))

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

    def addwitnessaddress(self, address):
        """
        Add a witness address for a script (pubkey or redeemscript known by the wallet).

        Args:
            address (str): An address known to the wallet.

        Returns:
            str | dict:
                - The new witness address (string) on success,
                - Parsed JSON dict if daemon returns structured output,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.addwitnessaddress("myKnownAddress")
            'witnessAddress'
        """
        args = self._build_command() + ["addwitnessaddress", str(address)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def backupwallet(self, destination):
        """
        Safely copies the current wallet file to a destination, which can be a directory or a full path.

        Args:
            destination (str): The destination directory or file path for the wallet backup.

        Returns:
            str | dict:
                - Success message or destination path (string),
                - Parsed JSON dict if daemon returns structured output,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.backupwallet("backup.dat")
            'backup.dat'
        """
        args = self._build_command() + ["backupwallet", str(destination)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def dumpprivkey(self, address):
        """
        Reveals the private key corresponding to a given Evrmore address.

        Args:
            address (str): The Evrmore address for which to retrieve the private key.

        Returns:
            str | dict:
                - The private key as a string on success,
                - Parsed JSON dict if daemon returns structured output,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.dumpprivkey("myaddress")
            'L1aW4aubDFB7yfras2S1mN3bqg9w7r7sM5J1mMZZF3y8gV4z3xkQ'
        """
        args = self._build_command() + ["dumpprivkey", str(address)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def dumpwallet(self, filename):
        """
        Dumps all wallet keys in a human-readable format to a server-side file.
        This does not allow overwriting existing files.

        Args:
            filename (str): The filename with path (absolute or relative to evrmored).

        Returns:
            dict | str:
                - dict with "filename" if successful,
                - raw string if daemon returns plain text,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.dumpwallet("test")
            {'filename': '/home/user/.evrmore/test'}
        """
        args = self._build_command() + ["dumpwallet", str(filename)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def encryptwallet(self, passphrase):
        """
        Encrypts the wallet with the given passphrase. This is only for first-time encryption.
        After this, any call that interacts with private keys (e.g., send, sign) will require
        unlocking the wallet using `walletpassphrase`, followed by `walletlock`.

        Note:
            This call will **shutdown the server** after encryption.
            If the wallet is already encrypted, use `walletpassphrasechange` instead.

        Args:
            passphrase (str): The passphrase to encrypt the wallet with. Must be at least 1 character.

        Returns:
            str:
                - Response from the daemon (usually a message about server shutdown),
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.encryptwallet("my pass phrase")
            "wallet encrypted; Evrmore server stopping, restart to run with encrypted wallet"
        """
        args = self._build_command() + ["encryptwallet", str(passphrase)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return out if out else "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaccount(self, address):
        """
        (DEPRECATED) Returns the account associated with the given address.

        Args:
            address (str): The Evrmore address for account lookup.

        Returns:
            str:
                - The account name associated with the address,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.getaccount("1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX")
            "myaccount"
        """
        args = self._build_command() + ["getaccount", str(address)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return out if out else "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaccountaddress(self, account=""):
        """
        (DEPRECATED) Returns the current Evrmore address for receiving payments to this account.

        Args:
            account (str, optional): The account name for the address.
                - "" represents the default account.
                - If the account does not exist, it will be created and a new address assigned.

        Returns:
            str:
                - The Evrmore address associated with the account,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.getaccountaddress("myaccount")
            "EVRaddress12345"
        """
        args = self._build_command() + ["getaccountaddress", str(account)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return out if out else "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getaddressesbyaccount(self, account):
        """
        (DEPRECATED) Returns the list of addresses for the given account.

        Args:
            account (str): The account name.

        Returns:
            list | str:
                - List of Evrmore addresses (parsed JSON) if available,
                - Raw text if daemon returns non-JSON,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.getaddressesbyaccount("tabby")
            ["EVRaddress1", "EVRaddress2"]
        """
        args = self._build_command() + ["getaddressesbyaccount", str(account)]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getbalance(self, account=None, minconf=None, include_watchonly=None):
        """
        Return the wallet balance.

        If account is not specified, returns the server's total available balance.
        If account is specified (DEPRECATED), returns the balance in the account.

        Args:
            account (str | None, optional):
                - DEPRECATED. Account string.
                - "" for keys not in any account, "*" for all accounts.
            minconf (int | None, optional):
                Minimum confirmations (default=1 if provided without value).
            include_watchonly (bool | None, optional):
                Include watch-only balances (default False).

        Returns:
            float | str:
                - Numeric EVR balance (float) on success,
                - Raw text if daemon returns non-JSON,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Examples:
            >>> rpc.getbalance()
            1520.25
            >>> rpc.getbalance("*", 6)
            1499.75
        """
        args = self._build_command() + ["getbalance"]

        provided = [
            account is not None,
            minconf is not None,
            include_watchonly is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) account (default "")
            args.append("" if account is None else str(account))

            # 2) minconf (default 1)
            if last_idx >= 1:
                args.append(str(1 if minconf is None else int(minconf)))

            # 3) include_watchonly (default false)
            if last_idx >= 2:
                iw = False if include_watchonly is None else bool(include_watchonly)
                args.append("true" if iw else "false")

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return float(out)
            except ValueError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getmasterkeyinfo(self):
        """
        Fetch and display the master private/public keys and derivation info.

        Returns:
            dict | str:
                - dict with keys:
                    - bip32_root_private (str): Extended master private key
                    - bip32_root_public (str): Extended master public key
                    - account_derivation_path (str): Derivation path to account keys
                    - account_extended_private_key (str): Extended account private key
                    - account_extended_public_key (str): Extended account public key
                - Raw text if daemon returns non-JSON,
                - "No data returned." if stdout is empty,
                - or "Error: ..." on failure (stderr included).

        Example:
            >>> rpc.getmasterkeyinfo()
            {
                "bip32_root_private": "xprv9s21ZrQH143K3...",
                "bip32_root_public": "xpub661MyMwAqRbcF...",
                "account_derivation_path": "m/44'/175'/0'",
                "account_extended_private_key": "xprv9y...",
                "account_extended_public_key": "xpub6z..."
            }
        """
        args = self._build_command() + ["getmasterkeyinfo"]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getmywords(self, account=None):
        """
        Return the 12-word BIP39 mnemonic and optional passphrase if the wallet was created
        using 12-word import/generation.

        Args:
            account (str | None): Optional account name. Defaults to None.

        Returns:
            dict | str:
                - dict with keys:
                    - word_list (str): Space-separated 12-word mnemonic
                    - passphrase (str, optional): Passphrase if one was used
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure (stderr included)

        Example:
            >>> rpc.getmywords()
            {
                "word_list": "word1 word2 word3 ... word12",
                "passphrase": "optional_passphrase"
            }
        """
        args = self._build_command() + ["getmywords"]
        if account is not None:
            args.append(str(account))

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # Handle non-JSON output by parsing lines into dict
                parsed = {}
                for line in out.splitlines():
                    if ":" in line:
                        key, val = line.split(":", 1)
                        parsed[key.strip().lower().replace(" ", "_")] = val.strip()
                return parsed if parsed else out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getnewaddress(self, account=None):
        """
        Returns a new Evrmore address for receiving payments.

        If 'account' is specified (DEPRECATED), it is added to the address book so payments
        received with the address will be credited to 'account'.

        Args:
            account (str | None): Optional. The account name for the address to be linked to.
                                  If not provided, the default account "" is used.
                                  The account does not need to exist; it will be created if missing.

        Returns:
            dict | str:
                - dict with {"address": str} on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Example:
            >>> rpc.getnewaddress()
            {'address': 'EVRxxxxxx...'}
        """
        args = self._build_command() + ["getnewaddress"]
        if account is not None:
            args.append(str(account))

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                # If it's a plain string (address), wrap it in dict
                parsed = json.loads(out)
                if isinstance(parsed, str):
                    return {"address": parsed}
                return parsed
            except json.JSONDecodeError:
                return {"address": out}
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getrawchangeaddress(self):
        """
        Returns a new Evrmore address for receiving change.
        This is intended for use with raw transactions, NOT normal use.

        Returns:
            dict | str:
                - dict with {"address": str} on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Example:
            >>> rpc.getrawchangeaddress()
            {'address': 'EVRxxxxxx...'}
        """
        args = self._build_command() + ["getrawchangeaddress"]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                parsed = json.loads(out)
                if isinstance(parsed, str):
                    return {"address": parsed}
                return parsed
            except json.JSONDecodeError:
                return {"address": out}
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getreceivedbyaccount(self, account, minconf=None):
        """
        DEPRECATED. Returns the total amount received by addresses with <account>
        in transactions with at least [minconf] confirmations.

        Args:
            account (str): The selected account. May be the default account using "".
            minconf (int, optional): Only include transactions confirmed at least
                this many times. Defaults to 1 if not provided.

        Returns:
            dict | str:
                - dict with {"amount": float} on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Examples:
            >>> rpc.getreceivedbyaccount("tabby")
            {'amount': 12.34}

            >>> rpc.getreceivedbyaccount("", 6)
            {'amount': 50.0}
        """
        args = self._build_command() + ["getreceivedbyaccount", str(account)]
        if minconf is not None:
            args.append(str(minconf))

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                parsed = json.loads(out)
                if isinstance(parsed, (int, float)):
                    return {"amount": float(parsed)}
                return parsed
            except json.JSONDecodeError:
                try:
                    return {"amount": float(out)}
                except ValueError:
                    return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getreceivedbyaddress(self, address, minconf=None):
        """
        Returns the total amount received by the given address in transactions with at least minconf confirmations.

        Args:
            address (str): The Evrmore address for transactions.
            minconf (int, optional): Only include transactions confirmed at least
                this many times. Defaults to 1 if not provided.

        Returns:
            dict | str:
                - dict with {"amount": float} on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Examples:
            >>> rpc.getreceivedbyaddress("1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX")
            {'amount': 5.0}

            >>> rpc.getreceivedbyaddress("1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX", 6)
            {'amount': 12.34}
        """
        args = self._build_command() + ["getreceivedbyaddress", str(address)]
        if minconf is not None:
            args.append(str(minconf))

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                parsed = json.loads(out)
                if isinstance(parsed, (int, float)):
                    return {"amount": float(parsed)}
                return parsed
            except json.JSONDecodeError:
                try:
                    return {"amount": float(out)}
                except ValueError:
                    return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def gettransaction(self, txid, include_watchonly=None):
        """
        Get detailed information about an in-wallet transaction.

        Args:
            txid (str): The transaction id.
            include_watchonly (bool | None): Whether to include watch-only addresses in
                balance calculation and details[]. When omitted, the node default (false) is used.

        Returns:
            dict | str:
                - Parsed JSON dict on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Examples:
            >>> rpc.gettransaction("1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d")
            >>> rpc.gettransaction("1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d", True)
        """
        args = self._build_command() + ["gettransaction", str(txid)]
        if include_watchonly is not None:
            args.append("true" if bool(include_watchonly) else "false")

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getunconfirmedbalance(self):
        """
        Returns the server's total unconfirmed balance.

        Args:
            None

        Returns:
            float | str:
                - The unconfirmed balance as a float on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Example:
            >>> rpc.getunconfirmedbalance()
        """
        args = self._build_command() + ["getunconfirmedbalance"]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return float(out)
            except ValueError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getwalletinfo(self):
        """
        Returns an object containing various wallet state info.

        Args:
            None

        Returns:
            dict | str:
                - Dictionary with wallet information on success
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure

        Example:
            >>> rpc.getwalletinfo()
            {
                "walletname": "wallet.dat",
                "walletversion": 169900,
                "balance": 12.34,
                "unconfirmed_balance": 0.5,
                "immature_balance": 0.0,
                "txcount": 42,
                "keypoololdest": 1625097600,
                "keypoolsize": 1000,
                "keypoolsize_hd_internal": 1000,
                "unlocked_until": 0,
                "paytxfee": 0.0001,
                "hdseedid": "abcdef123456...",
                "hdmasterkeyid": "abcdef123456..."
            }
        """
        args = self._build_command() + ["getwalletinfo"]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importaddress(self, address, label="", rescan=True, p2sh=False):
        """
        Adds a script (in hex) or address that can be watched as if it were in your wallet but cannot be used to spend.

        Args:
            address (str): The hex-encoded script or Evrmore address.
            label (str, optional): An optional label. Defaults to "".
            rescan (bool, optional): Whether to rescan the wallet for transactions. Defaults to True.
            p2sh (bool, optional): Add the P2SH version of the script as well. Defaults to False.

        Returns:
            str: Empty string "" on success (no output).
                 "Error: ..." on failure.

        Example:
            >>> rpc.importaddress("myscript")
            ''
            >>> rpc.importaddress("myscript", "testing", False)
            ''
        """
        args = self._build_command() + [
            "importaddress",
            address,
            label,
            str(rescan).lower(),
            str(p2sh).lower(),
        ]

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importmulti(self, requests, options=None):
        """
        Import addresses/scripts (with priv/pub keys or redeem script), optionally in one rescan.

        Args:
            requests (list[dict]): Each item follows the daemon's spec, e.g.:
                {
                  "scriptPubKey": "<script>" | {"address": "<address>"},
                  "timestamp": 1455191478 | "now",
                  "redeemscript": "<script>",
                  "pubkeys": ["<pubKey>", ...],
                  "keys": ["<WIF or hex privkey>", ...],
                  "internal": False,
                  "watchonly": True,
                  "label": "example"
                }
            options (dict | None): Optional options object, e.g. {"rescan": False}

        Returns:
            list | str:
                - list of per-item results (parsed JSON) on success, e.g. [{"success": true}, ...]
                - raw text if the daemon returns non-JSON
                - or "Error: ..." on failure

        Example:
            >>> rpc.importmulti(
            ...   [{"scriptPubKey": {"address": "myAddr"}, "timestamp": "now"}],
            ...   {"rescan": False}
            ... )
            [{'success': True}]
        """
        if not isinstance(requests, (list, tuple)) or not all(isinstance(x, dict) for x in requests):
            return 'Error: "requests" must be a list of dicts'

        args = self._build_command() + ["importmulti", json.dumps(list(requests))]
        if options is not None:
            if not isinstance(options, dict):
                return 'Error: "options" must be a dict if provided'
            args.append(json.dumps(options))

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                # Node usually returns a JSON array; blank would be unexpected but handle it.
                return []
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importprivkey(self, privkey, label=None, rescan=None):
        """
        Import a private key into the wallet.

        Args:
            privkey (str): WIF (or node-accepted) private key.
            label (str | None): Optional label. If omitted but `rescan` is provided,
                                an empty string "" is passed to preserve positional args.
            rescan (bool | None): Whether to rescan the wallet for transactions.
                                  Defaults to True when needed for position.

        Returns:
            dict | list | str:
                - Parsed JSON if the daemon returns JSON
                - Raw text if the daemon returns non-JSON (many nodes return empty string on success)
                - "Error: ..." on failure
        """
        args = self._build_command() + ["importprivkey"]

        # Always include privkey
        args.append(str(privkey))

        # Determine if we need to include later args; preserve positional order
        provided = [
            label is not None,
            rescan is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 2) label (default "")
            lbl = "" if label is None else str(label)
            args.append(lbl)

            # 3) rescan (default true)
            if last_idx >= 1:
                r = True if rescan is None else bool(rescan)
                args.append("true" if r else "false")

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return ""  # node often returns nothing on success
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importprunedfunds(self, rawtransaction, txoutproof):
        """
        Import funds without a rescan (for pruned wallets).

        Args:
            rawtransaction (str): Hex-encoded raw transaction that funds an address already in the wallet.
            txoutproof (str): Hex-encoded proof from `gettxoutproof` that contains the transaction.

        Returns:
            dict | list | str:
                - Parsed JSON if the daemon returns JSON
                - Raw text if the daemon returns non-JSON (often empty on success)
                - "Error: ..." on failure
        """
        args = self._build_command() + ["importprunedfunds", str(rawtransaction), str(txoutproof)]
        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return ""  # node may return nothing on success
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importpubkey(self, pubkey, label=None, rescan=None):
        """
        Add a hex-encoded public key to the wallet as watch-only.

        Args:
            pubkey (str): Hex-encoded public key.
            label (str | None): Optional label (default: "").
            rescan (bool | None): Whether to rescan the wallet for transactions (default: True).

        Returns:
            dict | list | str:
                - Parsed JSON on success when daemon returns JSON
                - Raw text when daemon returns non-JSON
                - "Error: ..." on failure
        """
        args = ["importpubkey", str(pubkey)]

        # Determine how many optional args to include while preserving positional defaults
        provided = [label is not None, rescan is not None]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 2) label (default "")
            args.append("" if label is None else str(label))
            # 3) rescan (default true)
            if last_idx >= 1:
                r = True if rescan is None else bool(rescan)
                args.append("true" if r else "false")

        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return ""
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def importwallet(self, filename):
        """
        Import keys from a wallet dump file (see dumpwallet).

        Args:
            filename (str): Path to the wallet dump file.

        Returns:
            dict | list | str:
                - Parsed JSON on success when daemon returns JSON
                - Raw text when daemon returns non-JSON
                - "Error: ..." on failure
        """
        args = ["importwallet", str(filename)]
        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return ""
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def keypoolrefill(self, newsize=None):
        """
        Fill the keypool with a new size.

        Args:
            newsize (int, optional): The new keypool size. Defaults to 100 if not specified.

        Returns:
            str: Empty string on success, or error message on failure.
        """
        args = ["keypoolrefill"]
        if newsize is not None:
            args.append(str(newsize))

        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaccounts(self, minconf=1, include_watchonly=False):
        """
        DEPRECATED. Returns a dictionary mapping account names to balances.

        Args:
            minconf (int, optional): Only include transactions with at least this many confirmations.
                                     Defaults to 1.
            include_watchonly (bool, optional): Whether to include balances in watch-only addresses.
                                                Defaults to False.

        Returns:
            dict: A dictionary where keys are account names and values are numeric balances.
        """
        args = ["listaccounts", str(minconf), str(include_watchonly).lower()]
        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": getattr(e, 'stderr', str(e)) or str(e)}

    def listaddressgroupings(self):
        """
        Lists groups of addresses that have had their common ownership revealed
        through shared inputs or change in past transactions.

        Returns:
            list: A list of groups, where each group is a list of entries.
                  Each entry is a list containing:
                    [address (str), amount (float), account (str, optional, DEPRECATED)]
        """
        args = ["listaddressgroupings"]
        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": getattr(e, 'stderr', str(e)) or str(e)}

    def listlockunspent(self):
        """
        Returns a list of temporarily unspendable (locked) outputs.

        See also: lockunspent() to lock and unlock transactions for spending.

        Returns:
            list: A list of dictionaries, each containing:
                  {
                      "txid": str   # The transaction ID locked
                      "vout": int   # The vout index of the locked output
                  }
        """
        args = ["listlockunspent"]
        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": getattr(e, 'stderr', str(e)) or str(e)}

    def listreceivedbyaccount(self, minconf=1, include_empty=False, include_watchonly=False):
        """
        DEPRECATED. List balances by account.

        Args:
            minconf (int, optional): The minimum number of confirmations before payments are included (default=1).
            include_empty (bool, optional): Whether to include accounts that haven't received any payments (default=False).
            include_watchonly (bool, optional): Whether to include watch-only addresses (default=False).

        Returns:
            list: A list of dictionaries containing:
                  {
                      "involvesWatchonly": bool,  # Only if imported addresses were involved
                      "account": str,             # The account name
                      "amount": float,            # Total amount received by addresses in this account
                      "confirmations": int,       # Confirmations of the most recent transaction
                      "label": str                # A comment for the address/transaction (if any)
                  }
        """
        args = ["listreceivedbyaccount", str(minconf), str(include_empty).lower(), str(include_watchonly).lower()]
        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": getattr(e, 'stderr', str(e)) or str(e)}

    def listreceivedbyaddress(self, minconf=1, include_empty=False, include_watchonly=False):
        """
        List balances by receiving address.

        Args:
            minconf (int, optional): The minimum number of confirmations before payments are included (default=1).
            include_empty (bool, optional): Whether to include addresses that haven't received any payments (default=False).
            include_watchonly (bool, optional): Whether to include watch-only addresses (default=False).

        Returns:
            list: A list of dictionaries containing:
                  {
                      "involvesWatchonly": bool,   # Only if imported addresses were involved
                      "address": str,              # The receiving address
                      "account": str,              # DEPRECATED, the account of the address
                      "amount": float,             # Total amount received by the address
                      "confirmations": int,        # Confirmations of the most recent transaction
                      "label": str,                # A comment for the address/transaction, if any
                      "txids": list                # List of transaction IDs received with the address
                  }
        """
        args = [
            "listreceivedbyaddress",
            str(minconf),
            str(include_empty).lower(),
            str(include_watchonly).lower()
        ]
        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": getattr(e, 'stderr', str(e)) or str(e)}

    def listsinceblock(self, blockhash=None, target_confirmations=None, include_watchonly=None, include_removed=None):
        """
        Get all transactions in blocks since the given blockhash (or all if omitted).

        Args:
            blockhash (str | None): The block hash to list transactions since.
            target_confirmations (int | None): Return the (n-1)th best-block hash as 'lastblock'. Default 1 when positionally needed.
            include_watchonly (bool | None): Include watch-only addresses. Default False when positionally needed.
            include_removed (bool | None): Include reorg-removed txs in 'removed'. Default True when positionally needed.

        Returns:
            dict | str:
                - Parsed JSON dict on success:
                  {
                    "transactions": [ ... ],
                    "removed": [ ... ],        # only if include_removed is true
                    "lastblock": "..."
                  }
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure
        """
        args = ["listsinceblock"]

        provided = [
            blockhash is not None,
            target_confirmations is not None,
            include_watchonly is not None,
            include_removed is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) blockhash (default "")
            args.append("" if blockhash is None else str(blockhash))

            # 2) target_confirmations (default 1)
            if last_idx >= 1:
                tc = 1 if target_confirmations is None else int(target_confirmations)
                args.append(str(tc))

            # 3) include_watchonly (default false)
            if last_idx >= 2:
                iw = False if include_watchonly is None else bool(include_watchonly)
                args.append("true" if iw else "false")

            # 4) include_removed (default true)
            if last_idx >= 3:
                ir = True if include_removed is None else bool(include_removed)
                args.append("true" if ir else "false")

        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listtransactions(self, account=None, count=None, skip=None, include_watchonly=None):
        """
        Return up to 'count' most recent transactions, skipping the first 'skip'.

        Args:
            account (str | None): DEPRECATED. Should be "*". Defaults to "*" when positionally needed.
            count (int | None): How many to return. Defaults to 10 when positionally needed.
            skip (int | None): How many to skip. Defaults to 0 when positionally needed.
            include_watchonly (bool | None): Include watch-only addrs. Defaults to False when positionally needed.

        Returns:
            list | str:
                - Parsed JSON list of tx objects on success
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure
        """
        args = ["listtransactions"]

        provided = [
            account is not None,
            count is not None,
            skip is not None,
            include_watchonly is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) account (default "*")
            args.append("*" if account is None else str(account))

            # 2) count (default 10)
            if last_idx >= 1:
                c = 10 if count is None else int(count)
                args.append(str(c))

            # 3) skip (default 0)
            if last_idx >= 2:
                s = 0 if skip is None else int(skip)
                args.append(str(s))

            # 4) include_watchonly (default false)
            if last_idx >= 3:
                iw = False if include_watchonly is None else bool(include_watchonly)
                args.append("true" if iw else "false")

        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listunspent(self, minconf=None, maxconf=None, addresses=None, include_unsafe=None, query_options=None):
        """
        Return UTXOs between minconf and maxconf, optionally filtered by addresses and options.

        Args:
            minconf (int | None): Minimum confirmations. Defaults to 1 when positionally needed.
            maxconf (int | None): Maximum confirmations. Defaults to 9_999_999 when positionally needed.
            addresses (list[str] | None): Addresses to filter. Defaults to [] when positionally needed.
            include_unsafe (bool | None): Include unsafe UTXOs. Defaults to True when positionally needed.
            query_options (dict | None): JSON options (minimumAmount, maximumAmount, maximumCount, minimumSumAmount).

        Returns:
            list | str:
                - Parsed JSON list of UTXO objects on success
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure
        """
        args = ["listunspent"]

        provided = [
            minconf is not None,
            maxconf is not None,
            addresses is not None,
            include_unsafe is not None,
            query_options is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) minconf (default 1)
            mc = 1 if minconf is None else int(minconf)
            args.append(str(mc))

            # 2) maxconf (default 9_999_999)
            if last_idx >= 1:
                xc = 9_999_999 if maxconf is None else int(maxconf)
                args.append(str(xc))

            # 3) addresses (default [])
            if last_idx >= 2:
                addrs = [] if addresses is None else list(addresses)
                # must be a JSON array string for the CLI
                args.append(json.dumps(addrs))

            # 4) include_unsafe (default true)
            if last_idx >= 3:
                iu = True if include_unsafe is None else bool(include_unsafe)
                args.append("true" if iu else "false")

            # 5) query_options (default {})
            if last_idx >= 4:
                qopts = {} if query_options is None else dict(query_options)
                args.append(json.dumps(qopts))

        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listwallets(self):
        """
        Return a list of currently loaded wallets.

        Returns:
            list[str] | str:
                - Parsed JSON array of wallet names on success
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure
        """
        cmd = self._build_command() + ["listwallets"]
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def lockunspent(self, unlock: bool, transactions=None):
        """
        Update the wallet's list of temporarily unspendable outputs.

        Args:
            unlock (bool):
                - True  -> unlock specified UTXOs (or ALL if no transactions provided)
                - False -> lock specified UTXOs (must provide `transactions`)
            transactions (list[dict] | None):
                Optional JSON-like list of {"txid": "<hex>", "vout": <int>} objects.
                Example: [{"txid":"<id>","vout":1}, {"txid":"<id2>","vout":0}]

        Returns:
            bool | str:
                - Parsed boolean on success (daemon prints true/false)
                - Raw text if daemon returns non-JSON
                - Or "Error: ..." on failure

        Notes:
            - If `unlock` is True and `transactions` is None, all current locks are cleared.
            - If `unlock` is False, you generally need to supply `transactions`.

        Example:
            >>> rpc.lockunspent(False, [{"txid": "a08e...adf0", "vout": 1}])
            True
        """
        args = self._build_command() + ["lockunspent", "true" if unlock else "false"]

        # Only include the second argument if caller provided transactions.
        if transactions is not None:
            try:
                # Ensure it's valid JSON for the CLI
                tx_json = json.dumps(transactions, separators=(",", ":"))
            except Exception as enc_err:
                return f"Error: invalid transactions format: {enc_err}"
            args.append(tx_json)

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                # "true"/"false" -> True/False
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def move(self, fromaccount: str, toaccount: str, amount, minconf: int | None = None, comment: str | None = None):
        """
        DEPRECATED. Move EVR between wallet *accounts* (legacy feature).

        Args:
            fromaccount (str): Source account name ("" for default).
            toaccount   (str): Destination account name ("" for default).
            amount      (int|float|str): Quantity of EVR to move.
            minconf     (int|None): Optional minimum confirmations. If you pass a
                                    comment without minconf, 0 will be used.
            comment     (str|None): Optional wallet-only comment.

        Returns:
            bool | str:
                - Parsed boolean (True/False) on success
                - Raw text if daemon returns non-JSON
                - "Error: ..." on failure
        """
        args = self._build_command() + ["move", str(fromaccount), str(toaccount), str(amount)]

        # Positional handling: if `comment` is provided but `minconf` isn't, supply 0.
        if minconf is not None or comment is not None:
            args.append(str(0 if minconf is None else int(minconf)))
        if comment is not None:
            args.append(str(comment))

        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                # daemon prints 'true'/'false' -> parse to bool
                return json.loads(out)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def removeprunedfunds(self, txid: str):
        """
        Delete a specific transaction from the wallet (for pruned-wallet workflows).

        Args:
            txid (str): Hex-encoded transaction ID to delete.

        Returns:
            dict | list | bool | str:
                - Parsed JSON if daemon returns JSON
                - True/False if daemon prints 'true'/'false'
                - Raw text if non-JSON text is returned
                - "No data returned." if stdout is empty
                - "Error: ..." on failure
        """
        args = self._build_command() + ["removeprunedfunds", str(txid)]
        try:
            result = run(args, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                # Some RPCs just return plain text like 'true'/'false' or nothing meaningful
                if out.lower() in ("true", "false"):
                    return out.lower() == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def rescanblockchain(self, start_height=None, stop_height=None):
        """
        Rescan the local blockchain for wallet-related transactions.

        Args:
            start_height (int | None): Block height where the rescan should start.
                                       If None and stop_height is also None, the node defaults to genesis.
                                       If None but stop_height is provided, we pass 0 so the CLI can accept a stop value.
            stop_height  (int | None): Last block height that should be scanned (inclusive). If None, scans to tip.

        Returns:
            dict | list | bool | str:
                - Parsed JSON result on success (e.g., {"start_height": n, "stop_height": m})
                - True/False if daemon prints boolean text
                - Raw text if daemon returns non-JSON
                - "No data returned." if stdout is empty
                - "Error: ..." on failure
        """
        args = ["rescanblockchain"]

        provided = [
            start_height is not None,
            stop_height is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) start_height (default to 0 if only stop_height was given)
            s = 0 if (start_height is None) else int(start_height)
            args.append(str(s))

            # 2) stop_height
            if last_idx >= 1:
                args.append(str(int(stop_height)))

        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                if out.lower() in ("true", "false"):
                    return out.lower() == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    from decimal import Decimal
    import json
    from subprocess import run, PIPE

    def sendfrom(self, fromaccount, toaddress, amount, minconf=None, comment=None, comment_to=None):
        """
        DEPRECATED (use sendtoaddress). Send an amount from an account to an Evrmore address.

        Positional args (required):
            fromaccount (str): Account name ("" for default).
            toaddress   (str): Destination EVR address.
            amount      (str|int|float|Decimal): Amount in EVR (fee added on top).

        Optional (positional order preserved):
            minconf     (int|None): Only use funds with at least this many confirmations. Default 1 if a later arg is provided.
            comment     (str|None): Wallet-only note.
            comment_to  (str|None): Wallet-only note for recipient name.

        Returns:
            dict | list | bool | str:
                - Parsed JSON on success when daemon returns JSON
                - Plain string (e.g., txid) if daemon returns raw text
                - True/False if daemon returns a lone boolean
                - "No data returned." if stdout empty
                - "Error: ..." on failure
        """
        # Required core
        args = ["sendfrom"]
        args.append(str("" if fromaccount is None else fromaccount))
        args.append(str(toaddress))

        # Normalize amount as a plain decimal string
        amt = Decimal(str(amount))
        args.append(format(amt, 'f'))

        # Figure out how far optional args go
        provided = [minconf is not None, comment is not None, comment_to is not None]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) minconf (default 1 if later args provided but minconf is None)
            mc = 1 if (minconf is None) else int(minconf)
            args.append(str(mc))

            # 2) comment
            if last_idx >= 1:
                args.append("" if comment is None else str(comment))

            # 3) comment_to
            if last_idx >= 2:
                args.append("" if comment_to is None else str(comment_to))

        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                lo = out.lower()
                if lo in ("true", "false"):
                    return lo == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    from decimal import Decimal
    import json
    from subprocess import run, PIPE

    def sendfromaddress(
            self,
            from_address,
            to_address,
            amount,
            comment=None,
            comment_to=None,
            subtractfeefromamount=None,
            conf_target=None,
            estimate_mode=None,
    ):
        """
        Send an amount from a specific address to a given address.
        All EVR change returns to `from_address`.

        Positional required:
            from_address (str)
            to_address   (str)
            amount       (str|int|float|Decimal) — EVR amount

        Optional (positional order preserved exactly as CLI):
            comment                 (str|None)
            comment_to              (str|None)
            subtractfeefromamount   (bool|None)   -> default False if later args provided
            conf_target             (int|None)
            estimate_mode           (str|None)    -> default "UNSET" if provided after earlier Nones

        Returns:
            dict | list | bool | str
            - Parsed JSON on success (if daemon emits JSON)
            - Plain string (e.g., txid) otherwise
            - True/False if stdout is a lone boolean
            - "No data returned." if empty
            - "Error: ..." on failure
        """
        args = ["sendfromaddress", str(from_address), str(to_address)]

        # Normalize amount as a plain decimal string (avoids scientific notation)
        amt = Decimal(str(amount))
        args.append(format(amt, "f"))

        # Determine how far we go with optional positional args
        provided = [
            comment is not None,
            comment_to is not None,
            subtractfeefromamount is not None,
            conf_target is not None,
            estimate_mode is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 1) comment (default "")
            args.append("" if comment is None else str(comment))

            # 2) comment_to (default "")
            if last_idx >= 1:
                args.append("" if comment_to is None else str(comment_to))

            # 3) subtractfeefromamount (default false)
            if last_idx >= 2:
                sffa = False if subtractfeefromamount is None else bool(subtractfeefromamount)
                args.append("true" if sffa else "false")

            # 4) conf_target (no implicit default unless later args require position; use 0 if None)
            if last_idx >= 3:
                ct = 0 if conf_target is None else int(conf_target)
                args.append(str(ct))

            # 5) estimate_mode (default UNSET)
            if last_idx >= 4:
                em = "UNSET" if estimate_mode is None else str(estimate_mode)
                args.append(em)

        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                lo = out.lower()
                if lo in ("true", "false"):
                    return lo == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def sendmany(
            self,
            from_account="",
            amounts=None,
            minconf=None,
            comment=None,
            subtractfeefrom=None,
            conf_target=None,
            estimate_mode=None,
    ):
        """
        Send multiple payments in one transaction.

        Positional args (Bitcoin/Evrmore CLI order preserved):
            from_account (str)                         — DEPRECATED upstream; usually "".
            amounts (dict[str, str|int|float|Decimal]) — {"address": amount, ...}
            minconf (int|None)                         — default 1 if later args supplied
            comment (str|None)                         — default ""
            subtractfeefrom (list[str]|None)           — JSON array of addresses
            conf_target (int|None)                     — default 0 if position needed
            estimate_mode (str|None)                   — default "UNSET" if position needed

        Returns:
            dict | list | bool | str
            - Parsed JSON on success (if daemon emits JSON)
            - Plain string (e.g., txid) otherwise
            - True/False if stdout is a lone boolean
            - "No data returned." if empty
            - "Error: ..." on failure
        """
        if not isinstance(amounts, dict) or not amounts:
            return "Error: 'amounts' must be a non-empty dict of {address: amount}"

        # Build amounts JSON where each value is emitted as a string to avoid FP drift.
        amt_obj = {}
        for addr, val in amounts.items():
            # normalize to decimal string; CLI accepts numeric OR string
            try:
                dec = Decimal(str(val))
            except Exception:
                return f"Error: invalid amount for {addr!r}: {val!r}"
            amt_obj[str(addr)] = str(dec)  # keep as string to preserve precision

        amounts_json = json.dumps(amt_obj, separators=(",", ":"))

        args = ["sendmany", str(from_account), amounts_json]

        # Figure out how far we need to fill positional optionals
        provided = [
            minconf is not None,
            comment is not None,
            subtractfeefrom is not None,
            conf_target is not None,
            estimate_mode is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 3) minconf (default 1)
            mc = 1 if minconf is None else int(minconf)
            args.append(str(mc))

            # 4) comment (default "")
            if last_idx >= 1:
                args.append("" if comment is None else str(comment))

            # 5) subtractfeefrom (default [] if present)
            if last_idx >= 2:
                if subtractfeefrom is None:
                    sff_json = "[]"
                else:
                    if not isinstance(subtractfeefrom, (list, tuple)):
                        return "Error: 'subtractfeefrom' must be a list of addresses"
                    sff_json = json.dumps([str(a) for a in subtractfeefrom], separators=(",", ":"))
                args.append(sff_json)

            # 6) conf_target (default 0 if position required)
            if last_idx >= 3:
                ct = 0 if conf_target is None else int(conf_target)
                args.append(str(ct))

            # 7) estimate_mode (default UNSET)
            if last_idx >= 4:
                em = "UNSET" if estimate_mode is None else str(estimate_mode)
                args.append(em)

        cmd = self._build_command() + args
        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                lo = out.lower()
                if lo in ("true", "false"):
                    return lo == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()


    def sendtoaddress(
            self,
            address,
            amount,
            comment=None,
            comment_to=None,
            subtractfeefromamount=None,
            conf_target=None,
            estimate_mode=None,
    ):
        """
        Send an amount to a given address.

        Positional order is preserved exactly like the CLI:
          address, amount, comment, comment_to, subtractfeefromamount, conf_target, estimate_mode

        Args:
            address (str): Destination Evrmore address.
            amount  (Decimal|str|int|float): Amount in EVR.
            comment (str|None): Wallet-only note. Default "" if a later arg is supplied.
            comment_to (str|None): Wallet-only note for recipient. Default "" if a later arg is supplied.
            subtractfeefromamount (bool|None): If True, fee is deducted from amount. Default False if position required.
            conf_target (int|None): Confirmation target (blocks). Default 0 if position required.
            estimate_mode (str|None): "UNSET"|"ECONOMICAL"|"CONSERVATIVE". Default "UNSET" if position required.

        Returns:
            dict | list | bool | str:
                - Parsed JSON on success (if daemon returns JSON)
                - Plain string (e.g., txid) otherwise
                - True/False if stdout is a lone boolean
                - "No data returned." if empty
                - "Error: ..." on failure
        """
        # normalize amount using Decimal to avoid float drift
        try:
            amt = Decimal(str(amount))
        except Exception:
            return f"Error: invalid amount: {amount!r}"

        args = ["sendtoaddress", str(address), str(amt)]

        # Determine how far to fill optional positional parameters
        provided = [
            comment is not None,
            comment_to is not None,
            subtractfeefromamount is not None,
            conf_target is not None,
            estimate_mode is not None,
        ]
        last_idx = -1
        for i, flag in enumerate(provided):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 3) comment (default "")
            args.append("" if comment is None else str(comment))

            # 4) comment_to (default "")
            if last_idx >= 1:
                args.append("" if comment_to is None else str(comment_to))

            # 5) subtractfeefromamount (default false)
            if last_idx >= 2:
                sffa = False if subtractfeefromamount is None else bool(subtractfeefromamount)
                args.append("true" if sffa else "false")

            # 6) conf_target (default 0)
            if last_idx >= 3:
                ct = 0 if conf_target is None else int(conf_target)
                args.append(str(ct))

            # 7) estimate_mode (default UNSET)
            if last_idx >= 4:
                em = "UNSET" if estimate_mode is None else str(estimate_mode)
                args.append(em)

        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                lo = out.lower()
                if lo in ("true", "false"):
                    return lo == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def setaccount(self, address, account):
        """
        DEPRECATED. Sets the account associated with the given address.

        Positional order is preserved exactly like the CLI:
          address, account

        Args:
            address (str): The Evrmore address to be associated with an account.
            account (str): The account name to assign to the address.

        Returns:
            dict | list | bool | str:
                - Parsed JSON on success (if daemon returns JSON)
                - Plain string otherwise
                - True/False if stdout is a lone boolean
                - "No data returned." if empty
                - "Error: ..." on failure
        """
        args = ["setaccount", str(address), str(account)]
        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                lo = out.lower()
                if lo in ("true", "false"):
                    return lo == "true"
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def settxfee(self, amount):
        """
        Set the transaction fee per kB. Overwrites the paytxfee parameter.

        Positional order is preserved exactly like the CLI:
          amount

        Args:
            amount (float | str): The transaction fee in EVR/kB.

        Returns:
            bool | str:
                - True/False if daemon returns a boolean
                - Raw string if response is not JSON or boolean
                - "No data returned." if empty
                - "Error: ..." on failure
        """
        args = ["settxfee", str(amount)]
        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            lo = out.lower()
            if lo in ("true", "false"):
                return lo == "true"
            return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def signmessage(self, address, message):
        """
        Sign a message with the private key of an address.

        Positional order is preserved exactly like the CLI:
          address, message

        Args:
            address (str): The Evrmore address to use for the private key.
            message (str): The message to create a signature of.

        Returns:
            str:
                - The base64-encoded signature string if successful
                - "No data returned." if output is empty
                - "Error: ..." on failure
        """
        args = ["signmessage", address, message]
        cmd = self._build_command() + args

        try:
            result = run(cmd, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

