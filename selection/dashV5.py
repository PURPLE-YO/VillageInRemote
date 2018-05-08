# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:29:45 2018
@author: Nan
"""
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pandas as pd
import plotly
import math
from functools import reduce
from plotly import tools

class Dashboard:    
    # need a func to select rows that corresponding to the each category in a filtered
    # dataframe (e.g. the whole dataset is limited by a certain date range)
    '''
    @searching_dict: must have a key = "Category" and value = [list of str of categories]
    @filtered_df: df that after the process by Textanalysis
    @whold_dict: a corpus which is dict of sets (backendV4.TextAnalysis.index_dict)
    '''
    def select_rows(self, filtered_df, corpus, searching_dict):
        # if categories have been defined by the user, extract all searching keywords
        # and store into a list
        dict_filtered_df = {}
        dict_filtered_index = {}
        lts_lts_index = []
                        
        if bool(searching_dict['Category']):
            for each in searching_dict['Category']:
                if len(each.split(' ')) > 1:
                    for ele in each.split(' '):
                        lts_lts_index.append(list(corpus.get(ele)))
                    dict_filtered_index[each] = list(reduce(set.intersection, [set(item) for item in lts_lts_index]))
                else:
                    dict_filtered_index[each] = list(corpus.get(each))
        
        for key,value in dict_filtered_index.items():
            dict_filtered_index[key] = list(set(value).intersection(set(filtered_df.index.tolist())))
        
        for key,value in dict_filtered_index.items():
            dict_filtered_df[key] = filtered_df.loc[value]
            # Passing list-likes to .loc or [] with any missing label will raise
            # KeyError in the future, you can use .reindex() as an alternative.
        '''
        @returned structure
        {'research':Dataframe, 'risk analysis':Dataframe, 'statistics':Dataframe}
        @Dataframe
        use whole_dict and filtered list of index to re-define the df with corresponding
        categories
        '''
        return dict_filtered_df
        
    '''
    @dict_filtered_df: from above df
    @original_df: cleanded integrated df
    '''
    def pie_plot_by_cat(self,dict_filtered_df,original_df):
        total_value = original_df.Value.sum() # calculate the total value of all tenders
        tot_value_cat = [] # compute the total values corresponding to the categories
        label_cat = [] # extract label of each category
        
        for key,value in dict_filtered_df.items():
            tot_value_cat.append(value.Value.sum())
            label_cat.append(key)
        
        tot_value_cat.append(total_value-sum(tot_value_cat)) # add sum of rest rows 
        label_cat.append('Rest')
        
        value_in_cat_agency = []
        agency_in_cat = [] # keep agency names in the list
        agency_cat = [] # agency's corresponding category
        
        for key,value in dict_filtered_df.items():
            top_row = value.sort_values(by='Value',ascending=False).head(3)
            value_in_cat_agency.append(top_row.iloc[0]['Value'])
            agency_in_cat.append(top_row.iloc[0]['Agency Name'])
            agency_cat.append(key)
        
        fig = {
            "data" :[
                        {
                            "values" : tot_value_cat,
                            "labels" : label_cat,
                            "text" : "Category",
                            "textposition":"inside",
                            "domain": {"x": [0, .48]},
                            "name": "Funding by categories",
                            "hoverinfo":"label+value+name",
                            "hole": .7,
                            "type": "pie"                        
                        },
                        {
                            "values" : value_in_cat_agency,
                            "labels" : [a+' in '+'"'+b+'"' for a,b in zip(agency_in_cat,agency_cat)],
                            "text":"Agency",
                            "textposition":"inside",
                            "domain": {"x": [.52, 1]},     
                            "name": "Top Agency",
                            "hoverinfo":"label+value+name",
                            "hole": .7,
                            "type": "pie"
                        }
                     ],
            "layout" : {
                    "title":"Fundings by Categories and the Top Funding Agency in each Category",
                    "annotations": [
                            {
                                "font": {
                                    "size": 20
                                },
                                "showarrow": False,
                                "text": "Funding by categories",
                                "x": 0.11,
                                "y": 0.5
                            },
                            {
                                "font": {
                                    "size": 20
                                },
                                "showarrow": False,
                                "text": "Top Agency",
                                "x": 0.8,
                                "y": 0.5
                            }
                        ]
                    }
        }
        
        url = plotly.offline.plot(fig,filename='Pie-plots-by-cat.html',auto_open=False)
        return url
    
    # similar to pie_plot_by_cat, if no categories have been given
    def pie_plot_by_key(self,filtered_df,searching_dict,top=20):
        # 'Keyword' from searching_dict is given by UI, which defines the basement value, namely, 
        # the way or direction to looking the dataset
        keyword = searching_dict['Keywords']
        if keyword == 'Agency Name':
            df_pie = filtered_df.groupby(keyword)['Value'].sum().head(top)
            df_pie = df_pie.sort_values(ascending=False)
        elif keyword == 'UNSPSC Title':
            df_pie = filtered_df.groupby(keyword)['Value'].sum().head(top)
            df_pie = df_pie.sort_values(ascending=False)
        elif keyword == 'Supplier Name':
            df_pie = filtered_df.groupby(keyword)['Value'].sum().head(top)
            df_pie = df_pie.sort_values(ascending=False)
        
        value_by_key = list(df_pie)
        label_by_key = df_pie.index.tolist()
            
        fig = {
            "data" : [
                {
                    'values'  : value_by_key,
                    'labels' : label_by_key,
                    "text" : keyword,
                    "textposition":"inside",
                    "name": "Funding by "+keyword,
                    "hoverinfo":"label+value+name",
                    "hole": .7,
                    "type": "pie" 
                }
            ],
            "layout" : {
                    "title":"Top "+str(top)+" Fundings by "+keyword,
                    "annotations" : [
                                        {
                                            "font": {
                                                "size": 20
                                            },
                                            "showarrow": False,
                                            "text": keyword,
                                            "x": 0.5
                                        }
                                    ]
                        }
        }
        
        url = plotly.offline.plot(fig,filename='Pie-plots-by-key.html',auto_open=False)
        return url
        
    # bar chart
    # CF : 'Consultancy Flag'
    # COF: 'Confidentiality Outputs Flag' 
    # CCF: 'Confidentiality Contract Flag'
    # select one among Procument,CF,COF,CCF 
    def hbar_by_cat(self,dict_filtered_df,Procurement='None',CF='None',COF='None',CCF='None'):
        x_value_by_cat = []
        x_label_by_cat = []
        for key,value in dict_filtered_df.items():
            x_label_by_cat.append(key)
            x_value_by_cat.append(value.Value.sum())
        
        x_flag_by_cat = [] # count of the flags corresponding to categories
        x_label_by_flag = []
        if Procurement != 'None':
            for key,value in dict_filtered_df.items():
                x_label_by_flag.append(key+' with label Procurement Method: '+Procurement)
                x_flag_by_cat.append(value.loc[value['Procurement Method']==Procurement,'Procurement Method'].count())
        elif CF != 'None':
            for key,value in dict_filtered_df.items():
                x_label_by_flag.append(key+' with label Consultancy Flag: '+CF)
                x_flag_by_cat.append(value.loc[value['Consultancy Flag']==CF,'Consultancy Flag'].count())
        elif COF != 'None':
            for key,value in dict_filtered_df.items():
                x_label_by_flag.append(key+' with label Confidentiality Outputs Flag: '+COF)
                x_flag_by_cat.append(value.loc[value['Confidentiality Outputs Flag']==COF,'Confidentiality Outputs Flag'].count())
        elif CCF != 'None':
            for key,value in dict_filtered_df.items():
                x_label_by_flag.append(key+' with label Confidentiality Contract Flag: '+CCF)
                x_flag_by_cat.append(value.loc[value['Confidentiality Contract Flag']==CCF,'Confidentiality Contract Flag'].count())    
        
        if Procurement != 'None':
            title_name = 'The number of Procurement Method in "'+Procurement+'" by category'
        elif CF != 'None': 
            title_name = 'The number of Consultancy Flag in "'+CF+'" by category'
        elif COF != 'None':
            title_name = 'The number of Confidentiality Outputs Flag in "'+COF+'" by category' 
        elif CCF != 'None':
            title_name = 'The number of Confidentiality Contract Flag in "'+CCF+'" by category' 
        
        trace0 = go.Bar(
                x = x_value_by_cat,
                y = x_label_by_cat,
                marker = dict(
                        color = 'rgba(50, 171, 96, 0.6)',
                        line = dict(
                                color='rgba(50, 171, 96, 1.0)',
                                width=1)
                        ),
                name = 'Total values by Category',
                orientation = 'h'
                )
        
        trace1 = go.Scatter(
                x = x_flag_by_cat,
                y = x_label_by_flag,
                mode ='lines+markers',
                marker = dict(
                        color='rgb(128, 0, 128)'
                        ),
                name = title_name,                   
                )
        
        layout = dict(
                title = 'Total Values by Category with '+title_name,
                    yaxis1=dict(
                        showgrid=False,
                        showline=False,
                        showticklabels=True,
                        domain=[0, 0.85],
                    ),
                    yaxis2=dict(
                        showgrid=False,
                        showline=True,
                        showticklabels=False,
                        linecolor='rgba(102, 102, 102, 0.8)',
                        linewidth=2,
                        domain=[0, 0.85],
                    ),
                    xaxis1=dict(
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                        showgrid=True,
                        domain=[0, 0.42],
                    ),
                    xaxis2=dict(
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                        showgrid=True,
                        domain=[0.47, 1],
                        side='top',
                    ),
                    legend=dict(
                        x=0.029,
                        y=1.038,
                        font=dict(
                            size=10,
                        ),
                    ),
                    margin=dict(
                        l=100,
                        r=20,
                        t=70,
                        b=70,
                    ),
                    paper_bgcolor='rgb(248, 248, 255)',
                    plot_bgcolor='rgb(248, 248, 255)'
                )
                    
        # Creating two subplots
        fig = tools.make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                                  shared_yaxes=False,vertical_spacing=0.001)
        
        fig.append_trace(trace0, 1, 1)
        fig.append_trace(trace1, 1, 2)
        
        fig['layout'].update(layout)
        url = plotly.offline.plot(fig, filename='h-bar-line.html',auto_open=False)
        return url
          
    # use keyword to find the situation of tenders
    def hbar_by_key(self,dataframe,keyword='Agency Name',top=20,Procurement='None',CF='None',COF='None',CCF='None'):
        # get a Series of total values that groupby keyword
        temp = dataframe.groupby(keyword)['Value'].sum().sort_values(ascending=False).head(top)
        x_value_by_key = list(temp)
        x_label_by_key = temp.index.tolist()
        title_name = ''
        
        count_value_by_key = []
        if Procurement != 'None':
            [count_value_by_key.append(dataframe.loc[dataframe[keyword]==x,'Procurement Method'].value_counts()[Procurement]) for x in x_label_by_key]
        elif CF != 'None':
            [count_value_by_key.append(dataframe.loc[dataframe[keyword]==x,'Consultancy Flag'].value_counts()[CF]) for x in x_label_by_key]
        elif COF != 'None':
            [count_value_by_key.append(dataframe.loc[dataframe[keyword]==x,'Confidentiality Outputs Flag'].value_counts()[COF]) for x in x_label_by_key]
        elif CCF != 'None':
            [count_value_by_key.append(dataframe.loc[dataframe[keyword]==x,'Confidentiality Contract Flag'].value_counts()[CCF]) for x in x_label_by_key]
        
        if Procurement != 'None':
            title_name = 'The number of Procurement Method in "'+Procurement+'"'
        elif CF != 'None': 
            title_name = 'The number of Consultancy Flag in "'+CF+'"'
        elif COF != 'None':
            title_name = 'The number of Confidentiality Outputs Flag in "'+COF+'"'
        elif CCF != 'None':
            title_name = 'The number of Confidentiality Contract Flag in "'+CCF+'"'
            
        trace0 = go.Bar(
                x = x_value_by_key,
                y = x_label_by_key,
                marker = dict(
                        color = 'rgba(50, 171, 96, 0.6)',
                        line = dict(
                                color='rgba(50, 171, 96, 1.0)',
                                width=1)
                        ),
                name = 'Total values by '+keyword,
                orientation = 'h'
                )
        
        trace1 = go.Scatter(
                x = count_value_by_key,
                y = x_label_by_key,
                mode ='lines+markers',
                marker = dict(
                        color='rgb(128, 0, 128)'
                        ),
                name = title_name,                   
                )
        
        layout = dict(
                title = 'Total Values of top '+str(top)+' by '+keyword+' with '+title_name,
                    yaxis1=dict(
                        showgrid=False,
                        showline=True,
                        showticklabels=True,
                        domain=[0, 0.85],
                    ),
                    yaxis2=dict(
                        showgrid=False,
                        showline=True,
                        showticklabels=True,
                        linecolor='rgba(102, 102, 102, 0.8)',
                        linewidth=2,
                        domain=[0, 0.85],
                    ),
                    xaxis1=dict(
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                        showgrid=True,
                        domain=[0, 0.42],
                    ),
                    xaxis2=dict(
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                        showgrid=True,
                        domain=[0.47, 1],
                        side='top',
                    ),
                    legend=dict(
                        x=0.029,
                        y=1.038,
                        font=dict(
                            size=10,
                        ),
                    ),
                    margin=dict(
                        l=100,
                        r=20,
                        t=70,
                        b=70,
                    ),
                    paper_bgcolor='rgb(248, 248, 255)',
                    plot_bgcolor='rgb(248, 248, 255)'
                )
                    
        # Creating two subplots
        fig = tools.make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                                  shared_yaxes=False,vertical_spacing=0.001)
        
        fig.append_trace(trace0, 1, 1)
        fig.append_trace(trace1, 1, 2)
        
        fig['layout'].update(layout)
        url = plotly.offline.plot(fig, filename='h-bar-line-key.html',auto_open=False)
        return url       
        
        
    def table_plot(self,dataframe,top=20):
        df = dataframe.drop([ 'Parent Contract ID', 'Contract ID',
       'Amendment Date', 
       'Agency Ref ID', 'UNSPSC Code', 'UNSPSC Title', 
       'ATM ID', 'SON ID', 'Panel Arrangement',
       'Confidentiality Contract Flag', 'Confidentiality Contract Reason',
       'Confidentiality Outputs Flag', 'Confidentiality Outputs Reason',
       'Consultancy Flag', 'Consultancy Reason', 'Amendment Reason',
        'Supplier Address', 'Supplier Suburb',
       'Supplier Postcode', 'Supplier Country', 'Supplier ABN Exempt',
       'Contact Name', 'Contact Phone', 'Branch', 'Division',
       'Office Postcode'],axis=1)
        df = df.sort_values(by='Value',ascending=False).head(top)

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
    def scatter_plot(self,keyword,dataframe,display=20,asc=False):
        df_panel_filtered = dataframe[dataframe['Panel Arrangement']=='Yes']
        df_panel_by_keyword = pd.Series()
        df_value_by_keyword = pd.Series()
        if keyword == 'Agency Name':
            df_panel_by_keyword = df_panel_filtered.groupby(keyword)['Panel Arrangement'].count()
            df_value_by_keyword = df_panel_filtered.groupby(keyword)['Value'].sum()
        # since one supplier Name corresponding multiple ABN,then use ABN as base value to generate data
        elif keyword == 'Supplier ABN': 
            df_panel_by_keyword = df_panel_filtered.groupby(keyword)['Panel Arrangement'].count()
            df_value_by_keyword = df_panel_filtered.groupby(keyword)['Value'].sum()
        elif keyword == 'UNSPSC Title':
            df_panel_by_keyword = df_panel_filtered.groupby(keyword)['Panel Arrangement'].count()
            df_value_by_keyword = df_panel_filtered.groupby(keyword)['Value'].sum()
        
        # df_panel_by_keword is a Series type, which only includes the count number 
        df_panel_by_keyword = df_panel_by_keyword.sort_values(ascending=asc).head(display)
        # convert Series to Dataframe
        df_panel = pd.DataFrame({keyword:df_panel_by_keyword.index,'Counts':df_panel_by_keyword.values})
        # get the list of top [display] counts [keyword]
        lts_keyword = list(df_panel[keyword])
        # filter the original dataframe via list of rows
        df_value_by_keyword = pd.DataFrame({keyword:df_value_by_keyword.index,'Value':df_value_by_keyword.values})
        df_value_by_keyword = df_value_by_keyword.sort_values(ascending=asc,by='Value')
        df_value_by_keyword = df_value_by_keyword[df_value_by_keyword[keyword].isin(lts_keyword)]
        df_value_by_keyword.reset_index(drop=True, inplace=True)
        
        slope = 2.666051223553066e-05
        hover_text = []
        bubble_size = []
        
        # merge above Series into one dataframe
        df_new = pd.merge(df_panel,df_value_by_keyword,on=keyword)              
        '''
        Add new rows to the df_new, which include corresponding Supplier, countries, flags and start dates
        '''        
        lts_country = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Supplier Country']
            temp_count = temp.value_counts()
            lts_country.append(temp_count.sort_values(ascending=False)[:3])
        df_new['Supplier Country'] = pd.Series(lts_country,index=df_new.index)
        
        lts_COF = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Confidentiality Outputs Flag']
            temp_count = temp.value_counts()
            lts_COF.append(temp_count)
        df_new['Confidentiality Outputs Flag'] = pd.Series(lts_COF,index=df_new.index)
        
        lts_CCF = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Confidentiality Contract Flag']
            temp_count = temp.value_counts()
            lts_CCF.append(temp_count)
        df_new['Confidentiality Contract Flag'] = pd.Series(lts_CCF,index=df_new.index)

        lts_CF = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Consultancy Flag']
            temp_count = temp.value_counts()
            lts_CF.append(temp_count)
        df_new['Consultancy Flag'] = pd.Series(lts_CF,index=df_new.index)        

        lts_PM = []
        for each in df_new[keyword].tolist():
            temp = dataframe.loc[dataframe[keyword]==each,'Procurement Method']
            temp_count = temp.value_counts()
            lts_PM.append(temp_count)
        df_new['Procurement Method'] = pd.Series(lts_PM,index=df_new.index)     
        
        for index,row in df_new.iterrows():
            hover_text.append(('{key}<br>'+
                               '{procurement}<br>'+
                               '{country}<br>'+
                               '{CF}<br>'+
                               '{CCF}<br>'+
                               '{COF}<br>').format(
                                       key=row[keyword],
                                       procurement=row['Procurement Method'],
                                       country=row['Supplier Country'],
                                       CF=row['Consultancy Flag'],                             
                                       CCF=row['Confidentiality Contract Flag'],
                                       COF=row['Confidentiality Outputs Flag']                                                                         
                                       ))
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
            title='Top '+str(display)+' Panel Arranged Contract by values',
            xaxis=dict(
                title='Total value by '+keyword,
                gridcolor='rgb(255, 255, 255)',
                type='log',
                zerolinewidth=1,
                ticklen=5,
                gridwidth=2,
            ),
            yaxis=dict(
                title='Total number of Panel Arrangement by '+keyword,
                gridcolor='rgb(255, 255, 255)',
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
    
    '''
    @dict_filtered_df: if the comparing by 2 categories
    @com_key: a dict of comparing list, its format should be {"Category/
              Agency Name/Supplier Name/UNSPSC Title" : ["Compare_1","Compare_2"]}
    @dataframe: selected rows from original df
    @panel: the flag of 'Panel Arrangement'
    @proc: type of the tender [Procurement Method] , which is used to count the number of related tenders
    '''    
    def compare_entity(self,dataframe,com_key,dict_filtered_df={},panel=False,CCF=False,COF=False,CF=False,proc=False):
        table_title_a = ['Entity']
        table_title_b = ['Entity']
        table_data_a = []
        table_data_b = []
        entity = []
        values_a = 0
        values_b = 0
        
        aggregation={
         "Value":
                {
                    "MIN": lambda x: x.min(skipna=True),
                    "MAX":lambda x: x.max(skipna=True),
                    "MEDIAN":lambda x: x.median(skipna=True),
                    "MEAN":lambda x:x.mean(skipna=True)
                }
        }
        
        if bool(dict_filtered_df):
            print()
        else:
            comp_key = list(com_key.keys())[0]
            comp_entity = list(com_key.values())[0]
            entity = entity + comp_entity
            df_summary = dataframe.groupby(comp_key).agg(aggregation)
            '''
            @df_summary:
                head: index[by keywords];('Value','MIN');('Value','MAX');('Value','MEDIAN');('Value','MEAN')
            '''
            if comp_key != 'Compare':
                df_a = dataframe.loc[dataframe[comp_key] == comp_entity[0]]
                df_b = dataframe.loc[dataframe[comp_key] == comp_entity[1]]
                values_a = df_a.Value.sum()
                values_b = df_b.Value.sum()
                
                table_data_a.append(comp_entity[0])
                table_data_b.append(comp_entity[1])                

                if panel == True:
                    table_title_a = table_title_a + ['Panel Arr: '+x for x in df_a['Panel Arrangement'].value_counts().index.tolist()]
                    table_title_b = table_title_b + ['Panel Arr: '+x for x in df_b['Panel Arrangement'].value_counts().index.tolist()]
                    table_data_a = table_data_a + list(df_a['Panel Arrangement'].value_counts())
                    table_data_b = table_data_b + list(df_b['Panel Arrangement'].value_counts())

                elif CCF == True:
                    table_title_a = table_title_a + (['CCF: '+x for x in df_a['Confidentiality Contract Flag'].value_counts().index.tolist()])
                    table_title_b = table_title_b + (['CCF: '+x for x in df_b['Confidentiality Contract Flag'].value_counts().index.tolist()])                
                    table_data_a = table_data_a + list(df_a['Confidentiality Contract Flag'].value_counts())
                    table_data_b = table_data_b + list(df_b['Confidentiality Contract Flag'].value_counts())

                elif COF == True:
                    table_title_a = table_title_a + ['COF: '+x for x in df_a['Confidentiality Outputs Flag'].value_counts().index.tolist()]
                    table_title_b = table_title_b + ['COF: '+x for x in df_b['Confidentiality Outputs Flag'].value_counts().index.tolist()]
                    table_data_a = table_data_a + list(df_a['Confidentiality Outputs Flag'].value_counts())
                    table_data_b = table_data_b + list(df_b['Confidentiality Outputs Flag'].value_counts())

                elif CF == True:               
                    table_title_a = table_title_a + ['CF: '+x for x in df_a['Consultancy Flag'].value_counts().index.tolist()]
                    table_title_b = table_title_b + ['CF: '+x for x in df_b['Consultancy Flag'].value_counts().index.tolist()]              
                    table_data_a = table_data_a + list(df_a['Consultancy Flag'].value_counts())
                    table_data_b = table_data_b + list(df_b['Consultancy Flag'].value_counts())

                elif proc == True:
                    table_title_a = table_title_a + ['Procurement: '+x for x in df_a['Procurement Method'].value_counts().index.tolist()]
                    table_title_b = table_title_b + ['Procurement: '+x for x in df_b['Procurement Method'].value_counts().index.tolist()]              
                    table_data_a = table_data_a + list(df_a['Procurement Method'].value_counts())
                    table_data_b = table_data_b + list(df_b['Procurement Method'].value_counts())
    
                table_title_a.append('Num of Parent')
                table_title_b.append('Num of Parent')                
                table_data_a.append(df_a.loc[df_a['Parent Contract ID']!='N/A','Parent Contract ID'].count())
                table_data_b.append(df_b.loc[df_b['Parent Contract ID']!='N/A','Parent Contract ID'].count())
                
                table_title_a = table_title_a + df_summary.columns.get_level_values(1).tolist()
                table_data_a = table_data_a + df_summary.loc[entity[0]].tolist()
                table_data_b = table_data_b + df_summary.loc[entity[1]].tolist()
        
        table_data = []
        table_data.append(table_title_a)
        table_data.append(table_data_a)
        table_data.append(table_data_b)

        figure = ff.create_table(table_data, height_constant=60)        
        # add bar comparison
        trace1 = go.Bar(x=[values_a],  xaxis='x2', yaxis='y2',
                        marker=dict(color='#0099ff'),
                        name=entity[0],
                        orientation = 'h',
                        )
        trace2 = go.Bar(x=[values_b], xaxis='x2', yaxis='y2',
                        marker=dict(color='#404040'),
                        name=entity[1],
                        orientation = 'h')
        
        # Add trace data to figure
        figure['data'].extend(go.Data([trace1, trace2]))
        
        # Edit layout for subplots
        figure.layout.yaxis.update({'domain': [0, .55]})
        figure.layout.yaxis2.update({'domain': [.7, 1]})
        figure.layout.yaxis2.update({'anchor': 'x2'})
        figure.layout.xaxis2.update({'anchor': 'y2'})
        figure.layout.yaxis2.update({'title': 'Total Value'})
        # Update the margins to add a title and see graph x-labels. 
        figure.layout.margin.update({'t':75, 'l':50})
        figure.layout.update({'title': 'Comparison between "'+entity[0]+'" and "'+entity[1]+'"'})
        # Update the height because adding a graph vertically will interact with
        # the plot height calculated for the table
        figure.layout.update({'height':800})

        url = plotly.offline.plot(figure,filename='comp-table.html',auto_open=False)
        return url                