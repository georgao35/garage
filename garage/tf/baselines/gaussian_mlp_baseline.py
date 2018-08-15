"""This module implements gaussian mlp baseline."""
import numpy as np

from garage.baselines import Baseline
from garage.core import Serializable
from garage.misc.overrides import overrides
from garage.tf.core import Parameterized
from garage.tf.regressors import GaussianMLPRegressor


class GaussianMLPBaseline(Baseline, Parameterized, Serializable):
    """A value function using gaussian mlp network."""

    def __init__(
            self,
            env_spec,
            subsample_factor=1.,
            num_seq_inputs=1,
            include_action_to_input=False,
            regressor_args=None,
    ):
        """
        Constructor.

        :param env_spec:
        :param subsample_factor:
        :param num_seq_inputs:
        :param regressor_args:
        """
        Parameterized.__init__(self)
        Serializable.quick_init(self, locals())
        super(GaussianMLPBaseline, self).__init__(env_spec)
        self._include_action_to_input = include_action_to_input
        if regressor_args is None:
            regressor_args = dict()
        if self._include_action_to_input:
            input_shape = ((env_spec.observation_space.flat_dim + env_spec.action_space.flat_dim) * num_seq_inputs, )
        else:
            input_shape = (env_spec.observation_space.flat_dim * num_seq_inputs,)
        print('Baseline input_shape: {}'.format(input_shape))
        self._regressor = GaussianMLPRegressor(
            input_shape=input_shape,
            output_dim=1,
            name="Baseline",
            **regressor_args)

    @overrides
    def fit(self, paths):
        """Fit regressor based on paths."""
        observations = np.concatenate([p["observations"] for p in paths])
        if self._include_action_to_input:
            actions = np.concatenate([p["actions"] for p in paths])
            observations = np.concatenate([observations, actions], axis=-1)
        returns = np.concatenate([p["returns"] for p in paths])
        self._regressor.fit(observations, returns.reshape((-1, 1)))

    @overrides
    def predict(self, path):
        """Predict value based on paths."""
        if self._include_action_to_input:
            return self._regressor.predict(np.concatenate([path["observations"], path["actions"]], axis=-1)).flatten()
        else:
            return self._regressor.predict(path["observations"]).flatten()

    @overrides
    def get_param_values(self, **tags):
        """Get parameter values."""
        return self._regressor.get_param_values(**tags)

    @overrides
    def set_param_values(self, flattened_params, **tags):
        """Set parameter values to val."""
        self._regressor.set_param_values(flattened_params, **tags)

    @overrides
    def get_params_internal(self, **tags):
        return self._regressor.get_params_internal(**tags)
