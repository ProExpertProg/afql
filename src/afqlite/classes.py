# TODO
import os.path

import yaml

INDEX_TO_CLASS = {}
with open(os.path.dirname(__file__) + "/../classes.yaml") as f:
    content = yaml.load(f, yaml.Loader)
    INDEX_TO_CLASS.update(content['names'])

CLASS_TO_INDEX = {
    INDEX_TO_CLASS[i]: i for i in INDEX_TO_CLASS
}

INDEX_TO_COLUMN = ['timestamp', 'xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class']
NUM_COLUMNS = len(INDEX_TO_COLUMN)

COLUMN_TO_INDEX = {
    column: i for i, column in enumerate(INDEX_TO_COLUMN)
}

