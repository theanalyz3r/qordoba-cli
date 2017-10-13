import pandas as pd
from qordoba.settings import get_localization_files
from qordoba.commands.i18n_base import BaseClass, FilesNotFound
import logging
try:
    # Python 2
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip
import os

log = logging.getLogger('qordoba')

class ReportNotValid(Exception):
    """
    Files not found
    """

"""
This command will match StingLiterals to existing localization files. 
If the StringLiteral already exists as a value, it will return the key. 
If the StringLiteral already exists as a key, it will return the key. 
On top, it will then generate new keys for each Stringliteral and 
add the results as new columns to existing report (CSV)"""

'''
to do: 
add csv, yaml to test
find bug -- key value nested dict
change find-new to input and output, -- .qorignore
'''

KEY_COUNT = 0
INVALID_FILES = ['.DS_STORE']


class i18nGenerateClass(BaseClass):

    # def generate_CSV_with_key_column(self, filepath, df):
    #     # adding key column to Dataframe with existing keys
    #     log.info("StringLiterals  were matched to existing keys. Generating new CSV ")
    #     beginning = '/'.join(filepath.split('/')[:-1])
    #     filename = filepath.split('/')[-1]
    #     filename_new = '/key-' + filename
    #
    #     csv_file = beginning + filename_new
    #     df.to_csv(csv_file, index=False, encoding='utf-8')
    #     log.info("scanned localization files for existing keys. Added keys to CSV.")
    #     return df

    def get_existing_i18n_key_values(self, localization_files):
        keys_values_localisation_files = dict()
        for file in localization_files:
            dictionary = self.get_nested_dictionary(file)
            key_values = self.get_all_keys(dictionary, list(), dict())
            key_values = self.convert(key_values)
            keys_values_localisation_files[file] = key_values
        # return self.convert(keys_values_localisation_files)
        return keys_values_localisation_files

    def index_lookup(self, stringLiteral, localization_k_v):
        # checks if stringLiteral exists in values, gives back corresponding key or None
        for i18n_file in localization_k_v:
            for key, value in localization_k_v[i18n_file].items():
                if value.strip() == stringLiteral.strip():
                    return key, i18n_file
                if key.strip() == stringLiteral.strip():
                    return key, i18n_file
        return None, None

    def generate_new_keys(self, stringLiteral):
        '''
        For now keys will be generated by taking the 2 words from the String
        which have the least frequency count within the Open National Corpus (spoken & written)
        source http://www.anc.org/data/anc-second-release/frequency-data/
        '''

        global KEY_COUNT
        KEY_COUNT += 1
        if KEY_COUNT%20 == 0:
            log.info("{} keys created ".format(KEY_COUNT))

        # ANC_csv = '../resources/ANC-all-count.csv'
        ANC_csv = 'ANC-all-count.csv'
        column_names = ['word', 'againWords', 'type', 'count']
        try:
            df_ANC = pd.read_csv(ANC_csv, names=column_names)
        except UnicodeDecodeError:
            df_ANC = pd.read_csv(ANC_csv, names=column_names, encoding='latin-1')
        # trying to make sense of this BS = need different approach
        stringLiteral = stringLiteral.replace('-', ' ')
        stringLiteral = stringLiteral.replace('.', ' ')
        stringLiteral = stringLiteral.replace('/', ' ')
        stringLiteral = stringLiteral.replace('_', ' ')
        words = stringLiteral.split(" ")
        words = [word.lower() for word in words if word.isalpha()]

        if len(words) == 1:
            return words[0]

        elif len(words) == 0:
            return stringLiteral

        elif len(set(words).intersection(df_ANC.word)) <= 1:
            word_tuple = (sorted(words,  key=len)[-2:])
            return '.'.join(set(([word_tuple[0],word_tuple[1]]))),

        else:
            w1 = None
            w2 = None
            v1 = 0
            v2 = 0
            for w in words:
                # the words with the lowest count
                a = df_ANC.loc[df_ANC['word'] == w]
                s = sum((a['count'].values))
                if v2 == 0 and v1 == 0:
                    v1 = s
                    v2 = s
                    w1 = w
                    w2 = w
                elif s < v1:
                    v1 = s
                    w1 = w
                elif s < v2 < v1:
                    v2 = s
                    w2 = w
                else:
                    continue
            return '.'.join(set(([w1,w2])))

    def generate(self, _curdir, report=None, localization=None):

        for filename in os.listdir(report):

            """!!!!! toDo: validate csv report"""

            if not filename.endswith(".csv"):
                continue
            filename_path = report + '/' + filename
            if not self.validate_report(filename_path, keys=False):
                raise ReportNotValid("The given report is not valid. ")

            df = pd.read_csv(filename_path, header=0)
            # converting StringLiterals to pure strings
            (df.text) = (df.text).apply(lambda x: x[:4].replace('"', ''))
            (df.text) = (df.text).apply(lambda x: x[:4].replace("'", ''))
            (df.text) = (df.text).apply(lambda x: x[-4:].replace('"', ''))
            (df.text) = (df.text).apply(lambda x: x[-4:].replace("'", ''))
            (df.text) = (df.text).apply(lambda x: x.strip())
            """
            Based on the given localization directory. 
            Getting existing key value pairs from localization files and updating dataframe.
            
            --> lookup if Stringliteral exists as value or key in a localization file. 
                If yes, return key, otherwise None.
            """
            if localization:
                localization_files = []
                for loc_file in os.listdir(localization):
                    if not loc_file.startswith('.'):
                        localization_files.append(localization + '/' + loc_file)

                localization_k_v = self.get_existing_i18n_key_values(localization_files)
                log.info(" ... searching if existing keys exist.")
                df['existing_keys'], df['existing_localization_file'] = izip(*df.iloc[:,-1].apply(lambda x: self.index_lookup(x, localization_k_v)))

                log.info("  " + u"\U0001F4AB" + u"\U0001F52E" + " .. starting to generate new keys for you - based on the extracted Strings from your files.")
                log.info(" (This could Take some time)")
                log.info("\b")


            '''generate new keys and update existing CSV report
            New keys are generated by picking the two lowest frequence word of english corpus within given string'''
            df['generated_keys'] = (df.text).apply(lambda x: self.generate_new_keys(x))
            os.remove(filename_path)
            df.to_csv(filename_path, encoding='utf-8', index=False)
            log.info("Process completed. " + u"\U0001F680" + u"\U0001F4A5")