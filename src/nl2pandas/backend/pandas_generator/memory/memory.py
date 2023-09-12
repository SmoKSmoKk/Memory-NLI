from typing import Dict, Union

from nl2pandas.backend.pandas_generator.definitions import DATABASE_PATH
from sqlitedict import SqliteDict


class Database:
    """
    This class saves the actions of a user during the refining process to a database so that they can be
    suggested to them at a later time.
    """

    def __init__(self, file=DATABASE_PATH):
        self.file = file
        self.db = SqliteDict(self.file)

    def save(self, db_items: Dict) -> None:
        """
        Saves the given items to the database

        :param db_items: a dictionary of key-value pairs to save
        :return: None
        """
        try:
            for key, value in db_items.items():
                self.db[key] = value

            self.db.commit()

        except Exception as exception:
            print("Error while storing data: ", exception)

    def load(self, key: str) -> Union[str, None]:
        """
        Loads the value from the database.

        :param key: the dictionary key of the value to load
        :return: value of database item or None
        """

        try:
            value = self.db[key]
            return value

        except KeyError:
            return None

    def delete(self, key: str) -> None:
        """
        Removes the value of the given key from the database.

        :param key: the key of the value to be removed
        :return: None
        """
        try:
            self.db.pop(key)

        except Exception as exception:
            print("Error while deleting item: ", exception)

    def reset(self) -> None:
        """
        Resets the entire dataframe.

        :return: None
        """
        try:
            self.db.clear()

        except Exception as exception:
            print("Error while resetting db: ", exception)
