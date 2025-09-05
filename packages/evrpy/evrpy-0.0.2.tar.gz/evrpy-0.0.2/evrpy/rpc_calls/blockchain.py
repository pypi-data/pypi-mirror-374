from subprocess import run, PIPE
from evrpy.base_commands import build_base_command
import json

class BlockchainRPC:

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

    def clearmempool(self):
        """
        Remove all transactions from the node’s mempool.

        Returns:
            dict | list | str:
                Parsed JSON/primitive if returned by the daemon, or raw string output.
                On failure: "Error: <message>".

        Example:
            >>> rpc.clearmempool()
        """
        command = self._build_command() + ["clearmempool"]

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

    def decodeblock(self, blockhex):
        """
        Decode a serialized block provided in hex format.

        Args:
            blockhex (str): The hex-encoded block data to decode.

        Returns:
            dict | str:
                On success: Parsed JSON with block details, or raw string if parsing fails.
                On error: "Error: <message>".

        Example:
            >>> rpc.decodeblock("00000020abcdef...")
        """
        command = self._build_command() + ["decodeblock", str(blockhex)]

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

    def getbestblockhash(self):
        """
        Get the hash of the best (tip) block in the active chain.

        Returns:
            str:
                On success: The block hash (hex string).
                On error: "Error: <message>".

        Example:
            >>> rpc.getbestblockhash()
        """
        command = self._build_command() + ["getbestblockhash"]

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

    def getblock(self, blockhash, verbosity=None):
        """
        Get details for a block by its hash.

        Args:
            blockhash (str): The block hash.
            verbosity (int | None, optional):
                - 0 → return hex-encoded serialized block data.
                - 1 → return block details as a JSON object.
                - 2 → return block details plus full transaction data.
                Defaults to 1 if not specified.

        Returns:
            str | dict:
                - If verbosity=0: a hex-encoded string of block data.
                - If verbosity=1: a dictionary with block metadata.
                - If verbosity=2: a dictionary with block metadata and transactions.
                - On error: "Error: <message>".

        Example:
            >>> rpc.getblock("00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09")
            >>> rpc.getblock("00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09", verbosity=2)
        """
        command = self._build_command() + ["getblock", str(blockhash)]
        if verbosity is not None:
            command.append(str(verbosity))

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

    def getblockchaininfo(self):
        """
        Get various state details about the current blockchain/chain processing.

        Args:
            None

        Returns:
            dict | str:
                - On success: a dictionary with chain status fields (e.g., chain, blocks, headers, bestblockhash, difficulty, softforks, warnings, etc.).
                - If the daemon returns non-JSON text: the raw string.
                - On error: "Error: <message>".

        Example:
            >>> rpc.getblockchaininfo()
        """
        command = self._build_command() + ["getblockchaininfo"]

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

    def getblockcount(self):
        """
        Get the number of blocks in the longest blockchain.

        Args:
            None

        Returns:
            int | str:
                - On success: the current block count as an integer.
                - If the daemon returns non-JSON text: the raw string.
                - On error: "Error: <message>".

        Example:
            >>> rpc.getblockcount()
        """
        command = self._build_command() + ["getblockcount"]

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



    def getblockhash(self, height):
        """
        Get the block hash at a specific height in the best blockchain.

        Args:
            height (int): The block height (index) to query.

        Returns:
            str:
                - On success: the block hash string.
                - On error: "Error: <message>".

        Example:
            >>> rpc.getblockhash(1000)
        """
        command = self._build_command() + ["getblockhash", str(height)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return out or "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getblockhashes(self, high, low, no_orphans=None, logical_times=None):
        """
        Return block hashes within a timestamp range.

        Args:
            high (int): Newer block timestamp.
            low (int): Older block timestamp.
            no_orphans (bool | None, optional): If True, include only main-chain blocks.
            logical_times (bool | None, optional): If True, include logical timestamps.

        Returns:
            list | str: Parsed list (hash strings or objects when logical_times=True),
            or "Error: <message>".

        Example:
            >>> rpc.getblockhashes(1231614698, 1231024505, no_orphans=True)
        """
        args = ["getblockhashes", str(int(high)), str(int(low))]

        # Only include options if caller provided at least one flag
        if (no_orphans is not None) or (logical_times is not None):
            opts = {}
            if no_orphans is not None:
                opts["noOrphans"] = bool(no_orphans)
            if logical_times is not None:
                opts["logicalTimes"] = bool(logical_times)
            args.append(json.dumps(opts))

        command = self._build_command() + args
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out or "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getblockheader(self, block_hash, verbose=True):
        """
        Fetch a block header by hash.

        Args:
            block_hash (str): The block hash.
            verbose (bool, optional): True (default) → parsed dict. False → hex string.

        Returns:
            dict | str: Dict when verbose=True; hex string when verbose=False; or "Error: <message>".

        Example:
            >>> rpc.getblockheader("00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09")
        """
        args = ["getblockheader", str(block_hash)]
        if verbose is not None:
            args.append("true" if bool(verbose) else "false")

        command = self._build_command() + args
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()

            if not bool(verbose):
                return out or "No data returned."

            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out or "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getchaintips(self):
        """
        List all known tips in the block tree (main tip and orphaned branches).

        Args:
            None

        Returns:
            list | str: Parsed list of tip objects, or "Error: <message>".

        Example:
            >>> rpc.getchaintips()
        """
        command = self._build_command() + ["getchaintips"]
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return out or "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getchaintxstats(self, nblocks=None, blockhash=None):
        """
        Compute statistics about total count and rate of transactions over a window.

        Args:
            nblocks (int | None, optional): Size of the window in blocks. If None, daemon uses its default (≈ one month).
            blockhash (str | None, optional): Hash of the block that ends the window. If provided without
                `nblocks`, a positional placeholder is inserted for alignment.

        Returns:
            dict | str: Parsed stats dictionary on success; or "Error: <message>".

        Example:
            >>> rpc.getchaintxstats(2016)
        """
        args = ["getchaintxstats"]

        # Positional handling:
        # - If only nblocks is provided -> [nblocks]
        # - If only blockhash is provided -> ["", blockhash] (keep position for nblocks)
        # - If both provided -> [nblocks, blockhash]
        if nblocks is not None and blockhash is None:
            args.append(str(int(nblocks)))
        elif nblocks is None and blockhash is not None:
            args.extend(["", str(blockhash)])
        elif nblocks is not None and blockhash is not None:
            args.extend([str(int(nblocks)), str(blockhash)])
        # else: neither provided -> just the RPC name

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            try:
                return json.loads(out) if out else "No data returned."
            except json.JSONDecodeError:
                return out or "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getdifficulty(self):
        """
        Return the current proof-of-work difficulty as a multiple of the minimum.

        Args:
            None

        Returns:
            float | str: Difficulty value on success, or "Error: <message>" on failure.

        Example:
            >>> rpc.getdifficulty()
        """
        command = self._build_command() + ["getdifficulty"]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            try:
                # Difficulty should parse cleanly as a number
                return json.loads(out) if out else "No data returned."
            except json.JSONDecodeError:
                return float(out) if out else "No data returned."
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def getmempoolancestors(self, txid, verbose=None):
        """
        Return all in-mempool ancestors for the given transaction.

        Args:
            txid (str): The transaction id (must currently be in the mempool).
            verbose (bool | None, optional): If True, return a dict keyed by txid with stats;
                if False, return a list of ancestor txids. Defaults to False.

        Returns:
            list[str] | dict | str: Parsed JSON (list or dict) on success, or
            "Error: <message>" on failure.

        Example:
            >>> rpc.getmempoolancestors("mytxid")              # → ['txid1', 'txid2', ...]
            >>> rpc.getmempoolancestors("mytxid", True)       # → {'txid1': {...}, ...}
        """
        args = ["getmempoolancestors", str(txid)]

        # Convert None to daemon default (False) to keep positional alignment consistent.
        use_verbose = False if verbose is None else bool(verbose)
        args.append("true" if use_verbose else "false")

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

    def getmempooldescendants(self, txid, verbose=None):
        """
        Return all in-mempool descendants for the given transaction.

        Args:
            txid (str): The transaction id (must currently be in the mempool).
            verbose (bool | None, optional): If True, return a dict keyed by txid with stats;
                if False, return a list of descendant txids. Defaults to False.

        Returns:
            list[str] | dict | str: Parsed JSON (list or dict) on success, or
            "No data returned." / "Error: <message>" on failure.

        Example:
            >>> rpc.getmempooldescendants("mytxid")            # → ['txid1', 'txid2', ...]
            >>> rpc.getmempooldescendants("mytxid", True)      # → {'txid1': {...}, ...}
        """
        args = ["getmempooldescendants", str(txid)]

        # Convert None to daemon default (False) and pass explicitly to keep positions aligned.
        use_verbose = False if verbose is None else bool(verbose)
        args.append("true" if use_verbose else "false")

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

    def getmempoolentry(self, txid):
        """
        Return mempool data for the given transaction.

        Args:
            txid (str): The transaction id (must currently be in the mempool).

        Returns:
            dict | str: Parsed JSON object with mempool stats on success.
            If the node returns non-JSON text, that raw text is returned.
            On empty output: "No data returned."
            On failure: "Error: <message>"

        Example:
            >>> rpc.getmempoolentry("mytxid")
        """
        command = self._build_command() + ["getmempoolentry", str(txid)]

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

    def getmempoolinfo(self):
        """
        Return details on the active state of the mempool.

        Args:
            None

        Returns:
            dict | str: Parsed JSON object with mempool statistics on success.
            If the node returns non-JSON text, that raw text is returned.
            On empty output: "No data returned."
            On failure: "Error: <message>"

        Example:
            >>> rpc.getmempoolinfo()
        """
        command = self._build_command() + ["getmempoolinfo"]

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

    def getrawmempool(self, verbose=None):
        """
        Return the mempool contents.

        Args:
            verbose (bool | None, optional):
                - True  → return a dict keyed by txid with detailed entry data.
                - False → return a list of txids.
                - None  → omit the arg so the node uses its default (False).

        Returns:
            dict | list | str:
                Parsed JSON (dict or list) on success.
                Raw text if the node returns non-JSON.
                "No data returned." if stdout is empty.
                "Error: <message>" on failure.

        Example:
            >>> rpc.getrawmempool()
            >>> rpc.getrawmempool(verbose=True)
        """
        args = ["getrawmempool"]
        if verbose is not None:
            args.append("true" if verbose else "false")

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

    def getspentinfo(self, txid, index):
        """
        Return information about where a specific output is spent.

        Args:
            txid (str): The transaction ID containing the output.
            index (int): The output index (vout) within the transaction.

        Returns:
            dict | str:
                Parsed JSON (dict) with spending transaction details on success.
                Raw text if the node returns non-JSON.
                "No data returned." if stdout is empty.
                "Error: <message>" on failure.

        Example:
            >>> rpc.getspentinfo("0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9", 0)
        """
        payload = {"txid": str(txid), "index": int(index)}
        command = self._build_command() + ["getspentinfo", json.dumps(payload)]

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

    def gettxout(self, txid, n, include_mempool=None):
        """
        Return details about an unspent transaction output (UTXO).

        Args:
            txid (str): The transaction ID containing the output.
            n (int): The output index (vout) within the transaction.
            include_mempool (bool, optional): Whether to include mempool transactions.
                Defaults to True if not specified. If False, excludes outputs spent in the mempool.

        Returns:
            dict | str:
                Parsed JSON (dict) with UTXO details on success.
                Raw text if the node returns non-JSON.
                "No data returned." if stdout is empty.
                "Error: <message>" on failure.

        Example:
            >>> rpc.gettxout("0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9", 1)
        """
        command = self._build_command() + ["gettxout", str(txid), str(n)]

        # Always include the third argument to preserve parameter order
        if include_mempool is None:
            command.append("true")  # default behavior
        else:
            command.append("true" if include_mempool else "false")

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

    def gettxoutproof(self, txids, blockhash=None):
        """
        Return a hex-encoded proof that the given txid(s) are included in a block.

        Args:
            txids (list[str]): One or more transaction IDs to prove inclusion for.
            blockhash (str | None, optional): Block hash to search in. If None, the node
                will try to find the tx via UTXO/txindex; providing a blockhash avoids
                needing -txindex.

        Returns:
            str:
                Hex-encoded serialized proof on success.
                "No data returned." if the node produced no output.
                "Error: <message>" on failure.

        Example:
            >>> rpc.gettxoutproof(["0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9"])
        """
        # Build args in strict positional order; include optional only if provided.
        args = ["gettxoutproof", json.dumps(list(txids))]
        if blockhash is not None:
            args.append(str(blockhash))

        command = self._build_command() + args

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            if not out:
                return "No data returned."
            # Node returns a hex string (may or may not be JSON-quoted); surface as text.
            try:
                parsed = json.loads(out)
                return parsed if isinstance(parsed, str) else str(parsed)
            except json.JSONDecodeError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def gettxoutsetinfo(self):
        """
        Return statistics about the current UTXO set (this call may take time).

        Args:
            None

        Returns:
            dict | str:
                - Parsed JSON object with UTXO set statistics on success.
                - Raw text if the node returns non-JSON.
                - "No data returned." if the node produced no output.
                - "Error: <message>" on failure.

        Example:
            >>> rpc.gettxoutsetinfo()
        """
        command = self._build_command() + ["gettxoutsetinfo"]

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

    def preciousblock(self, blockhash):
        """
        Treat a block as if it were received before other competing blocks with the same work.

        Args:
            blockhash (str): The block hash to mark as precious.

        Returns:
            str | dict:
                - Parsed JSON or raw text from the node, if any.
                - "No data returned." if the command succeeds with no output.
                - "Error: <message>" on failure.

        Example:
            >>> rpc.preciousblock("00000000c9379837...f6ed09")
        """
        command = self._build_command() + ["preciousblock", str(blockhash)]
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

    def pruneblockchain(self, height):
        """
        Prune the blockchain up to a specified block height or UNIX timestamp.

        Args:
            height (int):
                The block height or UNIX timestamp to prune up to.
                - If a block height is provided, blocks up to that height will be pruned.
                - If a UNIX timestamp is provided, blocks with block time at least 2 hours older than the timestamp will be pruned.

        Returns:
            int | str:
                - The height of the last block pruned, if successful.
                - "Error: <message>" on failure.

        Example:
            >>> rpc.pruneblockchain(1000)
        """
        command = self._build_command() + ["pruneblockchain", str(height)]
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            try:
                return int(out)
            except ValueError:
                return out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def savemempool(self):
        """
        Dump the current mempool to disk.

        Returns:
            str:
                - An empty string ("") if successful.
                - "Error: <message>" on failure.

        Example:
            >>> rpc.savemempool()
        """
        command = self._build_command() + ["savemempool"]
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            return (result.stdout or "").strip()
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def verifychain(self, checklevel=None, nblocks=None):
        """
        Verify the blockchain database.

        Args:
            checklevel (int, optional):
                The thoroughness of the block verification (0–4).
                Defaults to 3 if omitted.
            nblocks (int, optional):
                The number of blocks to verify.
                Defaults to 6. Use 0 to verify all blocks.

        Returns:
            bool:
                - True if the blockchain verified successfully.
                - False otherwise.
                - "Error: <message>" on failure.

        Example:
            >>> rpc.verifychain()
            >>> rpc.verifychain(checklevel=4, nblocks=100)
        """
        optional_spec = [
            str(checklevel) if checklevel is not None else None,
            str(nblocks) if nblocks is not None else None,
        ]

        while optional_spec and optional_spec[-1] is None:
            optional_spec.pop()

        command = self._build_command() + ["verifychain"] + [
            arg if arg is not None else "" for arg in optional_spec
        ]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return json.loads(out.lower()) if out.lower() in ["true", "false"] else out
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()

    def verifytxoutproof(self, proof):
        """
        Verify that a proof points to a transaction in a block.

        Args:
            proof (str):
                The hex-encoded proof generated by `gettxoutproof`.

        Returns:
            list:
                A list of transaction IDs (`txid`) that the proof commits to.
                Returns an empty list if the proof is invalid.
                Returns "Error: <message>" if verification fails.

        Example:
            >>> rpc.verifytxoutproof("hex_proof_string")
        """
        command = self._build_command() + ["verifytxoutproof", str(proof)]

        try:
            result = run(command, stdout=PIPE, stderr=PIPE, text=True, check=True)
            out = (result.stdout or "").strip()
            return json.loads(out)
        except Exception as e:
            return f"Error: {getattr(e, 'stderr', str(e)) or str(e)}".strip()
