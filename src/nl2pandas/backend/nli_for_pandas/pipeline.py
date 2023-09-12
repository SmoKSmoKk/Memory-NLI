from builtins import zip
from typing import Dict, List, SupportsFloat, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import tensorflow
from imblearn.over_sampling import RandomOverSampler
from nl2pandas.backend.nli_for_pandas.classifier.neural_net import NeuralNet
from nl2pandas.backend.nli_for_pandas.data.data import Data
from nl2pandas.backend.nli_for_pandas.embedding.BERT import BERT
from nl2pandas.backend.nli_for_pandas.embedding.embedding import Embedding
from nl2pandas.backend.nli_for_pandas.entity_abstraction.combiner import Combiner
from nl2pandas.backend.nli_for_pandas.entity_abstraction.entity_abstraction import (
    EntityAbstraction,
)
from nl2pandas.backend.nli_for_pandas.similarity.cosine_similarity import (
    CosineSimilarity,
)
from nl2pandas.backend.nli_for_pandas.similarity.similarity import Similarity
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.optimizers import Adam
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.callbacks import History


class Pipeline:
    """
    Contains all steps to translate utterances to an executable command (as defined per DSL).

    :param preprocessing: module for preprocessing the utterances
    :param entity_abstraction: module for entity abstraction (lifting)
    :param embedding: module for calculating the embedding
    :param similarity: module for calculating the similarity measure
    :param classifier: module that acts as the final classifier
    :param combiner: module that is used for recombining entities and lifted action
    :param data: Data object containing the utterances and their actions
    :param certainty_threshold: Threshold below which to output NOT_SURE for probabilities from the classifier
    """

    def __init__(
            self,
            preprocessing=None,
            entity_abstraction: EntityAbstraction = EntityAbstraction(),
            embedding: Embedding = BERT(),
            similarity: Similarity = CosineSimilarity(),
            classifier=NeuralNet(),
            combiner: Combiner = Combiner(),
            data=Data(),
            certainty_threshold: float = 0.5,
    ):
        self.preprocessing = preprocessing
        self.entity_abstraction = entity_abstraction
        self.embedding = embedding
        self.similarity = similarity
        self.classifier = classifier
        self.combiner = combiner
        self.data = data
        self.certainty_threshold = certainty_threshold

    def add_utterance(self, utterance: str, actions: str):
        """
        Adds a new input utterance with its corresponding actions (split by ";") to the data set,
        on which then can be trained.
        To do so, the utterance and the actions are lifted (to allow for generalization).

        :param utterance: new input utterance
        :param actions: corresponding list of actions
        """
        lifted_utterance, entities = self.entity_abstraction.lift_entities(utterance)
        # replace entities, which were lifted in input utterance, in the actions string
        lifted_actions = self.entity_abstraction.replace_entities(actions, entities)

        # add lifted utterance and actions to dataset
        self.data.utterances.append(lifted_utterance)
        self.data.actions.append(lifted_actions)

    def train_classifier(self, epochs: int = 500, oversample: bool = True) -> History:
        """
        Utilizes the whole pipeline to execute training of the classifier using the data of the pipeline

        :param epochs: number of epochs to train the model
        :param oversample: flag whether the dataset should be oversampled

        :return: accuracy on training data
        """
        # 1. preprocessing of data
        # 2. entity abstraction

        training_data = self.data

        # 3. calculate the similarities and true values
        similarities, true_values = self.get_similarities_and_true_values(training_data)

        train_x = np.array(similarities).reshape(-1, 1)
        train_y = np.array(true_values).reshape(-1, 1)

        if oversample:
            # oversample if more than 1 class
            if sum(train_y) / len(train_y) < 1:
                train_x, train_y = RandomOverSampler().fit_resample(train_x, train_y)

        # 5. train on this data
        history = self.classifier.train(train_x, train_y, epochs=epochs)
        return history

    def get_similarities_and_true_values(self, data: Data):
        """
        Calculates embeddings for the data utterances and creates all possible pairs of utterances.
        Uses the similarity measure to calculate the similarities and true values.

        :param data: Data object containing utterances and actions

        :return: a list of similarity scores as well as the corresponding true values (0 or 1) for all pairs of
        utterances based on the data in self.data.
        """
        embeddings = self.embedding.embed(data.utterances)

        # create all pairs for utterances
        indices = range(len(data.utterances))
        all_pairs = [(i, j) for i in indices for j in indices]

        # 4. calculate similarity & construct y_train
        true_values = []
        similarities = []
        for i1, i2 in all_pairs:
            sim = self.similarity.calculate(embeddings[i1], embeddings[i2])
            similarities.append(sim)
            prob = int(data.actions[i1] == data.actions[i2])
            true_values.append(prob)

        return similarities, true_values

    def determine_and_set_certainty_threshold(
            self, true_positive_threshold: float = 0.9, visualize: bool = False
    ) -> float:
        """
        Calculates the threshold to decide whether to return NOT_SURE or the action corresponding to the utterance.
        If the probability of the classifier is below the threshold, NOT_SURE is returned.
        The threshold is determined by looking at the true positive rate and the threshold has result in a true positive
        rate of above 90% (default - can be adjusted).

        :param true_positive_threshold: threshold above which the true positive rate must be
        :param visualize: whether the threshold calculation should be visualized

        :return: the calculated certainty threshold
        """
        # calculate the similarities and true values
        similarities, true_values = self.get_similarities_and_true_values(Data())

        # create y_score values
        predictions = self.classifier.predict(np.array(similarities))

        f1score = []
        tprs = []
        accuracies = []

        thresholds = np.arange(0, 1, 0.01)
        for t in thresholds:
            tp = 0
            fp = 0
            fn = 0
            tn = 0
            for i in range(len(predictions)):
                if predictions[i] >= t and true_values[i] == 1:
                    tp += 1
                elif predictions[i] >= t and true_values[i] == 0:
                    fp += 1
                elif predictions[i] < t and true_values[i] == 1:
                    fn += 1
                elif predictions[i] < t and true_values[i] == 0:
                    tn += 1

            f1 = 2 * tp / (2 * tp + fp + fn)
            true_positive_rate = tp / (tp + fn)
            accuracy = (tp + tn) / (tp + fp + fn + tn)

            f1score.append(f1)
            tprs.append(true_positive_rate)
            accuracies.append(accuracy)

        # set certainty threshold where the F1-Score is highest
        index = np.argmax(f1score)
        self.certainty_threshold = thresholds[index]

        index -= 1
        self.certainty_threshold = thresholds[index]

        if visualize:
            plt.plot(thresholds, f1score, label="F1-Score")
            plt.plot(thresholds, tprs, label="True Positive Rate")
            plt.plot(thresholds, accuracies, label="Accuracy")

            # plt.hlines(true_positive_threshold, xmin=0, xmax=1, colors="red")
            plt.vlines(thresholds[index], ymin=0, ymax=1, colors="red")
            plt.xlabel("Threshold")
            plt.legend()

            plt.show()

        print(f"Certainty threshold was set to {self.certainty_threshold}")
        return self.certainty_threshold

    def get_probabilities(
            self, input_utterance: str
    ) -> Tuple[List[Tuple[str, str, float]], Dict[str, List[str]]]:
        """
        Utilizes the pipeline to retrieve the probabilities for all the saved utterances to find the most likely
        program to be executed.

        :param input_utterance: utterance to be executed

        :return: dictionary of utterances, their corresponding programs and their probability
        """
        # 1. preprocessing of data

        # 2. entity abstraction
        lifted_utterance, entities = self.entity_abstraction.lift_entities(
            input_utterance
        )

        # 3. calculate the embeddings
        embeddings = self.embedding.embed([lifted_utterance] + self.data.utterances)

        input_embedding = embeddings[0]
        embeddings = embeddings[1:]

        # 4. calculate similarities
        similarities = []
        for embedding in embeddings:
            sim = self.similarity.calculate(input_embedding, embedding)
            similarities.append(sim)

        # 5. get probabilities from classifier
        probabilities = self.classifier.predict(np.array(similarities))

        results = list(
            zip(self.data.utterances, self.data.actions, list(probabilities))
        )
        results.sort(key=lambda tup: tup[2], reverse=True)

        return results, entities

    def get_programs(
            self, input_utterance: str
    ) -> List[Dict[str, Union[str, SupportsFloat, Dict[str, Union[str, float, List]]]]]:
        """
        Utilizes the pipeline to get the most probable action (if its probability value is above the certainty threshold
        and uses the recombiner to create the grounded action using the corresponding entities.

        :param input_utterance: utterance to parse

        :return: list of possible programs as dictionaries containing the grounded action (combined with entities),
        lifted action (with entity placeholder), action (as returned by get_program) and entities
        """
        possibilities, entities = self.get_probabilities(
            input_utterance
        )  # possibilities = (utterances, actions, probabilities)

        certain_possibilities = [
            pos for pos in possibilities if pos[2] >= self.certainty_threshold
        ]

        action_list: List[Dict[str, Union[str, SupportsFloat, Dict[str, Union[str, float, List]]]]] = []

        for possibility in certain_possibilities:
            utterance, action, probability = possibility

            # only add if not already present
            if any(elem["general_action"] == action for elem in action_list):
                continue

            (
                pre_lifted_action,
                additional_entities,
            ) = self.entity_abstraction.lift_entities(action)

            merged_entities = {
                "numbers": entities["numbers"] + additional_entities["numbers"],
                "values": entities["values"] + additional_entities["values"],
                "number_lists": entities["number_lists"] + additional_entities["number_lists"],
                "string_lists": entities["string_lists"]
                + additional_entities["string_lists"],
                "conditions": entities["conditions"] + additional_entities["conditions"],
            }

            try:
                (
                    grounded_action,
                    lifted_action,
                    ordered_entities,
                ) = self.combiner.recombine(pre_lifted_action, merged_entities)
                general_action = pre_lifted_action
            except Exception:
                continue

            action_list.append(
                {
                    "training_utterance": utterance,
                    "grounded_action": grounded_action,
                    "lifted_action": lifted_action,
                    "general_action": general_action,
                    "entities": ordered_entities,
                    "probability": str(probability),
                }
            )

        if len(action_list) >= 1:
            return action_list
        else:
            return [
                {
                    "grounded_action": "NOT_SURE",
                    "lifted_action": "NOT_SURE",
                    "general_action": "NOT_SURE",
                    "entities": {},
                }
            ]

    def save_classifier(self, name: str = "./models/server_classifier.model"):
        """
        Saves the classifier to the specified file.

        :param name: file location for saving the model.
        """
        self.classifier.model.save(name)

    def load_classifier(
            self, name: str = "../models/server_classifier.model"
    ) -> Sequential:
        """
        Loads the classifier from the specified file and updates it in self.classifier.

        :param name: file location where the model is stored.

        :return: the loaded model
        """
        self.classifier.model = tensorflow.keras.models.load_model(name)
        self.classifier.model.compile(
            optimizer=Adam(learning_rate=0.005),
            loss=BinaryCrossentropy(),
            metrics=["accuracy"],
        )
        return self.classifier.model

    def reset_classifier(self) -> NeuralNet:
        """
        Resets the training progress of the classifier and initializes it anew.

        :return: the newly initialized model
        """
        self.classifier.__init__()
        return self.classifier
