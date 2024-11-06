#!pip install python-dotenv
#!pip install pyngrok --upgrade
#!pip install pinata-python
# !ngrok authtoken 2le3rm8srOecz9Z9SBy4oVdQ4Yh_27W3UyDpgB7ua7uUV5a9j #Without "" marks
from pickle import STRING
from asyncio import transports
import datetime
import json
import hashlib
from flask import Flask, jsonify, render_template
from pyngrok import ngrok

# Ajouter votre clé d'authentification ngrok ici
ngrok.set_auth_token('Token')  # Remplacez par votre authtoken

class Blockchain:
    __number : int
    def __init__(self):
        self.__number = 1  # Initialiser le numéro de la blockchain
        self.chain = []
        self.transactions = []  # Liste des transactions en attente
        self.create_blockchain(proof=1, previous_hash='0')

    def create_blockchain(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions  # Inclure les transactions dans le bloc
        }
        self.transactions = []  # Réinitialiser la liste des transactions en attente après le minage
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            current_proof = block['proof']
            hash_operation = hashlib.sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        # Retourner l'index du prochain bloc qui inclura la transaction
        return self.get_previous_block()['index'] + 1

    def get_number(self):
        # Méthode pour accéder au numéro de la blockchain
        return self.__number

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def index():
    response = {
      'message': "Blockchain is running with ngrok",
      'number': blockchain.get_number(),
    }
    return jsonify(response), 200

@app.route('/mine_block/<sender>/<recipient>/<amount>', methods=['GET'])
def mine_block(sender: STRING, recipient: STRING, amount: int):
    # Ajouter la transaction avant de miner le bloc
    blockchain.add_transaction(sender, recipient, float(amount))

    # Miner le block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_blockchain(proof, previous_hash)
    response = {
        'message': 'Block mined!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions'],
        'total_blocks_mined': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
    'length': len(blockchain.chain)}
    return jsonify(response), 200

#@app.route('/valid/<chain>', methods=['GET'])
#def valid(chain):
#    response = {'valid': blockchain.is_chain_valid(json.loads(chain))
#    return jsonify(response), 200

# Lancer le serveur Flask et ngrok
if __name__ == '__main__':
    # Lancer ngrok pour exposer le port 5000
    public_url = ngrok.connect(5000)  # Assurez-vous que ce port est le même que celui sur lequel Flask tourne
    print(f"Votre application est accessible publiquement ici : {public_url}")

    # Démarrer l'application Flask
    app.run(host='127.0.0.1', port=5000)  # Assurez-vous que Flask écoute sur 0.0.0.0