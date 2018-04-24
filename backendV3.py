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
from nltk.corpus import stopwords


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
#                if features == 'Parent Contract ID':
#                    df.loc[:, features] = df.loc[:, features].fillna('None')
#                elif features == 'Description':
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Agency Ref ID':
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
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
#                elif features == 'ATM ID':
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'SON ID':
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Panel Arrangement':  # value str [Yes/No]
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Confidentiality Contract Flag':  # value str [No]
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Confidentiality Contract Reason':  # value str
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Confidentiality Outputs Flag':  # value str [No]
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Confidentiality Outputs Reason':  # value str
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Consultancy Flag':  # value str [Yes/No]
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Consultancy Reason':  # value str [ex:Skills currently unavailable within agency]
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Amendment Reason':  # value str [ex:Contract value increased from $932,144.50]
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Supplier Address':  # value str
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Supplier Suburb':  # value str
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Supplier Postcode':  # value str like numbers
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Supplier ABN':  # value float [79097795125.0]
                    df.loc[:, features] = df.loc[:, features].fillna(float(0))  # use 0.0 replace Nan in this field
#                elif features == 'Contact Phone':  # value str like num
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Branch':  # value str
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Division':  # value str
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
#                elif features == 'Office Postcode':  # vlaue str like numbers
#                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
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
    
    
    def category_match(self,key_word, input_dataframe):
        category_list = []
        # give score benchmark as 70 to cut down not useful data
        temp = process.extractBests(key_word, input_dataframe['UNSPSC Title'], limit=input_dataframe.shape[0],
                                    score_cutoff=70)
        for item in temp:
            category_list.append(item[2])
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
    
    
    # def value_match(range, input_dataframe):
    #     lower_bound = range['Low Bound']
    #     upper_bound = range['Upper Bound']
    #     target_value = input_dataframe[(input_dataframe['Value'] <= upper_bound) & (input_dataframe['Value'] >= lower_bound)]
    #     date_
    
    
    def find_match(self,keyword, input_frame):
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
                filtered_df = self.date_match(dateRange, filtered_df)
                # print("1", filtered_df.shape[0])
    
            elif key == "Supplier Name":
                # may have multiple words input in supplier
                # supplier1 OR supplier2 OR ...
                temp = pd.DataFrame()
                for words in value:
                    temp = pd.concat([temp, self.supplier_match(words, filtered_df)], join='outer')
                filtered_df = temp
                # print("2", filtered_df.shape[0])
    
            elif key == 'Category':
                temp = pd.DataFrame()
                # user may tick multiple categories
                for words in value:
#                    print("3", self.category_match(words, filtered_df).shape[0])
                    temp = pd.concat([temp, self.category_match(words, filtered_df)], join='outer')
                filtered_df = temp
                # print("5", filtered_df.shape[0])
    
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
    
        filtered_id = filtered_df.index.tolist()
        return filtered_id       


# ---------------------------main----------------------------------
if __name__ == '__main__':    
    import time
    start_time = time.time()
    
    from dash_trialV2 import Dashboard
    
    txtA = TextAnalysis()
    print("--- %s seconds ---set up TextAnalysis object" % (time.time() - start_time))
    proc = Pre_process()
    print("--- %s seconds ---set up Pre_process object" % (time.time() - start_time))
    proc.upload_file('All_data.csv')
    print("--- %s seconds ---upload_file" % (time.time() - start_time))
    df = proc.cleaned_Dataframe.sort_values(by='Value',ascending=False)    
    print("--- %s seconds ---cleaned_Dataframe" % (time.time() - start_time))
  
    keyword = txtA.unpack("test3.json")
#    keyword1 = txtA.unpack('test3.json')
    print("--- %s seconds ---unpack" % (time.time() - start_time))

    output = txtA.find_match(keyword, df)
#    output1 = txtA.find_match(keyword1,df)    
    
#    print("--- %s seconds ---find_match" % (time.time() - start_time))
#    output_json = {"Contract ID": output, "UI Command": keyword}
    print("--- %s seconds ---find_match" % (time.time() - start_time))

    dash = Dashboard()
    filtered_rows = output
    df_filtered_rows = df.loc[filtered_rows,:]
    
#    filtered_rows1 = output1
#    df_filtered_rows1 = df.loc[filtered_rows1,:]
    
    list_category = keyword['Category']
#    list_category1 = keyword1['Category']
    
    dash.df = proc.cleaned_Dataframe
    url = dash.pie_plot(dataframe=df_filtered_rows,category=list_category)
#    url1 = dash.pie_plot(dataframe=df_filtered_rows1,category=list_category1)    

    print("--- %s seconds --- output dash url" % (time.time() - start_time))
    wb.open(url)