import os
import json
import pickle
from enum import Enum
from collections import defaultdict


class TrueCasing():
    class __WordCase(Enum):
        """ an enum that represents all possible word cases """
        Lower = 1
        Upper = 2
        Capital = 3

    
    def __init__(self, corpus_filename, output_filename):
        self.words = []
        self.max_words_context = 4
        self.word_dictionary = defaultdict(int)
        self.corpus_filename = corpus_filename
        self.output_filename = output_filename
        self.__data_corpus = "unifiedDataCorpus.pkl"
        
        self.__parse_file()

    def __parse_file(self):
        """ read the file and create the dictionary and words list """
        
        if not os.path.isfile(self.__data_corpus):
            print("no data corpus")
            # Takes VERY LONG TIME to complete, if the .pkl is not in the folder please contact the author to get a replacement        
            base_line_file_name = "corpus_"
            for i in range(1, self.max_words_context + 1):
                self.__create_data_corpus(self.corpus_filename, "{}{}.pkl".format(base_line_file_name, i), i)
                self.__correct_db("{}{}.pkl".format(base_line_file_name, i), "{}{}.pkl".format(base_line_file_name, i), i)
            
            for i in range(1, self.max_words_context + 1):
                item = pickle.load(open("{}{}.pkl".format(base_line_file_name, i), 'rb'))
                for k, v in item.items():
                    self.word_dictionary[k] = v

            pickle.dump(self.word_dictionary, open(self.__data_corpus, 'wb'))
        else:
            self.word_dictionary = pickle.load(open(self.__data_corpus, 'rb'))
            
        
        print("done reading -> " + str(len(self.word_dictionary)))
    
    @staticmethod
    def __create_data_corpus(fileName, outputFile, max_word_amount=1):
        """ creates a corpus file with sentences of the length of max_word_amount """
        
        unified_word_dictionary = defaultdict(int)
        
        index_minus = (max_word_amount // 2) - int(max_word_amount % 2 == 0)
        index_plus = max_word_amount - index_minus
        
        with open(fileName, 'r', encoding="utf-8") as f:
            
            for index, line in enumerate(f.readlines()):
                line_parts = line.split()
                for i, word in enumerate(line_parts):
                    if i != len(line_parts) - index_plus - 1:
                        unified_word_dictionary[" ".join(line_parts[i - index_minus: i + index_plus])] += 1
                    elif max_word_amount == 1:
                        unified_word_dictionary[word] += 1
                
                if index % 100000 == 0:
                    print(index)
                    
            pickle.dump(dict(filter(lambda x: x[1] > 10, unified_word_dictionary.items())), open(outputFile, 'wb'))
    
    @staticmethod
    def __correct_db(fileName, outputFile, max_word_amount=1):
        """ remove unwanted multiple sentences with the wrong length """
        
        unified_word_dictionary = pickle.load(open(fileName, 'rb'))
        pickle.dump(dict(filter(lambda x: len(x[0].split(" ")) == max_word_amount, unified_word_dictionary.items())), open(outputFile, 'wb'))
    
    def parse(self, text, write_to_file=False):
        """ parse the text and create the true casing for it 
            according to the file and word dictionary """

        self.words = list()
        
        for word in text.lower().split(" "):
            self.__remove_new_line(word, self.words)
        
        trueCaseWordList = list()
        for index, word in enumerate(self.words):
            trueCaseWordList.append(self.__get_word_case(word, index))
        parsed_text = " ".join(trueCaseWordList).replace(" \n ", "\n")

        if write_to_file:
            with open(self.output_filename, 'w', encoding="utf-8") as f:
                f.write(parsed_text)
        else:
            return parsed_text 
    
    @staticmethod
    def __remove_new_line(word, listToAppend):
        """ insert the word parts divided before and after \n
            if the word doesnt has \n append the original word """

        if "\n" in word:
            parts = word.split("\n")
            for i, part in enumerate(parts):
                listToAppend.append(part)
                if i != len(parts) - 1:
                    listToAppend.append("\n")
        else:
            listToAppend.append(word)
    
    def __get_word_case(self, word, index):
        """ get the most likely case of the word using context and the data corpus """
        
        results = {self.__WordCase.Lower : 0, self.__WordCase.Upper : 0, self.__WordCase.Capital : 0}
        
        if word == "\n" or word == " " or word == "":
            return word
        
        if self.__check_new_sentence(word, index):
            return word.capitalize()
        
        for i in range(1, self.max_words_context + 1, 1):
            (_, case) = self.__check_word_varient(word, index, i)
            results[case] += i
        
        max_item = max(results.items(), key = lambda x: x[1])[0]
        
        if max_item == self.__WordCase.Lower:
            return word.lower()
        elif max_item == self.__WordCase.Upper:
            return word.upper()
        else:
            return word.capitalize()
        
    
    def __check_word_varient(self, original_word, index, max_words):
        """ check what varient of the word in a sentence with amax_words is more likely """
        
        result = [0, self.__WordCase.Lower]
        index_minus = (max_words // 2) - int(max_words % 2 == 0)
        index_plus = max_words - index_minus
        
        sentence = " ".join(self.words[index - index_minus : index + index_plus])
        lower_sentence = sentence.replace(original_word, original_word.lower())
        upper_sentence = sentence.replace(original_word, original_word.upper())
        capital_sentence = sentence.replace(original_word, original_word.capitalize())
        
        for case, possible_case in zip(self.__WordCase, [lower_sentence, upper_sentence, capital_sentence]):
            query_result = self.word_dictionary.get(possible_case)
            query_result = query_result if query_result is not None else 0
            
            if result[0] < query_result:
                result[0] = self.word_dictionary[possible_case]
                result[1] = case
        
        return result
    
    def __check_new_sentence(self, word, index):
        """ check and return if the word given is a start of a sentence """
        
        if index == 0:
            return True
        last_word = self.words[index - 1]
        
        if last_word == "\n" or last_word == " " or last_word == "":
            return True
        
        if last_word[-1] == "." or last_word[-1] == '!' or last_word[-1] == '?' or word[0] == '"':
            return True
        return False


def true_case(input_filename, output_filename, corpus_filename):
    
    print('starting true-casing', input_filename, 'into', output_filename, 'using', corpus_filename)
    TrueCasing(corpus_filename, output_filename).parse(open(input_filename, 'r', encoding="utf-8").read(), True)
