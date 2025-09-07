import numpy as np
from itertools import tee

from tensorflow.keras.models import model_from_json
from tensorflow.keras.optimizers import deserialize as deserialize_optimizer
from tensorflow.python.keras.utils.generic_utils import slice_arrays

from .enums.frequency import Frequency
from .utils import subtract_params
from .parameter import BaseParameterClient

from .utils.model_utils import is_multiple_input_model, is_multiple_output_model


class SparkWorker(object):
    """Synchronous Spark worker. This code will be executed on workers."""

    def __init__(
        self,
        json,
        parameters,
        train_config,
        master_optimizer,
        master_loss,
        master_metrics,
        custom_objects,
    ):
        self.json = json
        self.parameters = parameters
        self.train_config = train_config
        self.master_loss = master_loss
        self.master_optimizer = master_optimizer
        self.master_metrics = master_metrics
        self.custom_objects = custom_objects
        self.model = None

    def train(self, data_iterator):
        """Train a keras model on a worker"""
        history = None
        optimizer = deserialize_optimizer(self.master_optimizer)
        self.model = model_from_json(self.json, self.custom_objects)
        self.model.compile(
            optimizer=optimizer, loss=self.master_loss, metrics=self.master_metrics
        )
        self.model.set_weights(self.parameters.value)

        feature_iterator, label_iterator = tee(data_iterator, 2)
        x_train = np.asarray([x for x, y in feature_iterator])
        y_train = np.asarray([y for x, y in label_iterator])
        if is_multiple_input_model(self.model):
            x_train = np.hsplit(x_train, len(self.model.input_shape))
        if is_multiple_output_model(self.model):
            y_train = np.hsplit(y_train, len(self.model.output_shape))
        weights_before_training = self.model.get_weights()
        if x_train.shape[0] > self.train_config.get("batch_size"):
            history = self.model.fit(x_train, y_train, **self.train_config)
        weights_after_training = self.model.get_weights()
        deltas = subtract_params(weights_before_training, weights_after_training)
        if history:
            yield [deltas, history.history]
        else:
            yield [deltas, None]


class AsynchronousSparkWorker:
    """Asynchronous Spark worker. This code will be executed on workers."""

    def __init__(
        self,
        json,
        parameters,
        client,
        train_config,
        frequency,
        master_optimizer,
        master_loss,
        master_metrics,
        custom_objects,
    ):
        if isinstance(client, BaseParameterClient):
            # either supply a client object directly
            self.client = client
        else:
            # or a string to create a client
            self.client = BaseParameterClient.get_client(client)

        self.train_config = train_config
        self.frequency = frequency
        self.master_optimizer = master_optimizer
        self.master_loss = master_loss
        self.master_metrics = master_metrics
        self.json = json
        self.parameters = parameters
        self.custom_objects = custom_objects
        self.model = None

    def train(self, data_iterator):
        """Train a keras model on a worker and send asynchronous updates
        to parameter server
        """
        feature_iterator, label_iterator = tee(data_iterator, 2)
        x_train = np.asarray([x for x, y in feature_iterator])
        y_train = np.asarray([y for x, y in label_iterator])

        if x_train.size == 0:
            return
        nb_train_sample = x_train.shape[0]

        self.model = model_from_json(self.json, self.custom_objects)
        if is_multiple_input_model(self.model):
            x_train = np.hsplit(x_train, len(self.model.input_shape))
        if is_multiple_output_model(self.model):
            y_train = np.hsplit(y_train, len(self.model.output_shape))
        optimizer = deserialize_optimizer(self.master_optimizer)
        self.model.compile(
            optimizer=optimizer, loss=self.master_loss, metrics=self.master_metrics
        )
        self.model.set_weights(self.parameters.value)

        epochs = self.train_config["epochs"]
        batch_size = self.train_config.get("batch_size")
        nb_batch = int(np.ceil(nb_train_sample / float(batch_size)))
        index_array = np.arange(nb_train_sample)
        batches = [
            (i * batch_size, min(nb_train_sample, (i + 1) * batch_size))
            for i in range(0, nb_batch)
        ]

        if self.frequency == Frequency.EPOCH:
            for epoch in range(epochs):
                weights_before_training = self.client.get_parameters()
                self.model.set_weights(weights_before_training)
                self.train_config["epochs"] = 1
                if nb_train_sample > batch_size:
                    self.model.fit(x_train, y_train, **self.train_config)
                self.train_config["epochs"] = epochs
                weights_after_training = self.model.get_weights()
                deltas = subtract_params(
                    weights_before_training, weights_after_training
                )
                self.client.update_parameters(deltas)
        elif self.frequency == Frequency.BATCH:
            for epoch in range(epochs):
                if nb_train_sample > batch_size:
                    for batch_start, batch_end in batches:
                        weights_before_training = self.client.get_parameters()
                        self.model.set_weights(weights_before_training)
                        batch_ids = index_array[batch_start:batch_end]
                        x = slice_arrays(x_train, batch_ids)
                        y = slice_arrays(y_train, batch_ids)
                        self.model.train_on_batch(x, y)
                        weights_after_training = self.model.get_weights()
                        deltas = subtract_params(
                            weights_before_training, weights_after_training
                        )
                        self.client.update_parameters(deltas)
        else:
            raise ValueError(
                "frequency parameter can be `epoch` or `batch, got {}".format(
                    self.frequency
                )
            )
        yield []
