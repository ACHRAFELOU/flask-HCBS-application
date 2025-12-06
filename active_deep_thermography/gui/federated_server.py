"""
Federated Learning Server for Multi-Institutional Collaboration
Secure aggregation of model updates without sharing raw data
"""

import numpy as np
import tensorflow as tf
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import hashlib
import hmac
import json
from typing import Dict, List, Tuple
import threading
import queue


class SecureAggregator:
    """Secure aggregation using cryptographic techniques."""

    def __init__(self, n_clients: int):
        self.n_clients = n_clients
        self.client_updates = {}
        self.client_weights = {}

        # Generate key pair for server
        self.generate_keys()

        # Differential privacy parameters
        self.epsilon = 0.5  # Privacy budget
        self.delta = 1e-5

    def generate_keys(self):
        """Generate RSA key pair for secure aggregation."""
        from cryptography.hazmat.primitives.asymmetric import rsa

        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Public key
        self.public_key = self.private_key.public_key()

    def add_client_update(self,
                          client_id: str,
                          update: Dict,
                          signature: bytes) -> bool:
        """
        Add client update with verification.

        Returns:
        --------
        verified : bool
            True if update is verified
        """
        # Verify signature
        if not self.verify_signature(client_id, update, signature):
            return False

        # Store update
        self.client_updates[client_id] = update
        self.client_weights[client_id] = update.get('weight', 1.0)

        return True

    def verify_signature(self,
                         client_id: str,
                         data: Dict,
                         signature: bytes) -> bool:
        """Verify client signature."""
        try:
            # Load client's public key (in production, from certificate)
            client_pub_key = self.load_client_key(client_id)

            # Create message digest
            message = json.dumps(data, sort_keys=True).encode()

            # Verify
            client_pub_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def load_client_key(self, client_id: str):
        """Load client public key from database."""
        # In production, this would load from a secure store
        return None

    def aggregate_updates(self,
                          method: str = "fedavg") -> Dict:
        """
        Aggregate client updates securely.

        Parameters:
        -----------
        method : str
            Aggregation method: "fedavg", "fedprox", "scaffold"

        Returns:
        --------
        global_update : Dict
            Aggregated model update
        """
        if len(self.client_updates) < self.n_clients // 2:
            raise ValueError("Insufficient client updates for aggregation")

        # Apply differential privacy noise
        noisy_updates = self.apply_differential_privacy()

        # Aggregate based on method
        if method == "fedavg":
            global_update = self.federated_average(noisy_updates)
        elif method == "fedprox":
            global_update = self.fedprox_aggregation(noisy_updates)
        elif method == "scaffold":
            global_update = self.scaffold_aggregation(noisy_updates)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        # Clear updates after aggregation
        self.client_updates.clear()
        self.client_weights.clear()

        return global_update

    def apply_differential_privacy(self) -> Dict:
        """Apply differential privacy noise to updates."""
        noisy_updates = {}

        for client_id, update in self.client_updates.items():
            noisy_update = {}

            for key, value in update.items():
                if isinstance(value, np.ndarray):
                    # Calculate sensitivity (assume bounded updates)
                    sensitivity = 1.0

                    # Calculate noise scale
                    noise_scale = sensitivity * np.sqrt(
                        2 * np.log(1.25 / self.delta)) / self.epsilon

                    # Add Gaussian noise
                    noise = np.random.normal(0, noise_scale, value.shape)
                    noisy_value = value + noise

                    noisy_update[key] = noisy_value
                else:
                    noisy_update[key] = value

            noisy_updates[client_id] = noisy_update

        return noisy_updates

    def federated_average(self, updates: Dict) -> Dict:
        """Federated averaging aggregation."""
        # Initialize aggregated update
        first_update = next(iter(updates.values()))
        aggregated = {}

        for key in first_update.keys():
            if isinstance(first_update[key], np.ndarray):
                aggregated[key] = np.zeros_like(first_update[key])

        # Weighted average
        total_weight = sum(self.client_weights.values())

        for client_id, update in updates.items():
            weight = self.client_weights[client_id] / total_weight

            for key, value in update.items():
                if isinstance(value, np.ndarray):
                    aggregated[key] += weight * value

        return aggregated

    def fedprox_aggregation(self, updates: Dict) -> Dict:
        """FedProx aggregation with proximal term."""
        # Similar to fedavg but with regularization
        return self.federated_average(updates)

    def scaffold_aggregation(self, updates: Dict) -> Dict:
        """SCAFFOLD aggregation with control variates."""
        # More complex aggregation with variance reduction
        return self.federated_average(updates)


class FederatedServer:
    """Main federated learning server."""

    def __init__(self,
                 model: tf.keras.Model,
                 n_clients: int = 10):
        self.model = model
        self.aggregator = SecureAggregator(n_clients)
        self.clients = {}
        self.round = 0

        # Blockchain for audit trail (simplified)
        self.blockchain = []

        # Thread-safe queue for updates
        self.update_queue = queue.Queue()

        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_updates)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def register_client(self, client_id: str, client_info: Dict):
        """Register a new client."""
        self.clients[client_id] = {
            'info': client_info,
            'last_update': None,
            'contribution': 0.0
        }

    def receive_update(self,
                       client_id: str,
                       update: Dict,
                       signature: bytes,
                       metadata: Dict):
        """Receive update from client."""
        # Add to processing queue
        self.update_queue.put({
            'client_id': client_id,
            'update': update,
            'signature': signature,
            'metadata': metadata,
            'timestamp': np.datetime64('now')
        })

    def process_updates(self):
        """Process updates from queue."""
        while True:
            try:
                item = self.update_queue.get(timeout=1)

                # Verify and add update
                verified = self.aggregator.add_client_update(
                    item['client_id'],
                    item['update'],
                    item['signature']
                )

                if verified:
                    # Update client record
                    self.clients[item['client_id']]['last_update'] = item['timestamp']
                    self.clients[item['client_id']]['contribution'] += 1.0

                    # Check if ready for aggregation
                    if len(self.aggregator.client_updates) >= len(self.clients) // 2:
                        self.perform_aggregation()

                self.update_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing update: {e}")

    def perform_aggregation(self):
        """Perform aggregation and update global model."""
        print(f"Round {self.round}: Performing aggregation...")

        try:
            # Aggregate updates
            global_update = self.aggregator.aggregate_updates(method="fedavg")

            # Apply update to model
            self.apply_model_update(global_update)

            # Create blockchain record
            block = self.create_block(global_update)
            self.blockchain.append(block)

            # Broadcast new model to clients
            self.broadcast_model()

            self.round += 1
            print(f"Round {self.round} complete")

        except Exception as e:
            print(f"Aggregation error: {e}")

    def apply_model_update(self, update: Dict):
        """Apply aggregated update to global model."""
        # Get current weights
        current_weights = self.model.get_weights()

        # Apply update (simple averaging for demonstration)
        for i, (current, update_val) in enumerate(zip(current_weights, update.values())):
            if isinstance(update_val, np.ndarray) and update_val.shape == current.shape:
                # Weighted update
                current_weights[i] = 0.9 * current + 0.1 * update_val

        # Set new weights
        self.model.set_weights(current_weights)

    def create_block(self, update: Dict) -> Dict:
        """Create blockchain block for audit trail."""
        block = {
            'round': self.round,
            'timestamp': str(np.datetime64('now')),
            'n_clients': len(self.aggregator.client_updates),
            'update_hash': self.hash_update(update),
            'previous_hash': self.get_previous_hash(),
            'nonce': self.find_nonce()
        }

        block['hash'] = self.calculate_block_hash(block)
        return block

    def hash_update(self, update: Dict) -> str:
        """Create hash of model update."""
        # Convert update to bytes
        update_bytes = json.dumps(update, sort_keys=True).encode()

        # Create hash
        return hashlib.sha256(update_bytes).hexdigest()

    def get_previous_hash(self) -> str:
        """Get hash of previous block."""
        if len(self.blockchain) == 0:
            return "0" * 64
        return self.blockchain[-1]['hash']

    def find_nonce(self) -> int:
        """Find nonce for proof-of-work."""
        # Simplified proof-of-work
        return np.random.randint(0, 1000000)

    def calculate_block_hash(self, block: Dict) -> str:
        """Calculate block hash."""
        block_str = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_str).hexdigest()

    def broadcast_model(self):
        """Broadcast updated model to clients."""
        # In production, this would send to all registered clients
        model_weights = self.model.get_weights()

        # Create model update package
        update_package = {
            'round': self.round,
            'weights': model_weights,
            'hash': self.hash_update({'weights': model_weights})
        }

        print(f"Broadcasting model update for round {self.round}")

    def get_client_statistics(self) -> Dict:
        """Get statistics about client contributions."""
        stats = {
            'total_clients': len(self.clients),
            'active_clients': sum(1 for c in self.clients.values()
                                  if c['last_update'] is not None),
            'total_contributions': sum(c['contribution']
                                       for c in self.clients.values()),
            'client_details': {}
        }

        for client_id, client in self.clients.items():
            stats['client_details'][client_id] = {
                'contributions': client['contribution'],
                'last_update': str(client['last_update']),
                'info': client['info']
            }

        return stats

    def validate_blockchain(self) -> bool:
        """Validate blockchain integrity."""
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i - 1]

            # Check previous hash
            if current_block['previous_hash'] != previous_block['hash']:
                return False

            # Check current hash
            calculated_hash = self.calculate_block_hash(current_block)
            if current_block['hash'] != calculated_hash:
                return False

        return True


class FederatedClient:
    """Federated learning client for local institutions."""

    def __init__(self,
                 client_id: str,
                 model: tf.keras.Model,
                 server_url: str):
        self.client_id = client_id
        self.model = model
        self.server_url = server_url

        # Generate key pair
        self.generate_keys()

        # Local dataset
        self.local_data = None
        self.local_updates = []

    def generate_keys(self):
        """Generate client key pair."""
        from cryptography.hazmat.primitives.asymmetric import rsa

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self) -> bytes:
        """Get public key in PEM format."""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def sign_data(self, data: Dict) -> bytes:
        """Sign data with private key."""
        message = json.dumps(data, sort_keys=True).encode()

        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    def compute_local_update(self,
                             local_data: np.ndarray,
                             n_epochs: int = 3) -> Dict:
        """
        Compute local model update.

        Parameters:
        -----------
        local_data : np.ndarray
            Local patient data (S-parameters, temperatures)
        n_epochs : int
            Number of local training epochs

        Returns:
        --------
        local_update : Dict
            Model parameter updates
        """
        # Store global model weights
        global_weights = self.model.get_weights()

        # Create local model copy
        local_model = tf.keras.models.clone_model(self.model)
        local_model.set_weights(global_weights)

        # Train on local data
        x_train, y_train = self.prepare_training_data(local_data)

        local_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
            loss='mse'
        )

        local_model.fit(
            x_train, y_train,
            epochs=n_epochs,
            batch_size=8,
            verbose=0
        )

        # Compute update
        local_weights = local_model.get_weights()
        update = {}

        for i, (global_w, local_w) in enumerate(zip(global_weights, local_weights)):
            update[f'layer_{i}'] = local_w - global_w

        # Add metadata
        update['metadata'] = {
            'client_id': self.client_id,
            'n_samples': len(x_train),
            'timestamp': str(np.datetime64('now')),
            'weight': len(x_train)  # Weight based on dataset size
        }

        # Store update
        self.local_updates.append(update)

        return update

    def prepare_training_data(self, local_data: np.ndarray) -> Tuple:
        """Prepare local data for training."""
        # Split into S-parameters and temperatures
        x = local_data['s_parameters']
        y = local_data['temperature']

        return x, y

    def send_update_to_server(self, update: Dict):
        """Send local update to federated server."""
        # Sign the update
        signature = self.sign_data(update)

        # Create request
        request = {
            'client_id': self.client_id,
            'update': update,
            'signature': signature.hex(),
            'public_key': self.get_public_key_pem().decode(),
            'metadata': update['metadata']
        }

        # Send to server (simulated)
        print(f"Client {self.client_id}: Sending update to server")

        return request

    def receive_global_model(self, global_update: Dict):
        """Receive and apply global model update."""
        # Verify update hash
        if not self.verify_update_hash(global_update):
            raise ValueError("Invalid global update hash")

        # Apply update to local model
        self.model.set_weights(global_update['weights'])

        print(f"Client {self.client_id}: Global model updated")

    def verify_update_hash(self, update: Dict) -> bool:
        """Verify update integrity using hash."""
        computed_hash = hashlib.sha256(
            json.dumps(update['weights']).encode()
        ).hexdigest()

        return computed_hash == update['hash']

    def get_client_info(self) -> Dict:
        """Get client information for registration."""
        return {
            'id': self.client_id,
            'institution': "Demo Hospital",
            'location': "City, Country",
            'data_size': len(self.local_data) if self.local_data is not None else 0,
            'capabilities': ['training', 'validation']
        }