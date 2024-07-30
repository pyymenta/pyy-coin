import argparse
from blockchain import Blockchain
from flask import Flask, jsonify, request
from uuid import uuid4
from argparse import ArgumentParser

app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods = ['GET'])
def mine():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['nounce']
    proof = blockchain.mine_block(previous_proof)
    previous_hash = blockchain.generate_block_hash(previous_block)
    newBlock = blockchain.generate_block(proof, previous_hash)

    response = {
        'message': 'Block mined!',
        'id': newBlock['incremental_id'],
        'timestamp': newBlock['timestamp'],
        'proof': newBlock['nounce'],
        'previous_hash': newBlock['previous_hash'],
        'transactions': newBlock['transactions']
    }

    return jsonify(response), 200

@app.route('/chain', methods = ['GET'])
def chain():
    response = {
        'blockchain': blockchain.blockchain,
        'length': len(blockchain.blockchain),
    }

    return jsonify(response), 200

@app.route('/check_validity', methods = ['GET'])
def check_validity():
    is_valid = blockchain.verify_blockchain(blockchain.blockchain)

    if is_valid:
        response = { 'message': 'All good. The Blockchain is valid.' }
    else:
        response = { 'message': 'Oh no! Something is wrong.' }

    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    transaction_payload = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']

    if not all(key in transaction_payload for key in transaction_keys):
        return 'All arguments is required!', 400

    transaction = blockchain.add_transaction(
        transaction_payload['sender'],
        transaction_payload['receiver'],
        transaction_payload['amount']
    )

    response = { 'message': f'This transaction will be added to the block! {transaction}'}

    return jsonify(response), 201

@app.route('/add_node', methods = ['POST'])
def add_node():
    request_payload = request.get_json()
    nodes = request_payload.get('nodes')

    if nodes is None:
        return "No nodes are found", 400

    for node in nodes:
        blockchain.add_node(node)

    response = {
        "message": "Node added to the network!",
        "total_nodes": list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/replace_blockchain', methods = ['GET'])
def replace_blockchain():
    is_replaced = blockchain.replace_chain()

    if is_replaced:
        response = {
            'message': 'Blockchain replaced!',
            'new_blockchain': blockchain.blockchain,
        }
    else:
        response = {
            'message': 'Blockchain was not replaced!',
            'current_blockchain': blockchain.blockchain,
        }

    return jsonify(response), 201

parser = argparse.ArgumentParser(description='A simple example of argparse.')
parser.add_argument('--port', type=int, default=5000, help='Port number to run the server on')

args = parser.parse_args()

app.run(host = '0.0.0.0', port = args.port)
