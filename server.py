from typing import Dict, List, Any
from fastapi import FastAPI, Request, HTTPException
from Logic.Blockchain import BlockChain
from uuid import uuid4

app: FastAPI = FastAPI()
blockchainInstance: BlockChain = BlockChain()
node_identifier: str = str(uuid4()).replace("-", "")


@app.get("/mine")
async def mine() -> Dict:
    """
    Running proof of Algorithmn to get the new proof, and get reward for finding the proof
    :return:
    """
    last_block = blockchainInstance.last_block
    last_proof = last_block["proof"]
    proof_of_work = blockchainInstance.proof_of_work(last_proof)

    blockchainInstance.new_transaction(
        sender="0",
        receiver=node_identifier,
        amount=1
    )

    previous_hash = blockchainInstance.hash(last_block)
    block = blockchainInstance.new_block(proof_of_work, previous_hash)

    response = {
        "Message": "New Block Forged",
        "Index": block["index"],
        "Transactions": block["transaction"],
        "Proof": block["proof"],
        "Previous_Hash": block["previous_hash"]
    }

    return response


@app.post("/transactions/new")
async def init_transaction(request: Request) -> Dict:
    requestObject: Dict = await request.json()
    requestContent: List = [i for i in requestObject.keys()]
    required: List = ["sender", "receiver", "amount"]
    response_verifier: bool = all(i == j for i, j in zip(sorted(requestContent), sorted(required)))

    if response_verifier:
        index: int = blockchainInstance.new_transaction(requestObject["sender"], requestObject["receiver"],
                                                        requestObject["amount"])
        response = {
            "Message": f"Transaction would be added to block {index}"
        }
        return response
    else:
        raise HTTPException(400, detail="Incomplete Values")


@app.get("/chain")
async def chain() -> Dict:
    response = {
        "chain": blockchainInstance.chain,
        "length": len(blockchainInstance.chain)
    }
    return response


@app.post("/node/register")
async def register_node(request: Request) -> Dict | Exception:
    """
    Add a new node to the list of nodes
    :param request:> Address of node. Eg. 'http://localhost:5000'
    :return:
    """
    values: Any = await request.json()
    nodes: Any = values["nodes"]

    if not nodes:
        return HTTPException(400, detail="Please Supply a valid list of Nodes!")

    for node in nodes:
        blockchainInstance.register_node(node)

    response: Dict = {
        "message": "New nodes has added",
        "total_nodes": list(blockchainInstance.nodes)
    }

    return response


@app.get("/nodes/resolve")
async def consensus() -> Dict:
    replaced = blockchainInstance.resolve_confilicts()
    response: Dict = {}
    if replaced:
        response = {
            "message": "Chain was replaced",
            "new_chain": blockchainInstance.chain
        }
    else:
        response = {
            "message": "Chain authoritive",
            "chain": blockchainInstance.chain
        }

    return response
