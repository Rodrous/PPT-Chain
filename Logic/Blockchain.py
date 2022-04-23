import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from time import time
from collections import OrderedDict
import hashlib


@dataclass
class BlockChain:
    chain: List = field(default_factory=list)
    current_transaction: List = field(default_factory=list)

    def new_block(self, proof: int, previous_hash: Optional[str]) -> Dict:
        block: OrderedDict = OrderedDict()
        block["index"] = len(self.chain) + 1
        block["timestamp"] = time(),
        block["transaction"] = self.current_transaction,
        block["proof"] = proof,
        block["previous_hash"] = previous_hash or self.hash(self.chain[-1])

        self.current_transaction = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender: str, receiver: str, amount: int) -> int:
        self.current_transaction.append(
            {
                "sender": sender,
                "receiver": receiver,
                "amount": amount
            }
        )

        return self.last_block["index"] + 1

    @property
    def last_block(self):
        if not self.chain:
            self.new_block(proof=100, previous_hash="1")
        return self.chain[-1]

    def hash(self, block: OrderedDict) -> str:
        jsondump = json.dumps(block).encode()
        return hashlib.sha256(jsondump).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        proof: int = 0
        while not self.validate_proof(last_proof, proof):
            proof += 1
        return proof

    def validate_proof(self, lastProof: int, proof: int) -> bool:
        guess = f"{lastProof}{proof}".encode()
        hash_val = hashlib.sha256(guess).hexdigest()
        return hash_val[:5] == "10000"
