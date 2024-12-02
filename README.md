# Blockchain with Flask and ngrok

This is a simple blockchain implementation written in Python. The application uses Flask to create a RESTful API for interacting with the blockchain and ngrok to expose the local server to the internet.

---

## Features

- **Blockchain Implementation**: A basic blockchain with Proof of Work (PoW) and transaction management.
- **REST API**: Provides endpoints to mine blocks, retrieve the blockchain, and validate its integrity.
- **ngrok Integration**: Exposes the application publicly so it can be accessed from anywhere.

---

## Requirements

Before running the application, ensure you have the following installed:

- **Python 3.8+**
- Required libraries: `python-dotenv`, `pyngrok`, `pinata-python`, and `flask`

Install the dependencies using pip:

```bash
pip install python-dotenv pyngrok pinata-python flask


## API Endpoints

### 1. Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Description**: Displays a welcome message and the total number of blocks in the blockchain.

#### Example Response:
```json
{
    "message": "Blockchain is running with ngrok",
    "total_blocks": 1
}

### 2. Mine a Block

- **URL**: `/mine_block/<sender>/<recipient>/<amount>`
- **Method**: `GET`
- **Description**: Mines a new block. Before mining, it adds a transaction to the pending transactions list.

#### Parameters:
- `sender` (string): Name or ID of the sender.
- `recipient` (string): Name or ID of the recipient.
- `amount` (float): Amount to transfer.

#### Example Request:
/mine_block/Alice/Bob/10.5

#### Example Response:
```json
{
    "message": "Block mined successfully!",
    "block": {
        "index": 2,
        "timestamp": "2024-12-02 14:00:00",
        "proof": 12345,
        "previous_hash": "abcd1234...",
        "transactions": [
            {
                "sender": "Alice",
                "receiver": "Bob",
                "amount": 10.5
            }
        ]
    },
    "total_blocks": 2
}
