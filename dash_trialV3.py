# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:29:45 2018

@author: Nan
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import plotly
import json
from fuzzywuzzy import process
import math

#c = Client()
#c.upload_file("/Users/NAN/Desktop/Qt Project/All_data.csv")
#df = c.cleaned_Dataframe.head(100)

class Dashboard:
    df = pd.DataFrame() # save original df for comparison
    
    # read json
    def get_json(self,json_file):
#        c = Client()
#        c.upload_file('All_data.csv')
#        df = c.cleaned_Dataframe
#        df = df.set_index('Contract ID')
#        with open(json_file) as json_data:
        j = json.load(json_file)
        filtered_rows = list(j['Contract ID']) # list of contract IDs
        df_filtered_rows = self.df.loc[filtered_rows,:] # extract filtered rows
        list_category = j['UI Command']['Category'] # extact a list of categories
        return df_filtered_rows,list_category
        
    # df should be filtered dataframe, keyvalue=x should be groupby by one key features
    # the category should be 
    # ********************************** df should be cleansed original df that read locally in srcipt ******************
    def pie_plot(self,dataframe,x='',category=[]):
        url = ''
        if bool(category): # if the dictionary is not empty
            index_by_cat = {}
            for ele in category:
                list_contract = process.extractBests(ele,dataframe['UNSPSC Title'],
                                                     limit=dataframe.shape[0],
                                                     score_cutoff=70)
                index_by_cat[ele] = []
                for each in list_contract:
                    index_by_cat[ele].append(each[2])
            value_by_cat = {}
            total_value = self.df['Value'].sum()  # df is cleand original dataframe
            rest_value = total_value # define the total value beside the categorised rows
            for each in list(index_by_cat.keys()):
                value_by_cat[each] = (self.df.loc[index_by_cat[each],:])['Value'].sum()                       
            values = []
            for each in list(value_by_cat.keys()):
                values.append(value_by_cat[each])
                rest_value = rest_value - value_by_cat[each]
            values.append(rest_value)
            labels = []
            for each in list(value_by_cat.keys()):
                labels.append(each)
            labels.append('Rest')
            
            trace = go.Pie(labels = labels, values=values,hoverinfo='label+value',
                           textinfo='percent')
            data = [trace]
            url = plotly.offline.plot(data,filename='Pie-plots-by-category.html',
                                      auto_open=False)
          
            #create sublabel for each category
          
        elif (not category) & (len(x)>0): # if the dict is empty 
            # gives the unique value of the column
            values = dataframe.groupby(x)['Value'].sum().sort_values(ascending=False)
            values_most_20 = values[:20] # extract 20 most valued contract from all 
            values_rest = pd.Series([values[20:].sum()])
            values = pd.concat([values_most_20,values_rest])
            labels = list(values.index)[:20] + ['Rest']
            trace = go.Pie(labels=labels, values=values,hoverinfo='label+percent',
                           textinfo='value')
            data = [trace]
            url = plotly.offline.plot(data,filename='Pie-plots-by-keyword.html',auto_open=False)
        return url
    
    # bar chart
#    def bar_plot(self,dataframe,category):
#        
#        process.extractBests('my_cat',data[], limit = data[].shape[0], score_cutoff = 70)
#        trace = go.Bar(
#                )
#    
    def table_plot(self,dataframe):
#        lts_header = list(dataframe) # retrive header of the df                    
        df = dataframe.drop(['Amendment Date','Agency Ref ID','ATM ID', 'SON ID',
                             'Consultancy Reason', 'Amendment Reason','Supplier Address', 'Supplier Suburb',
                             'Supplier Postcode', 'Supplier Country', 'Supplier ABN Exempt','Branch', 'Division',
                             'Office Postcode'],axis=1)
        df = df.sort_values(by='Value',ascending=False)

        lts_head = list(df)
        data_table = []
        for each in lts_head:
            data_table.append(df[each])
        
        trace = go.Table(type='table',header=dict(values=lts_head,line = dict(color = '#506784'),
                            fill = dict(color = 'grey'),align = ['left','center'],font = dict(color = 'white', size = 12)),
                            cells=dict(values=data_table,align = ['left', 'center'],font = dict(color = '#506784', size = 11)))
        data = [trace]
        url = plotly.offline.plot(data,filename='Table.html',auto_open=False)  
        return url
    
    # present the weight of panel Arragnement
    def scatter_plot(self,keyword,dataframe):
        df_panel_filtered = dataframe[dataframe['Panel Arrangement']=='Yes']
        if keyword == 'Agency Name':
            df_panel_by_keyword = df_panel_filtered.groupby(keyword)['Panel Arrangement'].count()
            df_value_by_keyword = df_panel_filtered.groupby(keyword)['Value'].sum()
        elif keyword == 'Supplier ABN':
            df_panel_by_keyword = df_panel_filtered.groupby(keyword)['Panel Arrangement'].count()
            df_value_by_keyword = df_panel_filtered.groupby(keyword)['Value'].sum()
        elif keyword == 'UNSPSC Title':
            df_panel_by_keyword = df_panel_filtered.groupby(keyword)['Panel Arrangement'].count()
            df_value_by_keyword = df_panel_filtered.groupby(keyword)['Value'].sum()
        
        # df_panel_by_keword is a Series type, which only includes the count number 
        df_panel_by_keyword = df_panel_by_keyword.sort_values(ascending=False).head(20)
        # convert Series to Dataframe
        df_panel = pd.DataFrame({keyword:df_panel_by_keyword.index,'Counts':df_panel_by_keyword.values})
        # get the list of top 20 counts [keyword]
        lts_keyword = list(df_panel[keyword])
        # filter the original dataframe via list of rows
        df_value_by_keyword = pd.DataFrame({keyword:df_value_by_keyword.index,'Value':df_value_by_keyword.values})
        df_value_by_keyword = df_value_by_keyword.sort_values(ascending=False,by='Value')
        df_value_by_keyword = df_value_by_keyword[df_value_by_keyword[keyword].isin(lts_keyword)]
        df_value_by_keyword.reset_index(drop=True, inplace=True)
        
        slope = 2.666051223553066e-05
        hover_text = []
        bubble_size = []
        
        # merge above Series into one dataframe
        df_new = pd.merge(df_panel,df_value_by_keyword,on=keyword)
#        print(df_new.shape)
      
        
        '''
        Add new rows to the df_new, which include corresponding Supplier, countries, flags and start dates
        '''
        lts_supplier = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Supplier Name'].head(1)
            lts_supplier.append(temp.tolist()[0])
        df_new['Supplier Name'] = pd.Series(lts_supplier,index=df_new.index)
        
        lts_country = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Supplier Country'].head(1)
            lts_country.append(temp.tolist()[0])
        df_new['Supplier Country'] = pd.Series(lts_country,index=df_new.index)
        
        lts_COF = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Confidentiality Outputs Flag'].head(1)
            lts_COF.append(temp.tolist()[0])
        df_new['Confidentiality Outputs Flag'] = pd.Series(lts_COF,index=df_new.index)
        
        lts_CCF = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Confidentiality Contract Flag'].head(1)
            lts_CCF.append(temp.tolist()[0])
        df_new['Confidentiality Contract Flag'] = pd.Series(lts_CCF,index=df_new.index)
        
        lts_date = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Start Date'].head(1)
            lts_date.append(temp.tolist()[0])
        df_new['Start Date'] = pd.Series(lts_date,index=df_new.index)
        
#        print('updated df_new: ',df_new.shape)
        
        for index,row in df_new.iterrows():
            hover_text.append(('Total number of Panel Arrangment:{count}<br>'+
                               'Supplier Country: {country}<br>'+'Confidentiality Contract: {CCF}<br>'
                               +'Confidentiality Outputs:{COF}<br>'+'Start Year:{sYear}<br>'+
                               'Supplier Name:{supplier}<br>').format(count=row['Counts'],
                                       country=row['Supplier Country'],CCF=row['Confidentiality Contract Flag'],
                                       COF=row['Confidentiality Outputs Flag'],
                                       sYear=row['Start Date'],supplier=row['Supplier Name']))
            bubble_size.append(math.sqrt(row['Value']*slope))
            
        
            
        df_new['text'] = hover_text
        df_new['size'] = bubble_size
        sizeref = 2.*max(df_new['size'])/(100**2)
        
        # create an empty dict to store trace
        trace = {}
        
        # filter of rows must base on the keyword
        for index in range(df_new.shape[0]):
            trace[index] = go.Scatter(
                    x = df_new['Value'][df_new[keyword]==df_new.loc[index,keyword]],
                    y = df_new['Counts'][df_new[keyword]==df_new.loc[index,keyword]],
                    mode = 'markers',
                    name = df_new.loc[index,keyword],
                    text = df_new['text'][df_new[keyword]==df_new.loc[index,keyword]],
                    marker=dict(
                        symbol='circle',
                        sizemode='area',
                        sizeref=sizeref,
                        size=df_new['size'][df_new[keyword]==df_new.loc[index,keyword]],
                        line=dict(width=2)
                    )
            )
        
        data = []
        for key,value in trace.items():
            data.append(value)
        
        layout = go.Layout(
            title='Panel Arranged Contract',
            xaxis=dict(
                title='Total value by '+keyword,
                gridcolor='rgb(255, 255, 255)',
#                range=[2.003297660701705, 5.191505530708712],
                type='log',
                zerolinewidth=1,
                ticklen=5,
                gridwidth=2,
            ),
            yaxis=dict(
                title='Total number of Panel Arrangement by '+keyword,
                gridcolor='rgb(255, 255, 255)',
#                range=[36.12621671352166, 91.72921793264332],
                zerolinewidth=1,
                ticklen=5,
                gridwidth=2,
            ),
            paper_bgcolor='rgb(243, 243, 243)',
            plot_bgcolor='rgb(243, 243, 243)',
        )
        
        fig = go.Figure(data=data, layout=layout)
        url = plotly.offline.plot(fig, filename='Bubble.html',auto_open=False)
        
        return url
        # https://plot.ly/python/bubble-charts/
        
        
        