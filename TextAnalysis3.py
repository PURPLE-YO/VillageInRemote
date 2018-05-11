#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
    Author: Jianying Zhang
    Date created: 19/04/2018
    Date last modified: 24/04/2018
    Python Version: 3.6
'''

import pandas as pd
import json
import numpy as np
import time
from fuzzywuzzy import process
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn

# open csv file as dataframe
df = pd.read_csv('/Users/purple/Desktop/All CN.csv', low_memory=False)

# convert to time format, dtype: datetime64[ns]
df['Start Date'] = pd.to_datetime(df['Start Date'])
'''
    Receive the json data from UI
    Get keyword to search
'''

'''
Case 1 – What contracts have been awarded to universities from panels in 2014
    fromUI = {
        'Agency Name':[],
        'Publish Date':[],
        'Start Date':[2014/1/],
        'End Date':[2014/12/31],
        'Value':[<bottom>,<top>],
        'Description':'',
        'UNSPSC Code':'',
        'UNSPSC Title':'uni*',
        'Procurement Method':'',
        'Panel Arrangement':'',
        'Confidentiality Contract Flag':'',
        'Confidentiality Contract Reason':'',
        'Confidentiality Outputs Flag':'',
        'Confidentiality Outputs Reason':'',
        'Consultancy Flag':'',
        'Consultancy Reason':'',
        'Supplier Name':'',
        'Supplier ABN':''}
'''


def unpack(fromUI):
    """
    Parse the json command from UI
    Unpack json data and fetch keyword from not None value

    @param fromUI: json format data sent from user interface
    @return: field with keyword
    @rtype: object
    """
    # read input json
    read = open(fromUI, 'r')
    # parse it as dictionary
    command = json.load(read)

    if command['Source'] != "UI":
        print('Command is not from UI')
    else:
        del command['Source']
        return command


# match the keyword of supplier
def supplier_match(key_word, input_dataframe):
    """

    @param dataframe: input datafram -> dataframe
    @param key_word: input supplier keyword -> str
    @return: set of contract id
    """
    supplier_list = []
    # process.extract -> list[(tuple),(tuple)]
    score = process.extractBests(key_word, input_dataframe['Supplier Name'], score_cutoff=80,
                                 limit=input_dataframe.shape[0])
    for item in score:
        supplier_list.append(item[2])

    filtered_df = input_dataframe.loc[supplier_list]
    # return dataframe after filtered
    return filtered_df


def date_match(dateRange, input_frame):
    """
    Find row index with matched dates

    @param range: date range in a dictionary range:{'Start Date':'yyyy-mm-dd', 'End Date':'yyyy-mm-dd'} -> dtype: dictionary
    @param input_frame:
    @return: set of date match -> dtype: set
    """
    # find match with a exact date, output one element
    if dateRange['Start Date'] == dateRange['End Date']:
        # convert dtype to datetime64, match the data in dataframe
        exact_date = np.datetime64(dateRange['Start Date'])
        # key = column name, value = keyword
        target_time = input_frame[input_frame['Start Date'] == exact_date]
    # if search a range
    else:
        # check if only one parameter received
        if dateRange['Start Date'] == '' or dateRange['End Date'] == '':
            # only start date specified, return the data from input date to the most recent
            if dateRange['End Date'] == '':
                # convert datatype to datetime64, match the data in dataframe
                start = np.datetime64(dateRange['Start Date'])
                target_time = input_frame[input_frame['Start Date'] >= start]
            # only end date specified, return all the data before input date
            else:
                # convert datatype to datetime64, match the data in dataframe
                end = np.datetime64(dateRange['End Date'])
                target_time = input_frame[input_frame['Start Date'] <= end]
        else:
            # convert datatype to datetime64, match the data in dataframe
            start = np.datetime64(dateRange['Start Date'])
            end = np.datetime64(dateRange['End Date'])
            # mask target_time
            target_time = input_frame[(input_frame['Start Date'] <= end) & (input_frame['Start Date'] >= start)]
    # return filtered dataframe
    return target_time


def category_multi_match(word_list, input_dataframe):
    """
    phrase match e.g Health services
    @param word_list: phrases splited into word list
    @param input_dataframe:
    @return:
    """
    temp_set = set()
    for word in word_list:
        # initial union with empty set
        if len(temp_set) == 0:
            temp_set = temp_set.union(index_dict[word])
        # filtered unnecessary index
        else:
            temp_set = temp_set.intersection(index_dict[word])
    # final list return
    category_list = list(temp_set)
    # filtered dataframe return
    filtered_df = input_dataframe.loc[category_list]
    return filtered_df


# find synonyms with the keyword input
# catch union set to return all related titles
def find_synonyms(input_word, keys_set):
    syn_set = wn.synsets(input_word)
    temp_set = set()
    for word_set in syn_set:
        temp_set |= set(word_set.lemma_names())
    intersection = keys_set & temp_set
    return intersection


def category_match(single_word, input_dataframe):
    """single word match for category
    @param single_word:
    @param input_dataframe:
    @return:
    """
    temp_set = set()
    synonyms = find_synonyms(single_word, keys_set)
    for word in synonyms:
        temp_set |= index_dict[word]
    category_list = list(temp_set)
    filtered_df = input_dataframe.loc[category_list]
    return filtered_df


def procurement_match(key_word, input_dataframe):
    """
    Procurement method has three options: Limited tender, Open tender, Prequalified tender

    @param key_word: ticked option of procurement method
    @param input_dataframe: uploaded datagrame
    @return: filtered set
    """
    matched = input_dataframe[input_dataframe['Procurement Method'] == key_word]
    return matched


def value_match(valueRange, input_dataframe):
    if valueRange['Lower Bound'] == valueRange['Upper Bound']:
        # convert format to float64 to match with dataframe
        exact_value = np.float64(valueRange['Lower Bound'])
        target_value = input_dataframe[input_dataframe['Value'] == exact_value]
    else:
        # convert format to float64 to match with dataframe
        low = np.float64(valueRange['Lower Bound'])
        high = np.float64(valueRange['Upper Bound'])
        target_value = input_dataframe[(input_dataframe['Value'] <= high) & (input_dataframe['Value'] >= low)]
    return target_value


def find_match(keyword, input_frame):
    """
    Apply all filters according to UI sent command
    @param keyword: dictionary -> {'column name': keyword}
    @return:
    """
    filtered_df = input_frame
    for key, value in keyword.items():
        if key == "Date Range":
            dateRange = value[0]
            # return new dataframe as base for next filter
            filtered_df = date_match(dateRange, filtered_df)

        elif key == "Supplier Name":
            temp = pd.DataFrame()
            # may have multiple words input in supplier
            # supplier1 OR supplier2 OR ...
            # merge dataframe with different supplier name
            for words in value:
                temp = pd.concat([temp, supplier_match(words, filtered_df)], join='outer')
            # return new dataframe as base for next filter
            filtered_df = temp

        elif key == 'Procurement Method':
            # user may enter one or more options
            # if only one method input
            temp_list = []
            # only one method input
            if len(value) == 1:
                filtered_df = procurement_match(value[0], filtered_df)
            # multiple methods input
            else:
                for method in value:
                    temp_df = procurement_match(method, filtered_df)
                    temp_list.append(temp_df)
                # return new filtered dataframe
                filtered_df = pd.concat(temp_list)

        # "Panel Arrangement" or
        # "Confidentiality Contract Flag" or
        # "Confidentiality Outputs Flag" or
        # "Consultancy Flag"
        # only have two options of "yes/no"
        elif key == ("Panel Arrangement" or "Confidentiality Contract Flag" or
                     "Confidentiality Outputs Flag" or
                     "Consultancy Flag"):
            filtered_df = filtered_df[filtered_df[key] == value]

        elif key == "Supplier Name":
            temp = pd.DataFrame()
            # may have multiple words input in supplier
            # supplier1 OR supplier2 OR ...
            # merge dataframe with different supplier name
            for words in value:
                temp = pd.concat([temp, supplier_match(words, filtered_df)], join='outer')
            # return new dataframe as base for next filter
            filtered_df = temp

        elif key == 'ValueRange':
            valueRange = value[0]
            # return new dataframe as base for next filter
            filtered_df = value_match(valueRange, filtered_df)

        elif key == 'Category':
            temp = pd.DataFrame()
            # user may tick multiple categories
            for words in value:
                # phrase input (e.g health services)
                if len(words.split(' ')) > 1:
                    # join a list of dataframes
                    phrase_list = words.split(' ')
                    temp = pd.concat([temp, category_multi_match(phrase_list, filtered_df)], join='outer')
                # for single word search and combine to previous dataframe
                else:
                    temp = pd.concat([temp, category_match(words, filtered_df)], join='outer')
            # return new dataframe as base for next filter
            filtered_df = temp

    filtered_id = filtered_df.index.tolist()
    return filtered_id


# ---------------------------main----------------------------------
start_time = time.time()
# convert column to string

# preprocess data for dictionary builder
temp_df = df['UNSPSC Title'].apply(str)
# convert all to lower case
temp_df = temp_df.apply(str.lower)
lemma = nltk.wordnet.WordNetLemmatizer()
temp_df = temp_df.apply(lemma.lemmatize)
temp_df = temp_df.apply(word_tokenize)
stop_words = set(stopwords.words('english'))
filtered_bag = set()
# create dictionary within the scope of whole program for reference
index_dict = dict()
# store all the keys into a set for match within the scope of whole program for reference
keys_set = set(index_dict.keys())

# build dictionary with token
for i in range(temp_df.shape[0]):
    for word in temp_df[i]:
        if word not in stop_words:
            if word not in filtered_bag:
                filtered_bag.add(word)
                index_dict[word] = set()
                # add index to the set
                index_dict[word].add(i)
            else:
                index_dict[word].add(i)

keyword = unpack("test2.json")
output = find_match(keyword, df)
print(df.loc[output]['Procurement Method'])

print("time-consuming: ", time.time() - start_time)
