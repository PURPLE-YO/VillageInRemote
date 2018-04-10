# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 19:20:26 2018

@author: Nan
"""

import pandas as pd 
import matplotlib.pyplot as plt

class Client:
       
    upload_Dataframe = pd.DataFrame()
    cleaned_Dataframe = pd.DataFrame()
    listOfFields = []
    listOfSelection = []
    filename = ''
    pointer='wait'
    output = ''
    
    # communication module which acquires input orders
    def comm_module(self):
        self.output = 'Welcome to the Tender database visualisation system!'
           
            # actually use the local file to make DA
         
    # comm_pointer
    def comm_pointer(self,index=0):
        if index == 1:
            self.pointer = 'Quit'
        elif index == 2:
            self.pointer = 'upload file'
        elif index == 3:
            self.pointer = 'fields selection'
        elif index == 0:
            self.pointer = 'wait'


    
    # Upload function
    def upload_file(self,upload_file):
        while True:
            try:              
                self.upload_Dataframe = pd.read_csv(upload_file,low_memory=False)
                self.listOfFields = list(self.upload_Dataframe)
                self.data_cleansing()
                self.output = 'Pass'
                break
            except FileNotFoundError:
                self.output = "File Not Found!"
            except SyntaxError:
                self.output = "SyntaxError, file path should be C:/Users/data.csv"

    # data cleansing -- handling missing value
    def data_cleansing(self):
        df = self.upload_Dataframe
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
                if features == 'Parent Contract ID':
                    df.loc[:, features] = df.loc[:, features].fillna('None')
                elif features == 'Amendment Date':
                    df.loc[:, features] = df.loc[:, features].fillna('Not Amended')
                elif features == 'Description':
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Agency Ref ID':
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'UNSPSC Title':
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
                #                        print(df.loc[list_of_nan[index],[features,'UNSPSC Code']])
                elif features == 'ATM ID':
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'SON ID':
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Panel Arrangement':  # value str [Yes/No]
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Confidentiality Contract Flag':  # value str [No]
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Confidentiality Contract Reason':  # value str
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Confidentiality Outputs Flag':  # value str [No]
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Confidentiality Outputs Reason':  # value str
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Consultancy Flag':  # value str [Yes/No]
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Consultancy Reason':  # value str [ex:Skills currently unavailable within agency]
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Amendment Reason':  # value str [ex:Contract value increased from $932,144.50]
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Supplier Address':  # value str
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Supplier Suburb':  # value str
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Supplier Postcode':  # value str like numbers
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Supplier ABN':  # value float [79097795125.0]
                    df.loc[:, features] = df.loc[:, features].fillna(float(0))  # use 0.0 replace Nan in this field
                elif features == 'Contact Phone':  # value str like num
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Branch':  # value str
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Division':  # value str
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
                elif features == 'Office Postcode':  # vlaue str like numbers
                    df.loc[:, features] = df.loc[:, features].fillna('N/A')
            self.cleaned_Dataframe = df

    def fields_selection(self,questions=0):

        # based on the question, distribute corresponding index to each question
        if questions == 0:
            self.listOfSelection = ['Agency Name']
        elif questions == 1:  # How much funding is available in the target categories? (Total, by category, over time)
            self.listOfSelection = ['Value', 'UNSPSC Title']
        elif questions == 2:  # question 2
            self.listOfSelection = []
        else:
            self.listOfSelection = []


    # Return the list of agency name with target category
    # def category_agency(self, category_name):
    #     listAgency = self.catByAgency.get(category_name)
    #     return listAgency

    # **********************************************************************

if __name__ == '__main__':
    c = Client()
    from Server import Server
    s = Server()
    c.upload_file("/Users/NAN/Desktop/Qt Project/All_data.csv")
    # question 1
    df = s.visual_q2(c.cleaned_Dataframe) # total included in rows which records sum value of a category
    df_sum = df[df['Agency Name']=='Total']    
    df_sum['Value'].plot(kind='barh')


