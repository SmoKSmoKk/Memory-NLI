import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CLASSIFIER_PATH = os.path.abspath(os.path.join(ROOT_DIR, '..', 'models', 'server_classifier.model'))

DATABASE_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'memory', 'past_actions.sqlite3'))

TEST_DATABASE_PATH = os.path.abspath(
    os.path.join(ROOT_DIR, '..', 'test', 'pandas_generator', 'memory', 'test_db.sqlite3')
)
