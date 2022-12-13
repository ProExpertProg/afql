import os.path

import yaml

INDEX_TO_CLASS = {}
with open(os.path.dirname(__file__) + "/../classes.yaml") as f:
    content = yaml.load(f, yaml.Loader)
    INDEX_TO_CLASS.update(content['names'])

CLASS_TO_INDEX = {
    INDEX_TO_CLASS[i]: i for i in INDEX_TO_CLASS
}
