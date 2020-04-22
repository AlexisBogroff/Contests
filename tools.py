import torch
import matplotlib.pyplot as plt


class data_monitoring:
    """
    - Understand data:
    -- viszualize
    -- get insights from standard metrics
    - Monitor training:
    -- vizualize parameters
    -- vizualize misclassified samples

    args:
    - database (pytorch tensor)
    """


    def __init__(self, db = None, model = None, sample_size_flatten = None, print_statistics = True, \
    print_plots = False, print_verbose = False):
        self._db = db
        self._model = model
        self._sample_size_flatten = sample_size_flatten
        self._print_statistics = print_statistics
        self._print_plots = print_plots
        self._print_verbose = print_verbose
        self._plot_n_limit = 5


    def get_misclassified_samples(self, model = None, db = None, sample_size_flatten = None, plot = False, plot_shape = None):
        """
        Get the number of misclassified samples (and proportion), \
        and get a dictionary of these samples' index and data.

        args:
        - db: data (x, y)
        - model: a trained model on the data provided
        """
        # Initialize output variables
        dic_misclassified_samples = {}
        n_misclassified = 0

        # Verify that a database was provided
        if db:
            self._db = db
        elif not self._db:
            raise AttributeError("No data passed in function"\
            " argument 'db', nor in object argument 'self.db'")

        # Verify that sample_size_flatten was provided
        if sample_size_flatten:
            self._sample_size_flatten = sample_size_flatten
        elif not self._sample_size_flatten:
            raise AttributeError("No sample_size_flatten passed in function"\
            " argument 'sample_size_flatten', nor in object argument 'self._sample_size_flatten'")

        # Loop through each db sample
        for idx, (x, y) in enumerate(self._db):
            # Make prediction
            z = self._model(x.reshape(-1, sample_size_flatten))
            
            # TODO extend: works only for multiclass classification
            # with a linear function as output layer
            y_hat_proba, y_hat_idx = torch.max(z, 1)
            
            # test if prediction differs from truth
            if y_hat_idx != y:
                n_misclassified += 1
                dic_misclassified_samples[idx] = x
                if self._print_verbose:
                    print("Sample' index: ", idx)
                if plot or self._print_plots:
                    # TODO extend: works only for squared images
                    # (not for rectangles, nor for other type of data)
                    plt.imshow(x.view(plot_shape[0], plot_shape[1]))
                    plt.show()
            # Stop plotting if > limit
            if n_misclassified >= self._plot_n_limit:
                break

        return n_misclassified, dic_misclassified_samples


    def get_training_accuracy(self, plot=True):
        raise NotImplementedError


    def get_validation_accuracy(self, plot=True):
        raise NotImplementedError
