# Install dependencies before running:
# pip install python-dotenv pyngrok pinata-python flask

from flask import Flask, jsonify  # Flask for the web application, jsonify for JSON responses
from pyngrok import ngrok  # Ngrok to expose the local server publicly
import datetime  # For timestamps in the blockchain
import json  # To serialize data for hashing and responses
import hashlib  # To generate secure hash values for blocks

# Add your ngrok authentication token below
NGROK_AUTH_TOKEN = "2le3rm8srOecz9Z9SBy4oVdQ4Yh_27W3UyDpgB7ua7uUV5a9j"  # Replace with your actual ngrok auth token
ngrok.set_auth_token(NGROK_AUTH_TOKEN)  # Authenticate ngrok with the provided token

# Blockchain class handles all blockchain operations
class Blockchain:
    def __init__(self):
        """
        Initialize the blockchain with:
        - An empty chain to hold blocks.
        - A transactions list to hold pending transactions.
        - The genesis block created during initialization.
        """
        self.chain = []  # List to store all blocks
        self.transactions = []  # List to store transactions pending inclusion in a block
        self.create_blockchain(proof=1, previous_hash='0')  # Create the genesis block

    def create_blockchain(self, proof, previous_hash):
        """
        Creates a new block and appends it to the blockchain.
        Each block contains:
        - Index: Position in the chain.
        - Timestamp: Time of block creation.
        - Proof: Proof of work value.
        - Previous hash: Hash of the previous block.
        - Transactions: List of transactions included in the block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []  # Clear pending transactions after including them in the block
        self.chain.append(block)  # Append the new block to the chain
        return block

    def get_previous_block(self):
        """
        Returns the last block in the chain.
        """
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        """
        Perform the proof of work algorithm.
        Finds a number (new_proof) such that the hash of the operation is valid (starts with 4 leading zeros).
        """
        new_proof = 1  # Initialize proof value
        check_proof = False
        while not check_proof:
            # Hash operation with the formula (new_proof^2 - previous_proof^2)
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':  # Check if the hash starts with 4 leading zeros
                check_proof = True
            else:
                new_proof += 1  # Increment and try again
        return new_proof

    def hash(self, block):
        """
        Creates a SHA-256 hash of a block.
        The block is serialized into JSON format to ensure consistent hashing.
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        """
        Validates the blockchain:
        - Checks if the hash of each block matches its `previous_hash` in the next block.
        - Verifies that the proof of work is valid for each block.
        """
        previous_block = chain[0]  # Start with the genesis block
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # Check if previous_hash matches the hash of the previous block
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # Verify the proof of work
            previous_proof = previous_block['proof']
            current_proof = block['proof']
            hash_operation = hashlib.sha256(
                str(current_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':  # Invalid proof
                return False
            # Move to the next block
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        """
        Adds a new transaction to the pending transactions list.
        Each transaction contains:
        - Sender: The address of the sender.
        - Receiver: The address of the receiver.
        - Amount: The transaction amount.
        """
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        # Return the index of the next block to include this transaction
        return self.get_previous_block()['index'] + 1

# Flask App for the Blockchain API
app = Flask(__name__)
blockchain = Blockchain()  # Create an instance of the blockchain

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint. Provides a message and total number of blocks in the blockchain.
    """
    response = {
        'message': "Blockchain is running with ngrok",
        'total_blocks': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/mine_block/<sender>/<recipient>/<amount>', methods=['GET'])
def mine_block(sender, recipient, amount):
    """
    Mines a new block:
    - Adds a transaction to the pending transactions.
    - Performs proof of work.
    - Creates a new block with the proof and previous block's hash.
    """
    blockchain.add_transaction(sender, recipient, float(amount))  # Add the transaction
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)  # Find a valid proof
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_blockchain(proof, previous_hash)  # Create the new block
    response = {
        'message': 'Block mined successfully!',
        'block': block,
        'total_blocks': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    """
    Returns the full blockchain.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    """
    Checks if the blockchain is valid.
    """
    valid = blockchain.is_chain_valid(blockchain.chain)
    response = {'is_chain_valid': valid}
    return jsonify(response), 200

if __name__ == '__main__':
    # Start ngrok to expose the Flask app publicly
    public_url = ngrok.connect(5000)
    print(f"Your application is publicly accessible here: {public_url}")

    # Start the Flask server on localhost
    app.run(host='127.0.0.1', port=5000)
