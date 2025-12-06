"""
Hierarchical Physics-Informed Neural Network (HPINN)
Dual-stage architecture for EM and thermal reconstruction
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import tensorflow_addons as tfa
from typing import Tuple, Dict, List
import numpy as np


class PhysicsInformedLoss(keras.losses.Loss):
    """Custom loss function incorporating physical constraints."""

    def __init__(self,
                 alpha: float = 0.1,
                 beta: float = 0.01,
                 name="physics_informed_loss"):
        super().__init__(name=name)
        self.alpha = alpha  # Weight for physics loss
        self.beta = beta  # Weight for regularization
        self.mse = keras.losses.MeanSquaredError()

    def call(self, y_true, y_pred):
        # Data fidelity term
        data_loss = self.mse(y_true, y_pred)

        # Physics constraints (embedded during training)
        physics_loss = self.compute_physics_loss(y_pred)

        # Total variation regularization for smoothness
        tv_loss = self.total_variation_loss(y_pred)

        return data_loss + self.alpha * physics_loss + self.beta * tv_loss

    def compute_physics_loss(self, y_pred):
        """Compute violation of physical laws."""
        # Maxwell's equations residual
        maxwell_loss = self.maxwell_constraint(y_pred)

        # Bioheat equation residual
        bioheat_loss = self.bioheat_constraint(y_pred)

        return maxwell_loss + bioheat_loss

    def maxwell_constraint(self, E_field):
        """Check Maxwell's equations divergence condition."""
        # ∇·D = ρ (simplified for source-free region)
        divergence = tf.reduce_mean(tf.abs(tf.linalg.trace(
            tf.gradients(E_field, E_field))))
        return divergence

    def bioheat_constraint(self, T_field):
        """Check bioheat equation consistency."""
        # Simplified: check if temperature satisfies diffusion equation
        laplacian = tf.reduce_mean(tf.abs(self.laplacian_2d(T_field)))
        return laplacian

    def laplacian_2d(self, field):
        """Compute 2D Laplacian using finite differences."""
        # Using convolution with Laplacian kernel
        kernel = tf.constant([[0, 1, 0],
                              [1, -4, 1],
                              [0, 1, 0]], dtype=tf.float32)
        kernel = tf.reshape(kernel, [3, 3, 1, 1])

        if len(field.shape) == 3:
            field = tf.expand_dims(field, -1)

        return tf.nn.conv2d(field, kernel, strides=1, padding='SAME')

    def total_variation_loss(self, image):
        """Total variation regularization for smooth images."""
        diff_i = image[:, 1:, :] - image[:, :-1, :]
        diff_j = image[:, :, 1:] - image[:, :, :-1]

        tv_loss = tf.reduce_mean(tf.abs(diff_i)) + tf.reduce_mean(tf.abs(diff_j))
        return tv_loss


class EMINet(Model):
    """Electromagnetic Inversion Network - Stage 1."""

    def __init__(self,
                 input_shape: Tuple[int, int, int],
                 output_shape: Tuple[int, int, int],
                 n_filters: int = 64,
                 n_blocks: int = 4,
                 use_attention: bool = True):
        super().__init__()

        self.input_shape_ = input_shape
        self.output_shape_ = output_shape

        # Encoder
        self.encoder = self.build_encoder(n_filters, n_blocks, use_attention)

        # Bottleneck with physics embedding
        self.bottleneck = self.build_bottleneck(n_filters * 2 ** n_blocks)

        # Decoder with skip connections
        self.decoder = self.build_decoder(n_filters, n_blocks, use_attention)

        # Output layers
        self.epsilon_output = layers.Conv2D(1, 1, activation='linear',
                                            name='epsilon_output')
        self.sigma_output = layers.Conv2D(1, 1, activation='relu',
                                          name='sigma_output')

        # Physics constraint layer
        self.physics_constraint = MaxwellConstraintLayer()

    def build_encoder(self, n_filters, n_blocks, use_attention):
        """Build encoder with residual blocks."""
        encoder_layers = []

        # Initial convolution
        encoder_layers.append(
            layers.Conv2D(n_filters, 3, padding='same', activation='relu')
        )

        # Downsampling blocks
        for i in range(n_blocks):
            filters = n_filters * (2 ** i)

            # Residual block
            res_block = self.residual_block(filters, use_attention)
            encoder_layers.append(res_block)

            # Downsample
            encoder_layers.append(
                layers.Conv2D(filters * 2, 3, strides=2, padding='same')
            )

        return keras.Sequential(encoder_layers)

    def build_bottleneck(self, filters):
        """Build bottleneck with physics awareness."""
        bottleneck = keras.Sequential([
            layers.Conv2D(filters, 3, padding='same', activation='relu'),
            layers.BatchNormalization(),
            SelfAttentionBlock(filters),
            layers.Conv2D(filters, 3, padding='same', activation='relu'),
            layers.BatchNormalization()
        ])

        # Frequency domain processing
        self.frequency_transform = layers.Lambda(
            lambda x: tf.signal.fft2d(tf.cast(x, tf.complex64))
        )

        return bottleneck

    def build_decoder(self, n_filters, n_blocks, use_attention):
        """Build decoder with skip connections."""
        decoder_layers = []

        for i in range(n_blocks - 1, -1, -1):
            filters = n_filters * (2 ** i)

            # Upsample
            decoder_layers.append(
                layers.Conv2DTranspose(filters, 3, strides=2, padding='same')
            )

            # Residual block with attention
            res_block = self.residual_block(filters, use_attention)
            decoder_layers.append(res_block)

        return keras.Sequential(decoder_layers)

    def residual_block(self, filters, use_attention):
        """Basic residual block."""

        def block(x):
            residual = x

            # First convolution
            x = layers.Conv2D(filters, 3, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Activation('relu')(x)

            # Second convolution
            x = layers.Conv2D(filters, 3, padding='same')(x)
            x = layers.BatchNormalization()(x)

            # Attention if requested
            if use_attention:
                x = SelfAttentionBlock(filters)(x)

            # Skip connection
            if residual.shape[-1] != filters:
                residual = layers.Conv2D(filters, 1)(residual)

            x = layers.Add()([x, residual])
            x = layers.Activation('relu')(x)

            return x

        return block

    def call(self, inputs, training=False):
        """Forward pass."""
        # Input: S-parameters [batch, height, width, channels]
        x = inputs

        # Encode
        encoder_features = []
        for layer in self.encoder.layers:
            x = layer(x, training=training)
            if 'conv' in layer.name and 'strides' in layer.name:
                encoder_features.append(x)

        # Bottleneck with frequency processing
        x_freq = self.frequency_transform(x)
        x = self.bottleneck(x, training=training)

        # Decode with skip connections
        for i, layer in enumerate(self.decoder.layers):
            x = layer(x, training=training)
            if 'transpose' in layer.name:
                # Add skip connection
                skip_feature = encoder_features.pop()
                x = layers.Concatenate()([x, skip_feature])

        # Outputs
        epsilon_r = self.epsilon_output(x)
        sigma = self.sigma_output(x)

        # Apply physics constraints
        epsilon_r, sigma = self.physics_constraint([epsilon_r, sigma, x_freq])

        # Stack outputs
        output = layers.Concatenate()([epsilon_r, sigma])

        return output


class ThermoNet(Model):
    """Thermal Reconstruction Network - Stage 2."""

    def __init__(self,
                 input_shape: Tuple[int, int, int],
                 output_shape: Tuple[int, int],
                 n_lstm_layers: int = 2,
                 use_convlstm: bool = True):
        super().__init__()

        # Convolutional LSTM for temporal evolution
        if use_convlstm:
            self.convlstm = self.build_convlstm(input_shape, n_lstm_layers)
        else:
            self.convlstm = self.build_lstm(input_shape, n_lstm_layers)

        # U-Net for spatial reconstruction
        self.unet = self.build_unet(output_shape)

        # Bioheat constraint layer
        self.bioheat_constraint = BioHeatConstraintLayer()

        # Attention mechanism for tumor focus
        self.attention = layers.MultiHeadAttention(num_heads=8, key_dim=64)

    def build_convlstm(self, input_shape, n_layers):
        """Build convolutional LSTM network."""
        convlstm_layers = []

        for i in range(n_layers):
            filters = 64 // (2 ** i)
            return_sequences = i < n_layers - 1

            convlstm_layers.append(
                layers.ConvLSTM2D(
                    filters=filters,
                    kernel_size=3,
                    padding='same',
                    return_sequences=return_sequences,
                    activation='tanh'
                )
            )

        return keras.Sequential(convlstm_layers)

    def build_lstm(self, input_shape, n_layers):
        """Build standard LSTM network."""
        lstm_layers = []

        # Reshape for LSTM
        lstm_layers.append(layers.Reshape((-1, input_shape[-1])))

        for i in range(n_layers):
            units = 256 // (2 ** i)
            return_sequences = i < n_layers - 1

            lstm_layers.append(
                layers.LSTM(units,
                            return_sequences=return_sequences,
                            dropout=0.2)
            )

        return keras.Sequential(lstm_layers)

    def build_unet(self, output_shape):
        """Build U-Net for spatial reconstruction."""
        # Encoder
        encoder_input = layers.Input(shape=output_shape + (128,))

        # Contracting path
        c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(encoder_input)
        c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(c1)
        p1 = layers.MaxPooling2D((2, 2))(c1)

        c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(p1)
        c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(c2)
        p2 = layers.MaxPooling2D((2, 2))(c2)

        c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(p2)
        c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(c3)
        p3 = layers.MaxPooling2D((2, 2))(c3)

        # Bottleneck
        c4 = layers.Conv2D(512, 3, activation='relu', padding='same')(p3)
        c4 = layers.Conv2D(512, 3, activation='relu', padding='same')(c4)

        # Expanding path
        u5 = layers.Conv2DTranspose(256, 2, strides=2, padding='same')(c4)
        u5 = layers.Concatenate()([u5, c3])
        c5 = layers.Conv2D(256, 3, activation='relu', padding='same')(u5)
        c5 = layers.Conv2D(256, 3, activation='relu', padding='same')(c5)

        u6 = layers.Conv2DTranspose(128, 2, strides=2, padding='same')(c5)
        u6 = layers.Concatenate()([u6, c2])
        c6 = layers.Conv2D(128, 3, activation='relu', padding='same')(u6)
        c6 = layers.Conv2D(128, 3, activation='relu', padding='same')(c6)

        u7 = layers.Conv2DTranspose(64, 2, strides=2, padding='same')(c6)
        u7 = layers.Concatenate()([u7, c1])
        c7 = layers.Conv2D(64, 3, activation='relu', padding='same')(u7)
        c7 = layers.Conv2D(64, 3, activation='relu', padding='same')(c7)

        # Output
        output = layers.Conv2D(1, 1, activation='sigmoid')(c7)

        return Model(inputs=encoder_input, outputs=output)

    def call(self, inputs, training=False):
        """Forward pass."""
        # Input: permittivity distribution
        permittivity = inputs

        # Process temporal evolution with ConvLSTM
        if hasattr(self, 'convlstm'):
            # Add time dimension
            x = tf.expand_dims(permittivity, axis=1)
            x = tf.tile(x, [1, 5, 1, 1, 1])  # 5 time steps

            x = self.convlstm(x, training=training)
        else:
            x = self.lstm(permittivity, training=training)

        # Spatial reconstruction with U-Net
        x = self.unet(x, training=training)

        # Apply attention for tumor regions
        attention_output = self.attention(x, x, x)
        x = layers.Add()([x, attention_output])

        # Apply bioheat constraints
        x = self.bioheat_constraint(x)

        return x


class HPINN(Model):
    """Hierarchical Physics-Informed Neural Network."""

    def __init__(self,
                 input_shape: Tuple[int, int, int],
                 output_shape: Tuple[int, int],
                 physics_constraints: bool = True):
        super().__init__()

        # Stage 1: EM Inversion
        self.eminet = EMINet(input_shape, output_shape)

        # Stage 2: Thermal Reconstruction
        self.thermonet = ThermoNet(output_shape + (2,), output_shape)

        # Physics constraints flag
        self.physics_constraints = physics_constraints

        # Loss tracking
        self.total_loss_tracker = keras.metrics.Mean(name="total_loss")
        self.data_loss_tracker = keras.metrics.Mean(name="data_loss")
        self.physics_loss_tracker = keras.metrics.Mean(name="physics_loss")
        self.temp_rmse_tracker = keras.metrics.Mean(name="temp_rmse")
        self.loc_error_tracker = keras.metrics.Mean(name="loc_error")

    def compile(self,
                optimizer=None,
                loss_fn=None,
                metrics=None):
        """Compile model with custom components."""
        if optimizer is None:
            optimizer = keras.optimizers.AdamW(
                learning_rate=1e-4,
                weight_decay=1e-6
            )

        if loss_fn is None:
            loss_fn = PhysicsInformedLoss(alpha=0.1, beta=0.01)

        super().compile(optimizer=optimizer, loss=loss_fn, metrics=metrics)

        # Custom metrics
        self.temp_rmse = keras.metrics.RootMeanSquaredError(name='temp_rmse')
        self.localization_error = LocalizationError(name='loc_error')

    def call(self, inputs, training=False):
        """Forward pass through both stages."""
        # Stage 1: S-parameters -> Permittivity
        permittivity = self.eminet(inputs, training=training)

        # Stage 2: Permittivity -> Temperature
        temperature = self.thernonet(permittivity, training=training)

        return temperature

    def train_step(self, data):
        """Custom training step with physics constraints."""
        x, y_true = data

        with tf.GradientTape() as tape:
            # Forward pass
            y_pred = self(x, training=True)

            # Data loss
            data_loss = self.compiled_loss(y_true, y_pred)

            # Physics loss
            if self.physics_constraints:
                physics_loss = self.compute_physics_loss(x, y_pred)
                total_loss = data_loss + 0.1 * physics_loss
            else:
                physics_loss = 0.0
                total_loss = data_loss

            # Add model regularization losses
            reg_loss = tf.reduce_sum(self.losses)
            total_loss += reg_loss

        # Compute gradients
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(total_loss, trainable_vars)

        # Apply gradients
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))

        # Update metrics
        self.total_loss_tracker.update_state(total_loss)
        self.data_loss_tracker.update_state(data_loss)
        self.physics_loss_tracker.update_state(physics_loss)

        # Temperature RMSE
        self.temp_rmse.update_state(y_true, y_pred)

        # Localization error
        self.loc_error_tracker.update_state(y_true, y_pred)

        return {
            "total_loss": self.total_loss_tracker.result(),
            "data_loss": self.data_loss_tracker.result(),
            "physics_loss": self.physics_loss_tracker.result(),
            "temp_rmse": self.temp_rmse.result(),
            "loc_error": self.loc_error_tracker.result()
        }

    def compute_physics_loss(self, x, y_pred):
        """Compute physics constraint loss."""
        # Maxwell's equations constraint
        em_loss = self.eminet.physics_constraint.loss

        # Bioheat equation constraint
        thermal_loss = self.thermonet.bioheat_constraint.loss

        return em_loss + thermal_loss

    def test_step(self, data):
        """Custom test step."""
        x, y_true = data

        # Forward pass
        y_pred = self(x, training=False)

        # Calculate losses
        data_loss = self.compiled_loss(y_true, y_pred)

        if self.physics_constraints:
            physics_loss = self.compute_physics_loss(x, y_pred)
            total_loss = data_loss + 0.1 * physics_loss
        else:
            physics_loss = 0.0
            total_loss = data_loss

        # Update metrics
        self.total_loss_tracker.update_state(total_loss)
        self.data_loss_tracker.update_state(data_loss)
        self.physics_loss_tracker.update_state(physics_loss)
        self.temp_rmse.update_state(y_true, y_pred)
        self.loc_error_tracker.update_state(y_true, y_pred)

        return {m.name: m.result() for m in self.metrics}

    @property
    def metrics(self):
        """Return list of metrics."""
        return [
            self.total_loss_tracker,
            self.data_loss_tracker,
            self.physics_loss_tracker,
            self.temp_rmse,
            self.loc_error_tracker
        ]


class MaxwellConstraintLayer(layers.Layer):
    """Layer enforcing Maxwell's equations constraints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loss = tf.Variable(0.0, trainable=False)

    def call(self, inputs):
        epsilon_r, sigma, freq_data = inputs

        # Enforce divergence condition: ∇·D ≈ 0
        epsilon_grad = tf.gradients(epsilon_r, epsilon_r)
        div_condition = tf.reduce_mean(tf.abs(epsilon_grad))

        # Enforce causality via Kramers-Kronig relations
        kk_violation = self.kramers_kronig_check(epsilon_r, sigma, freq_data)

        # Update loss
        self.loss.assign(div_condition + kk_violation)

        return epsilon_r, sigma

    def kramers_kronig_check(self, epsilon_r, sigma, freq_data):
        """Check Kramers-Kronig relations."""
        # Simplified implementation
        return tf.reduce_mean(tf.abs(epsilon_r - tf.math.real(freq_data)))


class BioHeatConstraintLayer(layers.Layer):
    """Layer enforcing bioheat equation constraints."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loss = tf.Variable(0.0, trainable=False)

    def call(self, temperature):
        # Enforce smoothness (thermal diffusion)
        temp_laplacian = self.laplacian_2d(temperature)
        diffusion_violation = tf.reduce_mean(tf.abs(temp_laplacian))

        # Enforce physiological bounds (36-40°C)
        lower_bound = tf.maximum(0, 36 - temperature)
        upper_bound = tf.maximum(0, temperature - 40)
        bound_violation = tf.reduce_mean(lower_bound + upper_bound)

        # Update loss
        self.loss.assign(diffusion_violation + 0.1 * bound_violation)

        return temperature

    def laplacian_2d(self, field):
        """Compute 2D Laplacian."""
        # Using convolution
        kernel = tf.constant([[0, 1, 0],
                              [1, -4, 1],
                              [0, 1, 0]], dtype=tf.float32)
        kernel = tf.reshape(kernel, [3, 3, 1, 1])

        if len(field.shape) == 3:
            field = tf.expand_dims(field, -1)

        return tf.nn.conv2d(field, kernel, strides=1, padding='SAME')


class SelfAttentionBlock(layers.Layer):
    """Self-attention block for feature enhancement."""

    def __init__(self, filters, **kwargs):
        super().__init__(**kwargs)
        self.filters = filters

        # Query, Key, Value projections
        self.query_conv = layers.Conv2D(filters // 8, 1)
        self.key_conv = layers.Conv2D(filters // 8, 1)
        self.value_conv = layers.Conv2D(filters, 1)

        # Output projection
        self.gamma = self.add_weight(
            name='gamma',
            shape=(),
            initializer='zeros'
        )
        self.output_conv = layers.Conv2D(filters, 1)

    def call(self, x):
        batch_size, h, w, c = tf.shape(x)

        # Project to query, key, value
        query = self.query_conv(x)
        key = self.key_conv(x)
        value = self.value_conv(x)

        # Reshape for attention
        query = tf.reshape(query, [batch_size, -1, query.shape[-1]])
        key = tf.reshape(key, [batch_size, -1, key.shape[-1]])
        value = tf.reshape(value, [batch_size, -1, value.shape[-1]])

        # Attention scores
        attention = tf.matmul(query, key, transpose_b=True)
        attention = tf.nn.softmax(attention, axis=-1)

        # Apply attention
        out = tf.matmul(attention, value)
        out = tf.reshape(out, [batch_size, h, w, self.filters])

        # Residual connection
        out = self.gamma * out + x
        out = self.output_conv(out)

        return out


class LocalizationError(keras.metrics.Metric):
    """Custom metric for tumor localization error."""

    def __init__(self, name="loc_error", **kwargs):
        super().__init__(name=name, **kwargs)
        self.error_sum = self.add_weight(name="error_sum", initializer="zeros")
        self.count = self.add_weight(name="count", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        # Find tumor centroids
        true_centroid = self.find_centroid(y_true)
        pred_centroid = self.find_centroid(y_pred)

        # Calculate Euclidean distance (in mm)
        error = tf.sqrt(tf.reduce_sum((true_centroid - pred_centroid) ** 2))

        self.error_sum.assign_add(error)
        self.count.assign_add(1)

    def result(self):
        return self.error_sum / tf.maximum(self.count, 1)

    def find_centroid(self, heatmap):
        """Find centroid of hottest region."""
        # Threshold
        threshold = 0.5 * tf.reduce_max(heatmap)
        mask = tf.cast(heatmap > threshold, tf.float32)

        # Coordinates
        grid_x, grid_y = tf.meshgrid(
            tf.range(tf.shape(heatmap)[1]),
            tf.range(tf.shape(heatmap)[2])
        )
        grid_x = tf.cast(grid_x, tf.float32)
        grid_y = tf.cast(grid_y, tf.float32)

        # Weighted average
        total_mass = tf.reduce_sum(mask) + 1e-8
        centroid_x = tf.reduce_sum(grid_x * mask) / total_mass
        centroid_y = tf.reduce_sum(grid_y * mask) / total_mass

        return tf.stack([centroid_x, centroid_y], axis=-1)