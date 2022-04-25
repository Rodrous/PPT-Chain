import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Any
from time import time
from collections import OrderedDict
import hashlib
from urllib.parse import urlparse
import aiohttp


@dataclass
class BlockChain:
    chain: List = field(default_factory=list)
    current_transaction: List = field(default_factory=list)
    nodes: Set = field(default_factory=set)

    def new_block(self, proof: int, previous_hash: Optional[str]) -> Dict:
        """
        Adds a new block to the chain.
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New block
        """
        block: OrderedDict = OrderedDict()
        block["index"] = len(self.chain) + 1
        block["timestamp"] = time(),
        block["transaction"] = self.current_transaction,
        block["proof"] = proof,
        block["previous_hash"] = previous_hash or hash(self.chain[-1])

        self.current_transaction = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender: str, receiver: str, amount: int) -> int:
        """
        Creates a new transaction to go into next block
        :param sender: Address of sender
        :param receiver: Address of reciever
        :param amount: Amount
        :return: Index of the block that will hold this transaction
        """
        self.current_transaction.append(
            {
                "sender": sender,
                "receiver": receiver,
                "amount": amount
            }
        )

        return self.last_block["index"] + 1

    @property
    def last_block(self) -> Any:
        if not self.chain:
            self.new_block(proof=100, previous_hash="1")
        return self.chain[-1]

    @staticmethod
    def hash(block: OrderedDict) -> str:
        """
        Creates a SHA-256 of a Block
        :param block: Block we got from mining
        :return: Hash of the block.
        """
        jsondump = json.dumps(block).encode()
        return hashlib.sha256(jsondump).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        proof: int = 0
        while not self.validate_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def validate_proof(lastProof: int, proof: int) -> bool:
        guess = f"{lastProof}{proof}".encode()
        hash_val = hashlib.sha256(guess).hexdigest()
        return hash_val[:5] == "10000"

    def register_node(self, address: str) -> None:
        self.nodes.add(urlparse(address).netloc)

    def validate_chain(self, chain: List) -> bool:
        """
        Determines if chain is valid
        :param chain: A blockchain
        :return: True if Valid or False if not
        """

        last_block: Any = chain[0]
        current_index: int = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block["previous_hash"] is not self.hash(last_block): return False
            if not self.validate_proof(last_block["proof"], block["proof"]): return False

            last_block = block
            current_index += 1
        return True

    async def resolve_confilicts(self) -> bool:
        """
        Consensus Algorithm, it resolves conflicts by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced ,False if not
        """
        neighbours: Set = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for nodes in neighbours:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{nodes}/chain") as response:
                    if response.status in [200, 201]:
                        length_param = await response.json()
                        length = length_param["length"]
                        chain_param = await  response.json()
                        chain = chain_param["chain"]

                    if length > max_length and self.validate_chain(chain):
                        max_length = length
                        new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False
