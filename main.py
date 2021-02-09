# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import nltk

from summary_generators.frequency_summary import get_summary_for_documents
from summary_generators.ti_idf_summary import generate_tf_idf_summary_alternative, get_most_used_phrases

nltk.download('averaged_perceptron_tagger')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_summary_for_documents()
    # generate_tf_idf_summary_alternative()
    #get_most_used_phrases()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
