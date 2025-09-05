from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json



class RestrictedassetsRPC:

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

    def addtagtoaddress(self, tag_name, to_address, change_address=None, asset_data=None):
        """
        Assign a tag to an address.

        Args:
            tag_name (str):
                Tag to assign. If it does not start with '#', one will be added automatically.
            to_address (str):
                Address that will receive the tag.
            change_address (str | None, optional):
                EVR change address for the qualifier token transfer. Defaults to "" when needed for position.
            asset_data (str | None, optional):
                Optional asset data (e.g., IPFS or txid hash). Defaults to "" when needed for position.

        Returns:
            str | dict:
                Parsed JSON if available; otherwise raw text. On error, returns "Error: ...".

        Example:
            >>> rpc.addtagtoaddress("#KYC", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """
        # Normalize tag name
        if not tag_name.startswith("#"):
            tag_name = "#" + tag_name

        args = ["addtagtoaddress", str(tag_name), str(to_address)]

        # Optional args in order; fill placeholders up to the last provided
        optionals = [change_address, asset_data]
        provided = [o is not None for o in optionals]
        last_idx = -1
        for i, p in enumerate(provided):
            if p:
                last_idx = i

        if last_idx >= 0:
            defaults = ["", ""]  # change_address, asset_data
            for i in range(last_idx + 1):
                val = optionals[i]
                args.append(defaults[i] if val is None else str(val))

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

    def checkaddressrestriction(self, address, restricted_name):
        """
        Check whether an address is frozen by the given restricted asset.

        Args:
            address (str):
                EVR address to check.
            restricted_name (str):
                Restricted asset name (must start with '$'; if omitted in the name, the node will add it).

        Returns:
            bool | str:
                - True/False on success (parsed from daemon output)
                - Raw text if the daemon returns non-JSON
                - Or "Error: ..." on failure

        Example:
            >>> rpc.checkaddressrestriction("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "$SECURITY")
        """
        command = self._build_command() + [
            "checkaddressrestriction",
            str(address),
            str(restricted_name),
        ]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # expected 'true'/'false' -> True/False
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def checkaddresstag(self, address, tag_name):
        """
        Check whether an address has the given tag.

        Args:
            address (str):
                EVR address to check.
            tag_name (str):
                Tag name to check (must start with '#'; if omitted in the name, the node will add it).

        Returns:
            bool | str:
                - True/False on success (parsed from daemon output)
                - Raw text if the daemon returns non-JSON
                - Or "Error: ..." on failure

        Example:
            >>> rpc.checkaddresstag("mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF", "#KYC")
        """
        command = self._build_command() + [
            "checkaddresstag",
            str(address),
            str(tag_name),
        ]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # expected 'true'/'false' -> True/False
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def checkglobalrestriction(self, restricted_name):
        """
        Check whether a restricted asset is globally frozen.

        Args:
            restricted_name (str):
                The restricted asset to check.

        Returns:
            bool | str:
                - True/False on success (parsed from daemon output)
                - Raw text if the daemon returns non-JSON
                - Or "Error: ..." on failure

        Example:
            >>> rpc.checkglobalrestriction("NEUBTRINO_RESTRICTED_1")
        """
        command = self._build_command() + [
            "checkglobalrestriction",
            str(restricted_name),
        ]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # expected 'true'/'false' -> True/False
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def freezeaddress(self, asset_name, address, change_address=None, asset_data=None):
        """
        Freeze an address from transferring a restricted asset.

        Args:
            asset_name (str):
                The name of the restricted asset you want to freeze.
            address (str):
                The address that will be frozen.
            change_address (str | None):
                The change address for the owner token of the restricted asset.
                Defaults to "" if omitted.
            asset_data (str | None):
                Asset data (IPFS or hash) applied to the transfer of the owner token.
                Defaults to "" if omitted.

        Returns:
            str | dict:
                - Transaction ID string (txid) on success
                - Raw text if daemon returns non-JSON
                - "Error: ..." string on failure

        Example:
            >>> rpc.freezeaddress("NEUBTRINO_RESTRICTED_1", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
            'txid'
        """
        params = [
            str(asset_name),
            str(address),
            "" if change_address is None else str(change_address),
            "" if asset_data is None else str(asset_data),
        ]

        command = self._build_command() + ["freezeaddress"] + params

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # parse txid if JSON
            except json.JSONDecodeError:
                return out  # return raw txid string if plain text
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def freezerestrictedasset(self, asset_name, change_address=None, asset_data=None):
        """
        Freeze all trading for a specific restricted asset.

        Args:
            asset_name (str):
                The name of the restricted asset you want to freeze.
            change_address (str | None):
                The change address for the owner token of the restricted asset.
                Defaults to "" if omitted.
            asset_data (str | None):
                Asset data (IPFS or hash) applied to the transfer of the owner token.
                Defaults to "" if omitted.

        Returns:
            str | dict:
                - Transaction ID string (txid) on success
                - Raw text if daemon returns non-JSON
                - "Error: ..." string on failure

        Example:
            >>> rpc.freezerestrictedasset("NEUBTRINO_RESTRICTED_1")
            'txid'
        """
        params = [
            str(asset_name),
            "" if change_address is None else str(change_address),
            "" if asset_data is None else str(asset_data),
        ]

        command = self._build_command() + ["freezerestrictedasset"] + params

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # parse txid if JSON
            except json.JSONDecodeError:
                return out  # return raw txid string if plain text
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getverifierstring(self, restricted_name):
        """
        Retrieve the verifier string that belongs to the given restricted asset.

        Args:
            restricted_name (str):
                The restricted asset name.

        Returns:
            str | dict:
                - Verifier string on success
                - Raw text if daemon returns non-JSON
                - "Error: ..." string on failure

        Example:
            >>> rpc.getverifierstring("NEUBTRINO_RESTRICTED_1")
            '#KYC & !#AML'
        """
        command = self._build_command() + ["getverifierstring", str(restricted_name)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # if it ever returns JSON
            except json.JSONDecodeError:
                return out  # plain string verifier
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def issuequalifierasset(
            self,
            asset_name,
            qty=1,
            to_address="",
            change_address="",
            has_ipfs=False,
            ipfs_hash=None,
            permanent_ipfs_hash=None,
    ):
        """
        Issue a qualifier or sub-qualifier asset.

        If the '#' character isn't added to the asset name, it will be added automatically.
        Qualifier assets always have unit=0 and are non-reissuable.

        Args:
            asset_name (str): A unique asset name (prefix '#' will be added automatically if omitted).
            qty (int, optional): Quantity to issue. Must be between 1 and 10. Default is 1.
            to_address (str, optional): Address asset will be sent to. If empty, a new one will be generated.
            change_address (str, optional): Address where Evrmore change will be sent. If empty, one will be generated.
            has_ipfs (bool, optional): Whether an IPFS hash is added to the asset. Default is False.
            ipfs_hash (str | None, optional): IPFS hash (required if has_ipfs=True).
            permanent_ipfs_hash (str | None, optional): Permanent IPFS hash for the asset.

        Returns:
            str | dict:
                - Transaction ID string on success
                - Raw text if daemon returns non-JSON
                - "Error: ..." string on failure

        Example:
            >>> rpc.issuequalifierasset("#ASSET_NAME", 1)
            'txid'
        """
        args = ["issuequalifierasset", str(asset_name), str(int(qty))]

        # Ensure positional consistency
        args.append(str(to_address or ""))
        args.append(str(change_address or ""))
        args.append("true" if has_ipfs else "false")

        # Handle optional IPFS fields
        if ipfs_hash is not None:
            args.append(str(ipfs_hash))
            if permanent_ipfs_hash is not None:
                args.append(str(permanent_ipfs_hash))

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

    def issuerestrictedasset(
            self,
            asset_name,
            qty,
            verifier,
            to_address,
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
        Issue a restricted asset.

        Args:
            asset_name (str): Unique name (a leading '$' will be added automatically if missing).
            qty (int | float): Quantity to issue.
            verifier (str): Verifier string that governs transfers (e.g., "#KYC & !#AML").
            to_address (str): Recipient address (must satisfy the verifier).
            change_address (str | None): EVR change address. Default "" when needed for position.
            units (int | None): Decimal precision (0–8). Default 0 when needed for position.
            reissuable (bool | None): Whether future reissuance/verifier changes are allowed. Default True when needed.
            has_ipfs (bool | None): Whether to attach IPFS/txid metadata. Default False when needed.
            ipfs_hash (str | None): IPFS (or RIP-5 txid) hash. Required by daemon if has_ipfs=True.
            permanent_ipfs_hash (str | None): Permanent IPFS hash.
            toll_amount (int | float | None): Toll fee amount. Default 0 when needed.
            toll_address (str | None): Toll receiver address. Default "" when needed.
            toll_amount_mutability (bool | None): Whether toll amount can change later. Default False when needed.
            toll_address_mutability (bool | None): Whether toll address can change later. Default False when needed.
            remintable (bool | None): Whether burned tokens can be reminted. Default True when needed.

        Returns:
            dict | str:
                - Parsed JSON (e.g., txid string or object) on success
                - Raw daemon output if not JSON
                - "Error: ..." on failure

        Example:
            >>> rpc.issuerestrictedasset("$SECURITY", 1000, "#KYC & !#AML", "mzKoqPMQcfFGStsMXfMEGMqNnGegm91vAF")
        """
        args = [
            "issuerestrictedasset",
            str(asset_name),
            str(qty),
            str(verifier),
            str(to_address),
        ]

        # Determine up to which optional parameter we must fill (to preserve positional order)
        optionals = [
            change_address,
            units,
            reissuable,
            has_ipfs,
            ipfs_hash,
            permanent_ipfs_hash,
            toll_amount,
            toll_address,
            toll_amount_mutability,
            toll_address_mutability,
            remintable,
        ]
        provided_flags = [opt is not None for opt in optionals]
        last_idx = -1
        for i, flag in enumerate(provided_flags):
            if flag:
                last_idx = i

        if last_idx >= 0:
            # 5) change_address -> default ""
            val = optionals[0] if optionals[0] is not None else ""
            args.append(str(val))

            if last_idx >= 1:
                # 6) units -> default 0
                val = optionals[1] if optionals[1] is not None else 0
                args.append(str(int(val)))

            if last_idx >= 2:
                # 7) reissuable -> default True
                val = optionals[2] if optionals[2] is not None else True
                args.append("true" if bool(val) else "false")

            if last_idx >= 3:
                # 8) has_ipfs -> default False
                val = optionals[3] if optionals[3] is not None else False
                args.append("true" if bool(val) else "false")

            if last_idx >= 4:
                # 9) ipfs_hash -> default ""
                val = optionals[4] if optionals[4] is not None else ""
                args.append(str(val))

            if last_idx >= 5:
                # 10) permanent_ipfs_hash -> default ""
                val = optionals[5] if optionals[5] is not None else ""
                args.append(str(val))

            if last_idx >= 6:
                # 11) toll_amount -> default 0
                val = optionals[6] if optionals[6] is not None else 0
                args.append(str(val))

            if last_idx >= 7:
                # 12) toll_address -> default ""
                val = optionals[7] if optionals[7] is not None else ""
                args.append(str(val))

            if last_idx >= 8:
                # 13) toll_amount_mutability -> default False
                val = optionals[8] if optionals[8] is not None else False
                args.append("true" if bool(val) else "false")

            if last_idx >= 9:
                # 14) toll_address_mutability -> default False
                val = optionals[9] if optionals[9] is not None else False
                args.append("true" if bool(val) else "false")

            if last_idx >= 10:
                # 15) remintable -> default True
                val = optionals[10] if optionals[10] is not None else True
                args.append("true" if bool(val) else "false")

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

    def isvalidverifierstring(self, verifier_string):
        """
        Checks whether the given verifier string is valid.

        Args:
            verifier_string (str): The verifier string to check.

        Returns:
            dict | str:
                - dict with validation details (parsed JSON) if possible,
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.isvalidverifierstring("#KYC & !#AML")
            {"isvalid": true, "reason": "Valid verifier string"}
        """
        args = ["isvalidverifierstring", str(verifier_string)]
        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # structured parse if JSON
            except json.JSONDecodeError:
                return out  # fallback to raw string
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaddressesfortag(self, tag_name):
        """
        List all addresses that have been assigned a given tag.

        Args:
            tag_name (str): The tag asset name to search for.

        Returns:
            list | str:
                - list of addresses (parsed JSON) on success,
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.listaddressesfortag("#KYC")
            ["EVRAddress1", "EVRAddress2", "EVRAddress3"]
        """
        args = ["listaddressesfortag", str(tag_name)]
        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # should normally be a list
            except json.JSONDecodeError:
                return out  # fallback to raw string
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listaddressrestrictions(self, address):
        """
        List all assets that have frozen a given address.

        Args:
            address (str): The address to check restrictions for.

        Returns:
            list | str:
                - list of restricted asset names (parsed JSON) on success,
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.listaddressrestrictions("EVRAddress123")
            ["$ASSET1", "$ASSET2"]
        """
        args = ["listaddressrestrictions", str(address)]
        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # expected to be a list of asset names
            except json.JSONDecodeError:
                return out  # fallback to raw string if not JSON
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listglobalrestrictions(self):
        """
        List all globally restricted assets.

        Returns:
            list | str:
                - list of restricted asset names (parsed JSON) on success,
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.listglobalrestrictions()
            ["$ASSET1", "$ASSET2"]
        """
        args = ["listglobalrestrictions"]
        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # expected to be a list of asset names
            except json.JSONDecodeError:
                return out  # fallback to raw string if not JSON
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def listtagsforaddress(self, address):
        """
        List all tags assigned to an address.

        Args:
            address (str): The EVR address to list tags for.

        Returns:
            list | str:
                - list of tag names (parsed JSON) on success,
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.listtagsforaddress("myEVRaddress")
            ["#TAG1", "#TAG2"]
        """
        args = ["listtagsforaddress", address]
        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            try:
                return json.loads(out)  # expected list of tag names
            except json.JSONDecodeError:
                return out  # fallback if not JSON
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()



    def reissuerestrictedasset(
            self,
            asset_name,
            qty,
            to_address,
            change_verifier=None,
            new_verifier=None,
            change_address=None,
            new_units=None,
            reissuable=None,
            new_ipfs=None,
            permanent_ipfs=None,
            change_toll_amount=None,
            toll_amount=None,
            toll_address=None,
            toll_amount_mutability=None,
            toll_address_mutability=None,
    ):
        """
        Reissue an existing restricted asset.

        Args:
            asset_name (str): Restricted asset name to reissue (must start with "$").
            qty (int | float): Additional quantity to issue.
            to_address (str): Recipient address (must satisfy current/new verifier).
            change_verifier (bool | None): Change the verifier string. Defaults to False when needed.
            new_verifier (str | None): New verifier string. Defaults to "" when needed.
            change_address (str | None): EVR change address. Defaults to "" when needed.
            new_units (int | None): New units/decimals (-1 keeps current). Defaults to -1 when needed.
            reissuable (bool | None): Whether future reissuance is allowed. Defaults to True when needed.
            new_ipfs (str | None): New IPFS/txid metadata. Defaults to "" when needed.
            permanent_ipfs (str | None): New permanent IPFS hash. Defaults to "" when needed.
            change_toll_amount (bool | None): Whether toll amount is being changed. Defaults to False when needed.
            toll_amount (int | float | None): Toll amount to set. Defaults to 0 when needed.
            toll_address (str | None): Toll receiver address. Defaults to "" when needed.
            toll_amount_mutability (bool | None): Whether toll amount can change later. Defaults to True when needed.
            toll_address_mutability (bool | None): Whether toll address can change later. Defaults to True when needed.

        Returns:
            dict | str:
                - Parsed JSON (e.g., txid string/object) on success,
                - raw daemon output if not JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.reissuerestrictedasset("$ASSET_NAME", 1000, "myaddress", True, "KYC & !AML")
        """
        args = [
            "reissuerestrictedasset",
            str(asset_name),
            str(qty),
            str(to_address),
        ]

        optionals = [
            change_verifier,  # 4
            new_verifier,  # 5
            change_address,  # 6
            new_units,  # 7
            reissuable,  # 8
            new_ipfs,  # 9
            permanent_ipfs,  # 10
            change_toll_amount,  # 11
            toll_amount,  # 12
            toll_address,  # 13
            toll_amount_mutability,  # 14
            toll_address_mutability,  # 15
        ]

        # find the last provided optional to preserve positional order
        last_idx = -1
        for i, v in enumerate(optionals):
            if v is not None:
                last_idx = i

        if last_idx >= 0:
            # 4) change_verifier -> default False
            v = optionals[0] if optionals[0] is not None else False
            args.append("true" if bool(v) else "false")

            if last_idx >= 1:
                # 5) new_verifier -> default ""
                v = optionals[1] if optionals[1] is not None else ""
                args.append(str(v))

            if last_idx >= 2:
                # 6) change_address -> default ""
                v = optionals[2] if optionals[2] is not None else ""
                args.append(str(v))

            if last_idx >= 3:
                # 7) new_units -> default -1
                v = optionals[3] if optionals[3] is not None else -1
                args.append(str(int(v)))

            if last_idx >= 4:
                # 8) reissuable -> default True
                v = optionals[4] if optionals[4] is not None else True
                args.append("true" if bool(v) else "false")

            if last_idx >= 5:
                # 9) new_ipfs -> default ""
                v = optionals[5] if optionals[5] is not None else ""
                args.append(str(v))

            if last_idx >= 6:
                # 10) permanent_ipfs -> default ""
                v = optionals[6] if optionals[6] is not None else ""
                args.append(str(v))

            if last_idx >= 7:
                # 11) change_toll_amount -> default False
                v = optionals[7] if optionals[7] is not None else False
                args.append("true" if bool(v) else "false")

            if last_idx >= 8:
                # 12) toll_amount -> default 0
                v = optionals[8] if optionals[8] is not None else 0
                args.append(str(v))

            if last_idx >= 9:
                # 13) toll_address -> default ""
                v = optionals[9] if optionals[9] is not None else ""
                args.append(str(v))

            if last_idx >= 10:
                # 14) toll_amount_mutability -> default True
                v = optionals[10] if optionals[10] is not None else True
                args.append("true" if bool(v) else "false")

            if last_idx >= 11:
                # 15) toll_address_mutability -> default True
                v = optionals[11] if optionals[11] is not None else True
                args.append("true" if bool(v) else "false")

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

    def removetagfromaddress(self, tag_name, to_address, change_address=None, asset_data=None):
        """
        Remove a tag from an address.

        Args:
            tag_name (str): The tag being removed from the address.
            to_address (str): The address from which the tag will be removed.
            change_address (str | None): Optional. Change address for the qualifier token to be sent to.
            asset_data (str | None): Optional. Asset data (IPFS hash or a hash) applied to the transfer.

        Returns:
            str | dict:
                - Transaction ID string (parsed JSON if possible),
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.removetagfromaddress("#TAG", "EVRaddress123")
            "txid"
        """
        args = ["removetagfromaddress", tag_name, to_address]

        if change_address is not None:
            args.append(change_address)
            if asset_data is not None:
                args.append(asset_data)
        elif asset_data is not None:
            # preserve order: add empty string placeholder if only asset_data is provided
            args.append("")
            args.append(asset_data)

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



    def transferqualifier(self, qualifier_name, qty, to_address, change_address=None, message=None, expire_time=None):
        """
        Transfer a qualifier asset owned by this wallet to the given address.

        Args:
            qualifier_name (str): Name of the qualifier asset (e.g., "#KYC").
            qty (int | float): Quantity to send.
            to_address (str): Destination address.
            change_address (str | None): EVR change address. Defaults to "" when needed to preserve argument order.
            message (str | None): Optional IPFS/txid hash to include with the transfer. Defaults to "" when needed.
            expire_time (int | None): UTC timestamp when the message expires. Defaults to 0 when needed.

        Returns:
            list | dict | str:
                - Parsed JSON (e.g., ["txid", ...]) on success,
                - raw daemon output if not JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.transferqualifier("#QUALIFIER", 20, "to_address", "", "QmHash...", 15863654)
        """
        args = [
            "transferqualifier",
            str(qualifier_name),
            str(qty),
            str(to_address),
        ]

        # Optional args in declared order
        optionals = [change_address, message, expire_time]

        # Determine the last provided optional index to preserve positional parsing
        last_idx = -1
        for i, v in enumerate(optionals):
            if v is not None:
                last_idx = i

        if last_idx >= 0:
            # 4) change_address -> default ""
            v = optionals[0] if optionals[0] is not None else ""
            args.append(str(v))

            if last_idx >= 1:
                # 5) message -> default ""
                v = optionals[1] if optionals[1] is not None else ""
                args.append(str(v))

            if last_idx >= 2:
                # 6) expire_time -> default 0
                v = optionals[2] if optionals[2] is not None else 0
                args.append(str(int(v)))

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

    def unfreezeaddress(self, asset_name, address, change_address=None, asset_data=None):
        """
        Unfreeze an address from transferring a restricted asset.

        Args:
            asset_name (str): The name of the restricted asset to unfreeze.
            address (str): The EVR address that will be unfrozen.
            change_address (str | None): Optional. The change address for the owner token of the restricted asset.
            asset_data (str | None): Optional. The asset data (IPFS or hash) to apply to the transfer of the owner token.

        Returns:
            str | dict:
                - Transaction ID string (parsed JSON if possible),
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.unfreezeaddress("$RESTRICTED_ASSET", "EVRaddress123")
            "txid"
        """
        args = ["unfreezeaddress", asset_name, address]

        if change_address is not None:
            args.append(change_address)
            if asset_data is not None:
                args.append(asset_data)
        elif asset_data is not None:
            # preserve order: if change_address is skipped but asset_data is provided
            args.append("")
            args.append(asset_data)

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

    def unfreezerestrictedasset(self, asset_name, change_address=None, asset_data=None):
        """
        Unfreeze all trading for a specific restricted asset.

        Args:
            asset_name (str): The restricted asset name to unfreeze.
            change_address (str | None): Optional. Change address for the owner token.
            asset_data (str | None): Optional. Asset data (IPFS hash or hash) to be applied to the transfer.

        Returns:
            str | dict:
                - Transaction ID string (parsed JSON if possible),
                - raw string if daemon does not return JSON,
                - or "Error: ..." on failure.

        Example:
            >>> rpc.unfreezerestrictedasset("$RESTRICTED_ASSET")
            "txid"
        """
        args = ["unfreezerestrictedasset", asset_name]

        if change_address is not None:
            args.append(change_address)
            if asset_data is not None:
                args.append(asset_data)
        elif asset_data is not None:
            # preserve order: insert "" if only asset_data is given
            args.append("")
            args.append(asset_data)

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


