import pandas as pd
import json
import numpy as np

from fuzzywuzzy import process

# open csv file as dataframe
df = pd.read_csv('/Users/purple/Desktop/All CN.csv', index_col=2, low_memory=False)
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
        # try:
        #     # find the target keyword in which certain column
        #     for key, value in command.items():
        #         if value is not None:
        #             keyword[key] = value
        #     return keyword
        # except Exception as inst:
        #     print(type(inst))  # the exception instance
        #     print(inst.args)  # arguments stored in .args
        #     print(inst)

# match the keyword of supplier
def supplier_match(key_word, dataframe):
    """

    @param dataframe: input datafram -> dataframe
    @param key_word: input keyword -> str
    @return: set of contract id
    """
    supplier_set = set()
    # process.extract -> list[(tuple),(tuple)]
    score = process.extractBests(key_word, dataframe['Supplier Name'], score_cutoff=80, limit=df.shape[0])
    for item in score:
        supplier_set.add(item[2])
    return supplier_set


def date_match(range, input_frame):
    """
    Find row index with matched dates

    @param range: date range in a dictionary range:{'Start Date':'yyyy-mm-dd', 'End Date':'yyyy-mm-dd'} -> dtype: dictionary
    @param input_frame:
    @return: set of date match -> dtype: set
    """
    # find match with a exact date, output one element
    if range['Start Date'] == range['End Date']:
        exact_date = np.datetime64(range['Start Date'])
        # key = column name, value = keyword
        target_time = input_frame[input_frame['Start Date'] == exact_date]
    # if search a range
    else:
        # convert datatype to datetime64, match the data in dataframe
        start = np.datetime64(range['Start Date'])
        end = np.datetime64(range['End Date'])
        # mask target_time
        target_time = input_frame[(input_frame['Start Date'] <= end) & (input_frame['Start Date'] >= start)]
    # store matched index in a list
    date_match = target_time.index.tolist()
    # convert list to set
    date_set = set(date_match)
    return date_set


def find_match(keyword, input_frame):
    """


    @param keyword: dictionary -> {'column name': keyword}
    @return:
    """
    for key, value in keyword.items():
        '''
        if key == "Date Range":
            # find range -> Dictionary {"Start Date":"","End Date":""}
            range = value[0]
            # find match with a exact date, output one element
            if range['Start Date'] == range['End Date']:
                exact_date = np.datetime64(range['Start Date'])
                # key = column name, value = keyword
                target_time = input_frame[input_frame['Start Date'] == exact_date]
            else:
                # convert dtype to datetime64, match the data in dataframe
                start = np.datetime64(range['Start Date'])
                end = np.datetime64(range['End Date'])
                # mask target_time
                target_time = input_frame[(input_frame['Start Date'] <= end) & (input_frame['Start Date'] >= start)]
                print('else')
            print(target_time)
        '''
        '''
            supplier_match(key, input_frame)
            cn_set = set()
            # process.extract -> list[(tuple),(tuple)]
            score = process.extractBests(value, input_frame['Supplier Name'], score_cutoff=80, limit=df.shape[0])

            for item in score:
                cn_set.add(item[2])
            return cn_set
        '''

        if key == "Date Range":
            range = value[0]
            date_index = date_match(range, input_frame)

        if key == "Supplier Name":
            supplier_index = set()
            for words in value:
                temp_set = supplier_match(words, input_frame)
                supplier_index |= temp_set


keyword = unpack("test.json")
find_match(keyword, df)

