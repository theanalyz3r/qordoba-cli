import os
import json
import sys
import yaml

DEFAULT_i18n_ML_YML = os.path.abspath(os.path.join("/".join(os.getcwd().split("/")[:-1]), '.i18n-ml.yml'))
DEFAULT_i18n_ML_YAML = os.path.abspath(os.path.join("/".join(os.getcwd().split("/")[:-1]), '.i18n-ml.yaml'))


"""
Onboarding 

1 a.
    bugfixing: make sure execute works correct

1. test:
    4 files send us 
    - .net 
    - c# 
    - js 
    - ruby

2. Documentation

3. configuration
    ignore files/folders
    how you want to write the keys

4. make pretty json

5. tests

"""

IGNOREFILES = [
    ".DS_Store",
    ".gitignore",
    ".git",
    "__init__.pyc",
    "__init__.py",
]


def convert_to_unicode(input):
    """convert strings into unicode"""
    if isinstance(input, dict):
        try:
            return {convert_to_unicode(key): convert_to_unicode(value) for key, value in iterate_items(input)}
        except AttributeError:
            return {convert_to_unicode(key): convert_to_unicode(value) for key, value in iterate_items(input)}
    elif isinstance(input, list):
        return [convert_to_unicode(element) for element in input]
    elif isinstance(input, str) or isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def iterate_items(to_iterate):
    # iterate command, compatible for python 2 and 3 
    if (sys.version_info > (3, 0)):
        # Python 3 code in this block
        return to_iterate.items()
    else:
        # Python 2 code in this block
        return to_iterate.iteritems()


def get_files_in_dir_no_subdirs(directory):
    report = os.path.realpath(directory)
    files = list()
    for file_ in os.listdir(directory):
        if file_ in IGNOREFILES or file_.startswith('.'):
            continue
        files.append(directory + '/' + file_)
    return files


def get_files_in_dir_with_subdirs(path):
    files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def save_str_list_to_file(file_path, file_content):
    with open(file_path, 'w') as output_file:
        for line in file_content:
            output_file.write(line)
        output_file.close()


def save_dict_to_JSON(file_path, file_content):
    with open(file_path, 'w') as output_file:
        dump = json.dumps(file_content, sort_keys=True, indent=4, separators=(',', ': '))
        output_file.write(dump)
        output_file.close()


def get_root_path(path):
    _ROOT = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(_ROOT, path)


def ignore_files(files):
    cleaned_files = [file for file in files if file.split("/")[-1] not in IGNOREFILES]
    return cleaned_files

def load_i18n_config():
    if os.path.isfile(DEFAULT_i18n_ML_YML):
        config = (DEFAULT_i18n_ML_YML)

    if os.path.isfile(DEFAULT_i18n_ML_YAML):
        config = (DEFAULT_i18n_ML_YML)

    with open(config, 'r') as stream:
        try:
            yml_content = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return yml_content


def filter_config_files(files):
    yml_content = load_i18n_config
    ignore_list = yml_content['ignore']
    for path in ignore_list():
        if path.endswith("/"):
            files = [f for f in files if path not in f]
        if path.startswith("."):
            files = [f for f in files if not f.endswith(path)]
        if path not path.startswith(".") and path not path.endswith("/"):




load_files_from_config()