import csv
from io import StringIO
from os.path import dirname, join
from typing import Dict, List

MAIN_DIRECTORY = dirname(dirname(__file__))


def get_full_path(*path):
    return join(MAIN_DIRECTORY, *path)


class Data:
    def __init__(self, csv_string: str = None, file: str = "./data/atomic_actions.csv"):
        """
        Data class which loads and holds the utterance-action-pairs.

        :param file: relative path to where the atomic actions are defined (must be csv: utterances, actions)
        :param csv_string: csv data in a string, if empty use data from file
        """
        if csv_string is None:
            f = open(get_full_path(file), newline="")
        else:
            f = StringIO(csv_string)

        reader = csv.reader(f)
        next(reader, None)  # skip header line
        self.utterances: List[str] = []
        self.actions: List[str] = []
        self.action_utterance_pairs: Dict[str, List] = {}

        for row in reader:
            self.utterances.append(row[0])
            self.actions.append(row[1])

            if row[1] not in self.action_utterance_pairs:
                self.action_utterance_pairs[row[1]] = [row[0]]
            else:
                self.action_utterance_pairs[row[1]].append(row[0])

        f.close()

    def save_to(self, file: str = "./data/atomic_actions.csv"):
        """
        :param file: file path to where the data should be saved as csv
        """
        f = open(get_full_path(file), "w", newline="")
        writer = csv.writer(f)
        writer.writerow(["# utterance", "action"])
        for utterance, action in zip(self.utterances, self.actions):
            writer.writerow([utterance, action])

        f.close()
