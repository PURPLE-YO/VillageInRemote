import pandas as pd
import json
import numpy as np
import time
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
    filtered_df = input_dataframe[input_dataframe.index == supplier_list]

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
        exact_date = np.datetime64(dateRange['Start Date'])
        # key = column name, value = keyword
        target_time = input_frame[input_frame['Start Date'] == exact_date]
    # if search a range
    else:
        # convert datatype to datetime64, match the data in dataframe
        start = np.datetime64(dateRange['Start Date'])
        end = np.datetime64(dateRange['End Date'])
        # mask target_time
        target_time = input_frame[(input_frame['Start Date'] <= end) & (input_frame['Start Date'] >= start)]
    # return filtered dataframe
    return target_time


def category_match(key_word, input_dataframe):
    category_list = []
    # give score benchmark as 70 to cut down not useful data
    temp = process.extractBests(key_word, input_dataframe['UNSPSC Title'], limit=input_dataframe.shape[0],
                                score_cutoff=70)
    for item in temp:
        category_list.append(item[2])
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


# def value_match(range, input_dataframe):
#     lower_bound = range['Low Bound']
#     upper_bound = range['Upper Bound']
#     target_value = input_dataframe[(input_dataframe['Value'] <= upper_bound) & (input_dataframe['Value'] >= lower_bound)]
#     date_


def find_match(keyword, input_frame):
    """
    Apply all filters according to UI sent command
    @param keyword: dictionary -> {'column name': keyword}
    @return:
    """
    filtered_df = input_frame
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
            dateRange = value[0]
            # return filtered Contract ID and dataframe after filter
            filtered_df = date_match(dateRange, filtered_df)
            # print("1", filtered_df.shape[0])

        elif key == "Supplier Name":
            # may have multiple words input in supplier
            # supplier1 OR supplier2 OR ...
            temp = pd.DataFrame()
            for words in value:
                temp = pd.concat([temp, supplier_match(words, filtered_df)], join='outer')
            filtered_df = temp
            # print("2", filtered_df.shape[0])

        elif key == 'Category':
            temp = pd.DataFrame()
            # user may tick multiple categories
            for words in value:
                print("3", category_match(words, filtered_df).shape[0])
                temp = pd.concat([temp, category_match(words, filtered_df)], join='outer')
            filtered_df = temp
            # print("5", filtered_df.shape[0])

        elif key == 'Procurement Method':
            # user may enter one or more options
            for method in value:
                filtered_df = procurement_match(method, filtered_df)

        # "Panel Arrangement" or
        # "Confidentiality Contract Flag" or
        # "Confidentiality Outputs Flag" or
        # "Consultancy Flag"
        # only have two options of "yes/no"
        elif key == ("Panel Arrangement" or "Confidentiality Contract Flag" or
                     "Confidentiality Outputs Flag" or
                     "Consultancy Flag"):
            filtered_df = filtered_df[filtered_df[key] == value]

    filtered_id = filtered_df.index.tolist()
    return filtered_id


# ---------------------------main----------------------------------
start_time = time.time()
keyword = unpack("test2.json")
output = find_match(keyword, df)
print("output: ", len(output), output)
print("time-consuming: ", time.time() - start_time)
# output_json = json.dumps({"Contract ID": output, "UI Command": keyword})
# print(output_json)
