# Copyright (C) 2018 ETH Zurich, Institute for Particle Physics and Astrophysics

"""
Created on May 25, 2018
author: Joerg Herbel
Original Source: ethz_des_mccl.psf_estimation.cnn_psf.cnn_util
"""

import h5py
import numpy as np
import tensorflow.compat.v1 as tf
import yaml
from cosmic_toolbox import logger

tf.disable_v2_behavior()

LOGGER = logger.get_logger(__file__)


def res_layer(tensor_in, kernel_shape, activation):
    """
    Standard resnet layer (from tiny image net)
    """
    with tf.variable_scope("conv_1"):
        weights = tf.get_variable(
            "weights",
            kernel_shape,
            initializer=tf.truncated_normal_initializer(0, 0.01),
        )
        biases = tf.get_variable(
            "biases", kernel_shape[-1], initializer=tf.zeros_initializer()
        )
        conv = (
            tf.nn.conv2d(tensor_in, weights, strides=[1, 1, 1, 1], padding="SAME")
            + biases
        )

        # Batch normalization with proper variable creation to match checkpoint
        with tf.variable_scope("batch_normalization"):
            # Create variables that match the checkpoint format
            mean = tf.get_variable(
                "moving_mean",
                [kernel_shape[-1]],
                initializer=tf.zeros_initializer(),
                trainable=False,
            )
            variance = tf.get_variable(
                "moving_variance",
                [kernel_shape[-1]],
                initializer=tf.ones_initializer(),
                trainable=False,
            )
            beta = tf.get_variable(
                "beta", [kernel_shape[-1]], initializer=tf.zeros_initializer()
            )
            gamma = tf.get_variable(
                "gamma", [kernel_shape[-1]], initializer=tf.ones_initializer()
            )

            conv = tf.nn.batch_normalization(
                conv,
                mean=mean,
                variance=variance,
                offset=beta,
                scale=gamma,
                variance_epsilon=1e-3,
            )
        conv = activation(conv)

    with tf.variable_scope("conv_2"):
        weights = tf.get_variable(
            "weights",
            kernel_shape,
            initializer=tf.truncated_normal_initializer(0, 0.01),
        )
        biases = tf.get_variable(
            "biases",
            kernel_shape[-1],
            initializer=tf.truncated_normal_initializer(0, 0.01),
        )
        conv = (
            tf.nn.conv2d(conv, weights, strides=[1, 1, 1, 1], padding="SAME") + biases
        )

        # Batch normalization with proper variable creation to match checkpoint
        with tf.variable_scope("batch_normalization"):
            # Create variables that match the checkpoint format
            mean = tf.get_variable(
                "moving_mean",
                [kernel_shape[-1]],
                initializer=tf.zeros_initializer(),
                trainable=False,
            )
            variance = tf.get_variable(
                "moving_variance",
                [kernel_shape[-1]],
                initializer=tf.ones_initializer(),
                trainable=False,
            )
            beta = tf.get_variable(
                "beta", [kernel_shape[-1]], initializer=tf.zeros_initializer()
            )
            gamma = tf.get_variable(
                "gamma", [kernel_shape[-1]], initializer=tf.ones_initializer()
            )

            conv = tf.nn.batch_normalization(
                conv,
                mean=mean,
                variance=variance,
                offset=beta,
                scale=gamma,
                variance_epsilon=1e-3,
            )
        conv = activation(conv + tensor_in)

    return conv


def create_cnn(
    input,
    filter_sizes,
    n_filters_start,
    n_resnet_layers,
    resnet_layers_kernel_size,
    n_fc,
    dropout_rate,
    n_out,
    activation_function="relu",
    apply_dropout=True,
    downsampling_method="max_pool",
    padding="same",
):
    activation = getattr(tf.nn, activation_function)
    x_tensor = tf.reshape(input, [-1] + input.get_shape().as_list()[1:] + [1])

    # Convolutional layers
    current_n_channels = 1
    current_height, current_width = x_tensor.get_shape().as_list()[1:3]
    x_conv = x_tensor

    for layer_ind in range(len(filter_sizes)):
        current_n_channels = int(n_filters_start * 2**layer_ind)

        if downsampling_method == "off":
            # Use variable names compatible with tf.layers.conv2d
            scope_name = "conv2d" if layer_ind == 0 else f"conv2d_{layer_ind}"

            with tf.variable_scope(scope_name):
                kernel = tf.get_variable(
                    "kernel",
                    [
                        filter_sizes[layer_ind],
                        filter_sizes[layer_ind],
                        x_conv.get_shape()[-1],
                        current_n_channels,
                    ],
                    initializer=tf.truncated_normal_initializer(0, 0.01),
                )
                bias = tf.get_variable(
                    "bias", [current_n_channels], initializer=tf.zeros_initializer()
                )
                x_conv = (
                    tf.nn.conv2d(
                        input=x_conv,
                        filters=kernel,
                        strides=[1, 1, 1, 1],
                        padding=padding.upper(),
                    )
                    + bias
                )
            x_conv = activation(x_conv)
        else:
            raise ValueError(
                f"Unsupported downsampling method: {downsampling_method}. "
                "Currently only 'off' is supported within UFig. For other methods, "
                "refer to the original implementation in the ethz_des_mccl repo."
            )

        # subtract in case of valid padding
        if padding == "valid":
            current_height -= filter_sizes[layer_ind] - 1
            current_width -= filter_sizes[layer_ind] - 1

    # ResNet layers
    resnet_kernel_shape = [
        resnet_layers_kernel_size,
        resnet_layers_kernel_size,
        current_n_channels,
        current_n_channels,
    ]

    for i_res in range(n_resnet_layers):
        with tf.variable_scope(f"resnet_layer_{i_res + 1}"):
            x_conv = res_layer(x_conv, resnet_kernel_shape, activation)

    # Fully connected layers
    x_conv_flat = tf.reshape(
        x_conv, [-1, current_height * current_width * current_n_channels]
    )

    x_fc = x_conv_flat
    for fc_ind in range(len(n_fc)):
        # Use variable names compatible with tf.layers.dense
        scope_name = "dense" if fc_ind == 0 else f"dense_{fc_ind}"

        with tf.variable_scope(scope_name):
            kernel = tf.get_variable(
                "kernel",
                [x_fc.get_shape()[-1], n_fc[fc_ind]],
                initializer=tf.truncated_normal_initializer(mean=0.0, stddev=0.1),
            )
            bias = tf.get_variable(
                "bias", [n_fc[fc_ind]], initializer=tf.constant_initializer(value=0.1)
            )
            x_fc = activation(tf.matmul(x_fc, kernel) + bias)

    # Dropout
    x_do = tf.nn.dropout(x_fc, rate=dropout_rate if apply_dropout else 0.0)

    # Map the fully connected features to output variables
    # The output layer is just another dense layer in the checkpoint
    final_dense_ind = len(n_fc)
    scope_name = "dense" if final_dense_ind == 0 else f"dense_{final_dense_ind}"

    with tf.variable_scope(scope_name):
        kernel_out = tf.get_variable(
            "kernel",
            [x_fc.get_shape()[-1], n_out],
            initializer=tf.truncated_normal_initializer(mean=0.0, stddev=0.1),
        )
        bias_out = tf.get_variable(
            "bias", [n_out], initializer=tf.constant_initializer(value=0.1)
        )
        x_out = tf.matmul(x_do, kernel_out) + bias_out

    return x_out


class CNNPredictor:
    def __init__(self, path_trained_cnn):
        LOGGER.debug(f"tensorflow {str(tf)} version {tf.__version__}")

        self.path_trained_cnn = path_trained_cnn

        # Reset graph
        tf.reset_default_graph()

        # Load configuration
        with h5py.File(
            get_path_output_config(path_trained_cnn), mode="r"
        ) as fh5_config:
            self.config = yaml.safe_load(fh5_config.attrs["config"])
            self.config_training_data = yaml.safe_load(
                fh5_config.attrs["config_training_data"]
            )
            self.input_shape = tuple(fh5_config["input_shape"])
            self.means = fh5_config["means"][...]
            self.scales = fh5_config["scales"][...]

        self.param_names = self.config["param_names"]

        # For backwards compatibility
        self.config.setdefault("n_resnet_layers", 0)
        self.config.setdefault("resnet_layers_kernel_size", 3)
        self.config.setdefault("activation_function", "relu")
        self.config.setdefault("padding", "same")

        # Get loss function used for training
        if "loss_function_kwargs" in self.config:
            self.config["loss_function_kwargs"]["is_training"] = False

        n_pred = 2 * len(self.config["param_names"])
        self._transform_predictions = self._apply_means_scales

        # Setup network
        self.input_tensor = tf.placeholder(tf.float32, (None,) + self.input_shape)
        input_tensor_norm = normalize_stamps(self.input_tensor)
        self.pred = create_cnn(
            input=input_tensor_norm,
            filter_sizes=self.config["filter_sizes"],
            n_filters_start=self.config["n_filters_start"],
            n_resnet_layers=self.config["n_resnet_layers"],
            resnet_layers_kernel_size=self.config["resnet_layers_kernel_size"],
            n_fc=self.config["n_fully_connected"],
            dropout_rate=self.config["dropout_rate"],
            n_out=n_pred,
            activation_function=self.config["activation_function"],
            apply_dropout=False,
            downsampling_method=self.config["downsampling_method"],
            padding=self.config["padding"],
        )

        # Transform predicted parameters
        self.par_pred_transformed = self._transform_predictions(
            self.pred[:, : len(self.param_names)]
        )

    def _apply_means_scales(self, pred):
        pred *= self.scales
        pred += self.means
        return pred

    def __call__(self, cube, batchsize=None):
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            tf.train.Saver().restore(sess, self.path_trained_cnn)

            if batchsize is None or len(cube) == 0:
                if len(cube) == 0:
                    LOGGER.warning("Predicting on empty cube, output will be empty!")

                pred = self.pred.eval(feed_dict={self.input_tensor: cube})
                par_transformed = self.par_pred_transformed.eval(
                    feed_dict={self.pred: pred}
                )

            else:
                ind_batch = list(range(0, len(cube), batchsize)) + [len(cube)]
                par_transformed = [None] * (len(ind_batch) - 1)

                for i in range(len(ind_batch) - 1):
                    LOGGER.info(f"Predicting on batch {i + 1} / {len(ind_batch) - 1}")
                    cube_current = cube[ind_batch[i] : ind_batch[i + 1]]

                    pred = self.pred.eval(feed_dict={self.input_tensor: cube_current})
                    par_transformed[i] = self.par_pred_transformed.eval(
                        feed_dict={self.pred: pred}
                    )

                par_transformed = np.concatenate(par_transformed)

            return par_transformed


def get_path_output_config(path_cnn):
    return path_cnn + ".h5"


def normalize_stamps(stamps):
    stamps_min = tf.reduce_min(stamps, axis=(1, 2), keepdims=True)

    stamps -= stamps_min

    stamps_max = tf.reduce_max(stamps, axis=(1, 2), keepdims=True)

    stamps /= stamps_max

    return stamps
