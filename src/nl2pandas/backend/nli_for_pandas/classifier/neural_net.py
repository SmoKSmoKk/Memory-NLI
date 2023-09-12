from numpy import ndarray
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.python.keras.callbacks import History


class NeuralNet:
    """
    This class uses a simple two-layer MLP (Multilayer Perceptron) that takes the embeddings of two utterances
    and predicts a probability of them being the same lifted program.
    It basically outputs σ(a cos-sim(φ(f), φ(f′)) + b), where a & b are learned scalars, σ is the sigmoid function
    and φ is the embedding of an utterance.

    :param lr: learning rate for optimizer, defaults to 0.005
    """

    def __init__(self, lr: float = 0.005):
        self.model = Sequential()
        # Dense layer performs the following: output = activation(dot(input, kernel) + bias)
        # which is exactly what we want: output = sigmoid(a*input + b)
        # with the input being our similarity measure
        self.model.add(
            Dense(
                1,
                input_dim=1,
                activation="sigmoid",
                kernel_initializer="glorot_uniform",
                bias_initializer="zeros",
            )
        )

        self.model.compile(
            optimizer=Adam(learning_rate=lr),
            loss=BinaryCrossentropy(),
            metrics=["accuracy"],
        )

    def train(self, x_train: ndarray, y_train: ndarray, epochs: int) -> History:
        """
        Trains the neural net by backpropagation, using the defined loss and optimizer.

        :param x_train: training input data (similarities between utterances)
        :param y_train: training target data (1 if same action, 0 if different)
        :param epochs: number of epochs to train the neural net

        :return accuracy of the last epoch
        """
        # manual_variable_initialization(True)
        history = self.model.fit(x_train, y_train, epochs=epochs, shuffle=True)

        return history

    def predict(self, similarities: ndarray) -> ndarray:
        """
        Predicts the probabilities that the utterances share the same program based on their similarities.

        :param similarities: numpy array of similarities

        :return: numpy array of probabilities
        """
        predictions = self.model.predict(similarities)
        # squeeze so that it results in an array of floats (instead of singleton lists)
        predictions = predictions.squeeze()
        return predictions
