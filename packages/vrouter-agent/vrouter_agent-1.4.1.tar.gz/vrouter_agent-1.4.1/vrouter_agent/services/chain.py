from enum import Enum
import os
import re
import mcrpc
from loguru import logger
import mcrpc.exceptions
from vrouter_agent.utils.cli import run_command
from cryptography.fernet import Fernet
from vrouter_agent.core.config import settings

class Chain:
    """
    Chain class 
    """
    def __init__(self, chain: str, user: str):
        self.chain = chain
        self.user = user
        self.chain_dir = os.path.join(f"/home/{user}/.multichain", chain)
        self.client = self.get_multichain_client()
        self.rpcuser = None
        self.rpcpasswd = None
        self.rpcport = None

    def subscribe_to_stream(self, stream: str) -> bool:
        try:
            logger.debug(f"Subscribing to stream {stream}...")
            self.client.subscribe(stream)
            return True

        except mcrpc.exceptions.RpcError as error:
            logger.exception("Error occurred: " + str(error))

        return False

    def is_subscribe_to_stream(self, stream: str)-> bool:
        try:
            stream = self.client.liststreams(stream)
            return stream[0].get("subscribed", False)

        except mcrpc.exceptions.RpcError as error:
            logger.exception("Error occurred: " + str(error))

        return False


    def is_running(self) -> bool:
        """
        Checks if the Multichain daemon is running for the specified chain.
        This method attempts to run the `multichain-cli` command with the `getinfo`
        argument to check the status of the Multichain daemon. If the command
        executes successfully (returns a code of 0), it indicates that the daemon
        is running.
        Returns:
            bool: True if the Multichain daemon is running, False otherwise.
        Logs:
            Logs an error message if the Multichain daemon is not running or if
            an IOError or KeyError occurs during the execution of the command.
        """

        try:
            _, code = run_command(
                [
                    "sudo",
                    "-u",
                    self.user,
                    "/usr/local/bin/multichain-cli",
                    self.chain,
                    "getinfo",
                ],
                name="multichain-cli",
            )
            if code == 0:
                return True
            logger.error(f"Multichaind is not running for chain name {self.chain}")
            return False

        except IOError as error:
            logger.exception("Error occurred: " + str(error))

        except KeyError as error:
            logger.exception(str(error))

        return False

    def validate_credentials(self) -> bool:
        """
        Validates the credentials for connecting to the blockchain.
        This method checks if the chain directory exists and reads the
        'multichain.conf' and 'params.dat' files to extract the rpcuser,
        rpcpassword, and rpcport values.
        Returns:
            bool: True if credentials are successfully validated.
            bool: False if an error occurs during validation.
        Raises:
            IOError: If there is an error reading the files.
            KeyError: If there is an error parsing the file contents.
        """

        try:
            if not os.path.exists(self.chain_dir):
                logger.error("Chain directory not found")
                return False 

            with open(
                os.path.join(self.chain_dir, "multichain.conf"),
                "r",
                encoding="utf-8",
            ) as blockchain_file:
                for line in blockchain_file.readlines():
                    if line.startswith("rpcuser"):
                        self.rpcuser = line.split("=")[1].strip()
                    if line.startswith("rpcpassword"):
                        self.rpcpasswd = line.split("=")[1].strip()

            with open(
                os.path.join(self.chain_dir, "params.dat"),
                "r",
                encoding="utf-8",
            ) as blockchain_file:
                for line in blockchain_file.readlines():
                    if line.startswith("default-rpc-port"):
                        self.rpcport = re.findall(r"\d+", line)[0]

            return True

        except IOError as error:
            logger.exception("Error occurred: " + str(error))

        except KeyError as error:
            logger.exception(str(error))

        return False

    def get_stream_item(self, stream, txid) -> dict:
        """
        Get stream item from the blockchain
        Args:
            txid (str): txid
        Returns:
            dict: stream item
        """
        try:
            return self.client.getstreamitem(stream, txid)

        except mcrpc.exceptions.RpcError as error:
            logger.exception("Error occurred: " + str(error))

        return None

    def get_multichain_client(self) -> mcrpc.RpcClient:
        """Multichain client

        Args:
            chain (str): chain
        Returns:
            client: multichain_client object
        """
        try:
            self.validate_credentials()
            if not self.is_running():
                return None
            return mcrpc.RpcClient(
                "localhost", self.rpcport, self.rpcuser, self.rpcpasswd, False
            )

        except Exception as error:
            logger.exception("Error occurred: " + str(error))

        return None

    def encrypt_data(self, data: str) -> str:
        """Encrypt the data using the private key"""
        # convert data to bytes
        data_bytes = data.encode("utf-8")
        # encrypt the data
        key = Fernet(settings.config.global_.secret_key)
        encrypted_data = key.encrypt(data_bytes)
        return encrypted_data.hex()

      
    
class StreamItem:
    def __init__(self, data: str, txid: str):
        self.data = data
        self.txid = txid
        self.private_key = settings.config.global_.secret_key

    def get_decrypted_data(self) -> str:
        """Decrypt the data using the private key"""
        # convert data to bytes
        data = bytes.fromhex(self.data)
        # decrypt the data
        key = Fernet(self.private_key)
        decrypted_data = key.decrypt(data)
        return decrypted_data.decode("utf-8")

