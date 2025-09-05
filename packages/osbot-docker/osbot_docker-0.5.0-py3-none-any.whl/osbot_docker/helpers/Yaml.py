import yaml

from osbot_utils.utils.Files import temp_file


class Yaml:
    @staticmethod
    def yaml_dump(python_object):
        return yaml.dump(python_object)

    @staticmethod
    def yaml_load(path_file):
        with open(path_file) as file:
            return yaml.safe_load(file)

    @staticmethod
    def yaml_parse(yaml_code):
        return yaml.safe_load(yaml_code)

    @staticmethod
    def yaml_save(python_object, path_file=None):       #todo: refactor other 'save' methods to have the content as the first param (to allow for creation of temp files when path_file path is not provided)
        if path_file is None:
            path_file = temp_file(extension=".yaml")
        with open(path_file, 'w') as file:
            yaml.dump(python_object, file)
        return path_file

# also add these methods to the top level to allow direct import and usage (without the Yaml.*)

yaml_dump    = Yaml.yaml_dump
yaml_load    = Yaml.yaml_load
yaml_parse   = Yaml.yaml_parse
yaml_save    = Yaml.yaml_save

yaml_to_str  = yaml_dump
yaml_to_json = yaml_parse
str_to_yaml  = yaml_load