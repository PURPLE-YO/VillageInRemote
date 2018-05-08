#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:38:11 2018
@author: NAN
"""
import pandas as pd
import json
import numpy as np
from fuzzywuzzy import process
import webbrowser as wb
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize



class Pre_process:
    
    upload_Dataframe = pd.DataFrame()
    cleaned_Dataframe = pd.DataFrame()
    listOfFields = []
    output = ''
    
    def upload_file(self,filename):
        while True:
            try:              
                self.upload_Dataframe = pd.read_csv(filename,low_memory=False)
                self.listOfFields = list(self.upload_Dataframe)
#                self.upload_Dataframe = self.optimize_df
                self.data_cleansing()
#                self.cleaned_Dataframe = self.cleaned_Dataframe.set_index('Contract ID') # re-set the index by using Contract ID
                self.cleaned_Dataframe = self.optimize_df(self.cleaned_Dataframe)
                self.cleaned_Dataframe = self.re_space_cap(self.cleaned_Dataframe)
                self.output = 'Pass'
                break
            except FileNotFoundError:
                self.output = "File Not Found!"
            except SyntaxError:
                self.output = "SyntaxError, file path should be C:/Users/data.csv"
    
        # eliminate space before and after the string variables, and lower all strs
        # and STRIPING (NON-RELEVANT) PUNCTUATION
    def re_space_cap(self,df):
        df['Agency Name'] = df['Agency Name'].apply(str.strip).apply(str.lower)
        df['Agency Name'] = df['Agency Name'].apply(
                lambda x : x.translate(str.maketrans("", "", ",.-'\"():;+&/?$°@")))
#        uni_agency = self.cleaned_Dataframe['Agency Name'].unique()
        
        df['Supplier Name'] = df['Supplier Name'].apply(str.strip).apply(str.lower)
        df['Supplier Name']= df['Supplier Name'].apply(
                lambda x : x.translate(str.maketrans("", "", ",.-'\"():;+/&?$°@")))
#        uni_supplier = self.cleaned_Dataframe['Supplier Name'].unique()
        
        df['UNSPSC Title'] = df['UNSPSC Title'].apply(str.strip).apply(str.lower)
        df['UNSPSC Title']= df['UNSPSC Title'].apply(
                lambda x : x.translate(str.maketrans("", "", ",.-'\"():;+/&?$°@")))
#        uni_title = self.cleaned_Dataframe['UNSPSC Title'].unique()   
        df['Supplier Country'] = df['Supplier Country'].apply(str.strip).apply(str.lower)
        df['Supplier Country']= df['Supplier Country'].apply(
                lambda x : x.translate(str.maketrans("", "", ",.-'\"():;+/&?$°@")))        
        return df
    
     # data cleansing -- handling missing value
    def data_cleansing(self):
        df = self.upload_Dataframe
        # convert to time format, dtype: datetime64[ns]
        df['Start Date'] = pd.to_datetime(df['Start Date'],infer_datetime_format=True,errors='coerce')
        df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce',infer_datetime_format=True)
        df['Amendment Date'] = pd.to_datetime(df['Amendment Date'],errors='coerce',infer_datetime_format=True)
        # searching for missing values in columns
        nan_col_any = df.isnull().any()  # for any column that includes Nan
        nan_col_all = df.isnull().all()  # for any column that all value is Nan
        # extract the list of Nan included columns
        nan_features_any = pd.Series(list(nan_col_any[nan_col_any == True].index))
        # eatract the list of all Nan columns
        nan_features_all = pd.Series(list(nan_col_all[nan_col_all == True].index))
        # if exist entire Nan values columns
        if nan_features_all.empty != True:
            for each in nan_features_all:
                df.drop(each, axis=1, inplace=True)  # delete entire column without reassign to df
        # for Nan value included columns, implement data cleansing(fillna method)
        if nan_features_any.empty != True:
            for features in nan_features_any:
                if features == 'UNSPSC Title':
                    list_of_nan = []
                    for index in range(df.shape[0]):
                        if type(df.loc[index, features]) != str:
                            list_of_nan.append(
                                index)  # acquire a list contain all index of Nan value in the Title column
                    nan_UNSPSC_Code = []
                    for each in list_of_nan:
                        nan_UNSPSC_Code.append(df.loc[each, 'UNSPSC Code'])
                    nan_UNSPSC_Code = list(
                        map(str, nan_UNSPSC_Code))  # get the corresponding value in UNSPSC Code
                    for index in range(len(list_of_nan)):
                        # use UNSPSC ID to replace the Nan Value
                        df.loc[list_of_nan[index], features] = nan_UNSPSC_Code[index]
                elif features == 'Supplier ABN':  # value float [79097795125.0]
                    df.loc[:, features] = df.loc[:, features].fillna(float(0))  # use 0.0 replace Nan in this field
            df = df.fillna('N/A')
            self.cleaned_Dataframe = df
 
    def optimize_df(self,df): # resize dtype of int, float, object columns for memory usage saving        
#        df_int = df.select_dtypes(include=['int'])
#        converted_int = df_int.apply(pd.to_numeric,downcast='unsigned')
        
        df_float = df.select_dtypes(include=['float'])
        converted_float = df_float.apply(pd.to_numeric,downcast='float')
        
        df_obj = df.select_dtypes(include=['object']).copy()
        converted_obj = pd.DataFrame()
        for col in df_obj.columns:
            num_unique_values = len(df_obj[col].unique())
            num_total_values = len(df_obj[col])
            if num_unique_values / num_total_values < 0.5:
                converted_obj.loc[:,col] = df_obj[col].astype('category')
            else:
                converted_obj.loc[:,col] = df_obj[col]
        
        optimized_df = df.copy()
#        optimized_df[converted_int.columns] = converted_int
        optimized_df[converted_float.columns] = converted_float
        optimized_df[converted_obj.columns] = converted_obj
        
        return optimized_df
    
    
        
        
class TextAnalysis:
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
    # preprocess data for dictionary builder
    temp_df = pd.DataFrame()
    # convert all to lower case
    lemma = nltk.wordnet.WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    filtered_bag = set()
    index_dict = dict()
    
    
                    
    def title_dict(self,dataframe):
        temp_df = dataframe['UNSPSC Title'].apply(str)
        temp_df = temp_df.apply(str.lower)
        temp_df = temp_df.apply(self.lemma.lemmatize)
        self.temp_df = temp_df.apply(word_tokenize)
        
        # build dictionary with token
        for i in range(self.temp_df.shape[0]):
            for word in self.temp_df[i]:
                if word not in self.stop_words:
                    if word not in self.filtered_bag:
                        self.filtered_bag.add(word)
                        self.index_dict[word] = set()
                        # add index to the set
                        self.index_dict[word].add(i)
                    else:
                        self.index_dict[word].add(i)
    
    def unpack(self,fromUI):
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
    def supplier_match(self,key_word, input_dataframe):
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
    
    
    def date_match(self,dateRange, input_frame):
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
            # only a start date or an end date entered
            if dateRange['Start Date'] == '' or dateRange['End Date'] == '':
                # only a start date input, then return the data from entered date to most recent
                if dateRange['End Date'] == '':
                    start = np.datetime64(dateRange['Start Date'])
                    target_time = input_frame[input_frame['Start Date'] >= start]
                # only an ende date input, then return the data before the entered date
                else:
                    end = np.datetime64(dateRange['End Date'])
                    target_time = input_frame[input_frame['Start Date'] <= end]
            # convert datatype to datetime64, match the data in dataframe
            else:
                start = np.datetime64(dateRange['Start Date'])
                end = np.datetime64(dateRange['End Date'])
                # mask target_time
                target_time = input_frame[(input_frame['Start Date'] <= end) & (input_frame['Start Date'] >= start)]
        # return filtered dataframe
        return target_time
    
    
    def category_multi_match(self,word_list, input_dataframe):
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
                temp_set = temp_set.union(self.index_dict[word])
            # filtered unnecessary index
            else:
                temp_set = temp_set.intersection(self.index_dict[word])
        # final list return
        category_list = list(temp_set)
        # filtered dataframe return
        filtered_df = input_dataframe.loc[category_list]
        return filtered_df
    
    
    def category_match(self,single_word, input_dataframe):
        """single word match for category
        @param single_word:
        @param input_dataframe:
        @return:
        """
        temp_set = self.index_dict[single_word]
        category_list = list(temp_set)
        filtered_df = input_dataframe.loc[category_list]
        return filtered_df
    
    
    def procurement_match(self,key_word, input_dataframe):
        """
        Procurement method has three options: Limited tender, Open tender, Prequalified tender
        @param key_word: ticked option of procurement method
        @param input_dataframe: uploaded datagrame
        @return: filtered set
        """
        matched = input_dataframe[input_dataframe['Procurement Method'] == key_word]
        return matched
    
    
    def find_match(self,keyword, input_frame):
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
                filtered_df = self.date_match(dateRange, filtered_df)
    
            elif key == "Supplier Name":
                temp = pd.DataFrame()
                # may have multiple words input in supplier
                # supplier1 OR supplier2 OR ...
                # merge dataframe with different supplier name
                for words in value:
                    temp = pd.concat([temp, self.supplier_match(words, filtered_df)], join='outer')
                # return new dataframe as base for next filter
                filtered_df = temp
    
            elif key == 'Procurement Method':
                # user may enter one or more options
                for method in value:
                    filtered_df = self.procurement_match(method, filtered_df)
    
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
                    temp = pd.concat([temp, self.supplier_match(words, filtered_df)], join='outer')
                # return new dataframe as base for next filter
                filtered_df = temp
    
            elif key == 'Category':
                temp = pd.DataFrame()
                # user may tick multiple categories
                for words in value:
                    # phrase input (e.g health services)
                    if len(words.split(' ')) > 1:
                        # join a list of dataframes
                        phrase_list = words.split(' ')
                        temp = pd.concat([temp, self.category_multi_match(phrase_list, filtered_df)], join='outer')
                    # for single word search and combine to previous dataframe
                    else:
                        temp = pd.concat([temp, self.category_match(words, filtered_df)], join='outer')
                # return new dataframe as base for next filter
                filtered_df = temp
    
        filtered_id = filtered_df.index.tolist()
        return filtered_id     


# ---------------------------main---------------------------------- test only
if __name__ == '__main__':    
    import time
    start_time = time.time()
    
    from dashV5 import Dashboard
    
    txtA = TextAnalysis()
    print("--- %s seconds ---set up TextAnalysis object" % (time.time() - start_time))
    proc = Pre_process()
    print("--- %s seconds ---set up Pre_process object" % (time.time() - start_time))
    proc.upload_file('All_data.csv')
    print("--- %s seconds ---upload_file" % (time.time() - start_time))
    df = proc.cleaned_Dataframe.sort_values(by='Value',ascending=False)    
    print("--- %s seconds ---cleaned_Dataframe" % (time.time() - start_time))
  
    txtA.title_dict(df) # create corpus [must]
    corpus = txtA.index_dict
    print("--- %s seconds ---set the corpus for text analysis" % (time.time() - start_time))
    
    keyword = txtA.unpack("test3.json")
    print("--- %s seconds ---unpack, read json" % (time.time() - start_time))

    output = txtA.find_match(keyword, df)
    df_new = df.loc[output]
    print("--- %s seconds ---find_match" % (time.time() - start_time))

    dash = Dashboard()
    print("--- %s seconds --- create object of Dashboard" % (time.time() - start_time))
    if 'Category' in keyword.keys():
        dict_df = dash.select_rows(filtered_df=df_new,corpus=corpus,searching_dict=keyword)
        url = dash.pie_plot_by_cat(dict_filtered_df=dict_df,original_df=df)
        wb.open(url)
        print("--- %s seconds --- output dash url - pie-by-category" % (time.time() - start_time))
        url2 = dash.hbar_by_cat(dict_filtered_df=dict_df,Procurement='Open tender')
        wb.open(url2)
        print("--- %s seconds --- output dash url - hbar_by_cat" % (time.time() - start_time))
        
    url1 = dash.pie_plot_by_key(df_new,keyword)
    wb.open(url1)
    print("--- %s seconds --- output dash url - pie-by-keywords" % (time.time() - start_time))
    
    
    print("--- %s seconds --- output dash url" % (time.time() - start_time))
