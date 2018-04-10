import pandas as pd
import numpy as np

class Server:
    # doc stored in the server for basic structure
    updated_data = pd.DataFrame()
    base = pd.read_csv('/Users/NAN/Desktop/Qt Project/Comm.csv', low_memory=False)
    base["Filter UNSPSC of Interest"] = base["Filter UNSPSC of Interest"].astype("category")
    base["Filter UNSPSC of Interest"].cat.set_categories(["Rest of Categories", "Categories of Interest"], inplace=True)

    temp = base[['UNSPSC Title', 'Filter UNSPSC of Interest']]
    grouped = temp.groupby(by=['UNSPSC Title'])

    # dataframe used to match category of interest
    # for those files missing with 'Filter UNSPSC of Interest'
    match_df = grouped.last()

    catByAgency = {
        'comprehensive health services': ["Attorney-General's Department",
                                          'Australian Customs and Border Protection Service',
                                          'Australian Electoral Commission', 'Australian Federal Police',
                                          'Australian Prudential Regulation Authority (APRA)',
                                          'Australian Sports Anti-Doping Authority (ASADA)',
                                          'Australian Taxation Office', 'Cancer Australia', 'Comsuper', 'CRS Australia',
                                          'CSIRO', 'Defence Materiel Organisation',
                                          'Department of Agriculture and Water Resources', 'Department of Defence',
                                          'Department of Finance',
                                          'Department of Foreign Affairs and Trade - Australian Aid Program',
                                          'Department of Health', 'Department of Human Services',
                                          'Department of Immigration and Border Protection',
                                          'Department of Infrastructure and Regional Development',
                                          'Department of Infrastructure and Transport',
                                          'Department of Parliamentary Services',
                                          'Department of Regional Australia, Local Government, Arts and Sport',
                                          'Department of the Treasury', "Department of Veterans' Affairs",
                                          'National Blood Authority', 'National Water Commission',
                                          'Office of the Fair Work Building Industry Inspectorate',
                                          'Professional Services Review', 'Royal Australian Mint'],
        'community and social services': ['Department of Social Services',
                                          'Department of Immigration and Border Protection',
                                          'Department of Foreign Affairs and Trade - Australian Aid Program',
                                          'Department of Education Employment and Workplace Relations',
                                          'Department of the Prime Minister and Cabinet',
                                          'Department of Human Services', 'Department of Defence',
                                          "Department of Veterans' Affairs",
                                          'Department of Regional Australia, Local Government, Arts and Sport',
                                          'Department of Communications and the Arts', "Attorney-General's Department",
                                          'Department of Infrastructure and Regional Development',
                                          'Department of Education and Training', 'Department of Employment',
                                          'Australian Human Rights Commission', 'Department of Health',
                                          'Australian Communications and Media Authority (ACMA)',
                                          'Department of Families, Housing, Community Services and Indigenous Affairs',
                                          'Murray-Darling Basin Authority', 'Australian Electoral Commission',
                                          'Australian Federal Police', 'Office of the Fair Work Ombudsman',
                                          'Department of Agriculture and Water Resources'],
        'healthcare provider support persons': ['Department of Immigration and Border Protection',
                                                "Department of Veterans' Affairs", 'Department of Defence',
                                                'Australian Taxation Office',
                                                'Department of the Prime Minister and Cabinet',
                                                'Australian Federal Police', 'Department of Parliamentary Services',
                                                'Department of Infrastructure and Regional Development',
                                                'Australian Organ and Tissue Donation and Transplantation Authority',
                                                'Australian Communications and Media Authority (ACMA)',
                                                'Cancer Australia',
                                                'Australian Radiation Protection and Nuclear Safety Agency (ARPANSA)'],
        'health programs': ['Department of Health', 'Department of the Prime Minister and Cabinet',
                            "Department of Veterans' Affairs", 'Cancer Australia',
                            'National Health Performance Authority',
                            'Department of Foreign Affairs and Trade - Australian Aid Program',
                            'Department of Industry, Innovation and Science', 'Independent Hospital Pricing Authority',
                            'Department of Families, Housing, Community Services and Indigenous Affairs',
                            'Department of Agriculture and Water Resources', 'Department of Human Services',
                            'Department of Defence', 'Australian Bureau of Statistics',
                            'Australian Communications and Media Authority (ACMA)',
                            'Australian Radiation Protection and Nuclear Safety Agency (ARPANSA)',
                            'Department of Foreign Affairs and Trade',
                            'Department of Infrastructure and Regional Development', 'Department of the Environment',
                            'Australian National Preventive Health Agency', 'Defence Materiel Organisation',
                            'Old Parliament House',
                            'Department of Regional Australia, Local Government, Arts and Sport',
                            'Department of Parliamentary Services'],
        'research programs': ['Australian Centre for International Agricultural Research',
                              'Department of Social Services', 'Department of Education and Training',
                              'Department of Education Employment and Workplace Relations', 'Department of Defence',
                              'Australian Research Council', "Department of Veterans' Affairs",
                              'Australian Fisheries Management Authority',
                              'Department of Immigration and Border Protection', "Attorney-General's Department",
                              'Department of Employment', 'Australian Institute of Family Studies',
                              'Safe Work Australia', 'Great Barrier Reef Marine Park Authority',
                              'Defence Materiel Organisation', 'National Health and Medical Research Council',
                              'National Mental Health Commission', 'Department of Industry, Innovation and Science',
                              'Fair Work Commission', 'Department of the Environment',
                              'Department of Families, Housing, Community Services and Indigenous Affairs',
                              'Australian Institute of Criminology', 'Department of Foreign Affairs and Trade',
                              'Department of Climate Change and Energy Efficiency',
                              'Australian Securities and Investments Commission',
                              'Asbestos Safety and Eradication Agency', 'Bureau of Meteorology',
                              'Department of Human Services', 'Geoscience Australia',
                              'Department of Agriculture and Water Resources',
                              'Department of the Prime Minister and Cabinet', 'Australian Federal Police',
                              'Australian Taxation Office',
                              'Australian Organ and Tissue Donation and Transplantation Authority',
                              'Australian National Preventive Health Agency', 'Australian War Memorial',
                              'Australian Human Rights Commission', 'Australian Institute of Health and Welfare',
                              'Department of Resources Energy and Tourism', 'Office of the Fair Work Ombudsman',
                              'Old Parliament House', 'Australian Communications and Media Authority (ACMA)',
                              'Austrade', 'Workplace Gender Equality Agency', 'Department of Finance',
                              'Australian Bureau of Statistics', 'Australian Aged Care Quality Agency',
                              'Clean Energy Regulator', 'Digital Transformation Office',
                              'Office of Parliamentary Counsel', 'Productivity Commission',
                              'Department of Regional Australia, Local Government, Arts and Sport',
                              'Office of the Australian Information Commissioner',
                              'Australian Prudential Regulation Authority (APRA)',
                              'Office of the Australian Accounting Standards Board', 'National Capital Authority',
                              'Office of the Fair Work Building Industry Inspectorate', 'Inspector-General of Taxation',
                              'Australian Transaction Reports and Analysis Centre (AUSTRAC)',
                              'Department of Foreign Affairs and Trade - Australian Aid Program',
                              'Australian Electoral Commission', 'Murray-Darling Basin Authority', 'Cancer Australia'],
        'disease prevention and control': ['Department of Health',
                                           'Department of Foreign Affairs and Trade - Australian Aid Program',
                                           'Department of Agriculture and Water Resources',
                                           'Australian Centre for International Agricultural Research',
                                           'Defence Materiel Organisation', 'Department of Defence',
                                           'Department of Communications and the Arts',
                                           'Department of the Prime Minister and Cabinet',
                                           'Department of Parliamentary Services', "Attorney-General's Department",
                                           'Department of Education and Training',
                                           'Department of Regional Australia, Local Government, Arts and Sport'],
        'health administration services': ['Department of Defence', 'Australian Federal Police',
                                           'Department of Human Services', "Department of Veterans' Affairs",
                                           'Department of Foreign Affairs and Trade', 'Cancer Australia',
                                           "Attorney-General's Department", 'Department of Finance',
                                           'Department of Immigration and Border Protection', 'Department of Health',
                                           'Department of Industry, Innovation and Science',
                                           'Australian National Preventive Health Agency',
                                           'Defence Materiel Organisation', 'Professional Services Review',
                                           'Department of Foreign Affairs and Trade - Australian Aid Program',
                                           'Safe Work Australia', 'Department of Parliamentary Services',
                                           'Department of Resources Energy and Tourism',
                                           'National Health and Medical Research Council', 'Austrade',
                                           'Department of Social Services',
                                           'Australian Transaction Reports and Analysis Centre (AUSTRAC)',
                                           'Department of Agriculture and Water Resources'],
        'market research': ['Austrade', 'Department of Health', 'Department of Human Services',
                            'Australian Taxation Office', 'Department of Communications and the Arts',
                            'Department of Defence', 'Department of Industry, Innovation and Science',
                            'Department of Social Services', 'Department of Finance',
                            'Australian National Preventive Health Agency',
                            'Australian Securities and Investments Commission', 'Department of the Environment',
                            'Department of Families, Housing, Community Services and Indigenous Affairs',
                            'Australian Communications and Media Authority (ACMA)',
                            'Department of Immigration and Border Protection', 'Tourism Australia',
                            "Attorney-General's Department", 'Australian Institute of Health and Welfare',
                            'Australian Electoral Commission', 'Department of the Treasury',
                            'Independent Hospital Pricing Authority', 'Department of Foreign Affairs and Trade',
                            'Australian Centre for International Agricultural Research',
                            'Department of Resources Energy and Tourism', "Department of Veterans' Affairs",
                            'Department of Infrastructure and Regional Development', 'Digital Transformation Office',
                            'Australian Bureau of Statistics', 'Department of Agriculture and Water Resources',
                            'Department of Employment',
                            'Australian Organ and Tissue Donation and Transplantation Authority',
                            'Clean Energy Regulator', 'Australian Competition and Consumer Commission',
                            'Department of Climate Change and Energy Efficiency', 'Defence Materiel Organisation',
                            'Department of Education and Training', 'Australian Federal Police',
                            'Australian Public Service Commission',
                            'Department of Regional Australia, Local Government, Arts and Sport',
                            'Department of Infrastructure and Transport', 'Bureau of Meteorology',
                            'Department of Education Employment and Workplace Relations',
                            'Australian Human Rights Commission', 'Office of the Fair Work Ombudsman',
                            'Australian Financial Security Authority',
                            'Department of Health - Therapeutic Goods Administration', 'IP Australia',
                            'Cancer Australia', 'Great Barrier Reef Marine Park Authority',
                            'Australian Sports Anti-Doping Authority (ASADA)', 'Comsuper',
                            'Australian National Audit Office (ANAO)', 'Old Parliament House',
                            'Australian Pesticides and Veterinary Medicines Authority',
                            'Workplace Gender Equality Agency', 'Department of the Prime Minister and Cabinet',
                            'Australian Criminal Intelligence Commission', 'Director of National Parks',
                            'Geoscience Australia', 'Australian Skills Quality Authority',
                            'Department of Foreign Affairs and Trade - Australian Aid Program',
                            'Murray-Darling Basin Authority', 'National Mental Health Commission',
                            'Australian Radiation Protection and Nuclear Safety Agency (ARPANSA)',
                            'Department of Parliamentary Services', 'National Capital Authority',
                            'Telecommunications Universal Service Management Agency', 'Office of National Assessments',
                            'Australian Research Council', 'Safe Work Australia', 'Private Health Insurance Ombudsman',
                            'National Archives of Australia', 'Federal Court of Australia',
                            'Australian Transport Safety Bureau', 'Fair Work Commission',
                            'Office of the Fair Work Building Industry Inspectorate'],
        'military science and research': ['Department of Defence', 'Defence Materiel Organisation',
                                          "Department of Veterans' Affairs"],
        'safety or risk analysis': ['Department of Defence', 'Department of Agriculture and Water Resources',
                                    'Defence Materiel Organisation', 'Department of Health',
                                    'Department of the Environment', 'Department of Immigration and Border Protection',
                                    'Clean Energy Regulator', "Attorney-General's Department", 'Department of Finance',
                                    'Australian Competition and Consumer Commission',
                                    'Office of the Director of Public Prosecutions',
                                    'Department of Foreign Affairs and Trade',
                                    'Department of Industry, Innovation and Science',
                                    'Department of Families, Housing, Community Services and Indigenous Affairs',
                                    'Department of the Prime Minister and Cabinet',
                                    'Department of Infrastructure and Transport', 'Australian Federal Police',
                                    "Department of Veterans' Affairs",
                                    'Australian Customs and Border Protection Service',
                                    'Department of Infrastructure and Regional Development', 'Safe Work Australia',
                                    'Australian Securities and Investments Commission',
                                    'Australian Fisheries Management Authority', 'Department of Parliamentary Services',
                                    'Geoscience Australia', 'Department of Health - Therapeutic Goods Administration',
                                    'Department of Communications and the Arts',
                                    'Department of Education Employment and Workplace Relations',
                                    'Australian Radiation Protection and Nuclear Safety Agency (ARPANSA)',
                                    'Administrative Appeals Tribunal', 'Royal Australian Mint',
                                    'Office of the Fair Work Building Industry Inspectorate',
                                    'National Offshore Petroleum Safety and Environmental Management Authority',
                                    'Office of the Fair Work Ombudsman', 'Australian Bureau of Statistics', 'Austrade',
                                    'Office of the Official Secretary to the Governor-General',
                                    'Australian Institute of Family Studies'],
        'economics': ['Department of Infrastructure and Regional Development',
                      'Department of Infrastructure and Transport',
                      'Department of Foreign Affairs and Trade - Australian Aid Program', 'Department of the Treasury',
                      'Department of Defence', 'Department of Foreign Affairs and Trade',
                      'Department of Communications and the Arts',
                      'Department of Infrastructure Transport Regional Development and Local Government',
                      'Productivity Commission', 'Department of the Environment',
                      'Department of the Prime Minister and Cabinet', 'Department of Industry, Innovation and Science',
                      'Department of Immigration and Border Protection',
                      'Department of Agriculture and Water Resources'],
        'medical science research and experimentation': ["Department of Veterans' Affairs", 'Australian Federal Police',
                                                         'Department of Defence', 'Department of Health',
                                                         'Defence Materiel Organisation',
                                                         'Department of Social Services',
                                                         'Department of Health - Therapeutic Goods Administration',
                                                         'Australian Pesticides and Veterinary Medicines Authority',
                                                         'Department of Foreign Affairs and Trade - Australian Aid Program',
                                                         'Australian Sports Anti-Doping Authority (ASADA)',
                                                         'Australian Radiation Protection and Nuclear Safety Agency (ARPANSA)',
                                                         'Australian Securities and Investments Commission'],
        'economic analysis': ['Australian Office of Financial Management',
                              'Department of Climate Change and Energy Efficiency',
                              'Department of Industry, Innovation and Science', 'Department of Health',
                              'Department of Social Services', 'Climate Change Authority',
                              'Department of the Environment', 'Department of Foreign Affairs and Trade',
                              'Department of Communications and the Arts', "Attorney-General's Department",
                              'Department of Education Employment and Workplace Relations',
                              'Department of the Treasury', 'Department of Defence',
                              'Department of Resources Energy and Tourism',
                              'Department of the Prime Minister and Cabinet', 'Defence Materiel Organisation',
                              'Department of Infrastructure and Transport',
                              'Department of Infrastructure and Regional Development', 'National Capital Authority',
                              'Australian Organ and Tissue Donation and Transplantation Authority',
                              'Australian Communications and Media Authority (ACMA)', 'Cancer Australia',
                              'Australian Centre for International Agricultural Research', 'Safe Work Australia',
                              'Great Barrier Reef Marine Park Authority',
                              'Department of Health - Therapeutic Goods Administration',
                              'Commonwealth Grants Commission', 'Department of Immigration and Border Protection',
                              'Department of Parliamentary Services', 'Australian Fisheries Management Authority',
                              'Geoscience Australia',
                              'Department of Foreign Affairs and Trade - Australian Aid Program',
                              'Productivity Commission', 'Australian Human Rights Commission',
                              'Department of Education and Training',
                              'Department of Families, Housing, Community Services and Indigenous Affairs',
                              'Department of Employment', 'Office of National Assessments',
                              'Parliamentary Budget Office'],
        'statistics': ['Department of Education Employment and Workplace Relations', "Attorney-General's Department",
                       'Department of Immigration and Border Protection', 'Department of Defence',
                       'Department of Education and Training', "Department of Veterans' Affairs",
                       'Department of Foreign Affairs and Trade - Australian Aid Program',
                       'National Health Performance Authority', 'Australian Bureau of Statistics',
                       'Department of Infrastructure and Regional Development',
                       'Department of Regional Australia, Local Government, Arts and Sport',
                       'Department of Infrastructure and Transport',
                       'Department of the Environment - Australian Antarctic Division',
                       'Department of Communications and the Arts', 'Department of Industry, Innovation and Science',
                       'Department of the Environment', 'Bureau of Meteorology',
                       'Tertiary Education Quality and Standards Agency',
                       'Department of Agriculture and Water Resources', 'Clean Energy Regulator',
                       'Australian Competition and Consumer Commission', 'Department of the Treasury',
                       'Department of Infrastructure Transport Regional Development and Local Government',
                       'Australian Electoral Commission', 'Department of Resources Energy and Tourism',
                       'Department of Social Services', 'Australian National Preventive Health Agency',
                       'Department of the Prime Minister and Cabinet', 'Department of Foreign Affairs and Trade',
                       'Australian Communications and Media Authority (ACMA)',
                       'Department of Families, Housing, Community Services and Indigenous Affairs',
                       'Commonwealth Grants Commission', 'Defence Materiel Organisation',
                       'National Health and Medical Research Council', 'Department of Employment'],
        'drug abuse prevention or control programs': ['Department of Defence', 'Australian Federal Police',
                                                      'Department of Families, Housing, Community Services and Indigenous Affairs',
                                                      'Australian Criminal Intelligence Commission',
                                                      'Department of Immigration and Border Protection']
    }

    def category_agency(self):
        while True:
            try:
                category_name = input('Enter the category of interest:')
                listAgency = self.catByAgency[category_name.lower()]
                break
            except TypeError:
                print('Wrong type data')
            except KeyError:
                print('Key not found')
        return listAgency, category_name
            

    def match_interest(self, input_df, match_with):
        new_df = input_df.merge(match_with, left_on = 'UNSPSC Title', right_index = True).reset_index()
        return new_df


    def visual_q2(self, input_df):
        if 'Filter UNSPSC of Interest' not in list(input_df):
            # updated file after add Category of Interest
            self.updated_data = self.match_interest(input_df, self.match_df)

        # filter the dataframe to exclude the items not interested (Cat of int, is corresponding to the UNSPSC Title NOT Agency)
        interest_check = self.updated_data['Filter UNSPSC of Interest'] == 'Categories of Interest'
        data_interest = self.updated_data[interest_check == True]
#        print(data_interest.shape)
        
        summary_df = pd.DataFrame() # create an empty df to concat created pivot tables
        
        # show all the category
        for category in self.catByAgency.keys():
            agency = self.catByAgency.get(category)
            funding = data_interest.loc[self.updated_data['Agency Name'].isin(agency)]
            # group by agency name and sort in descend order
            top_funding = pd.pivot_table(funding, index='Agency Name', values='Value', aggfunc=np.sum) \
                 .sort_values(by='Value', ascending=False)
            top_funding.loc['Total'] = top_funding['Value'].sum() # add one row in the bottom to sum up the values
            top_funding.reset_index(level=0,inplace=True) # reset the index instead of using Agency name as index
            top_funding['Category Name'] = category
#            print(top_funding)
#            print(type(top_funding))
           
            summary_df = pd.concat([summary_df,top_funding]).reset_index(drop=True)
            
#        print(summary_df)
        return summary_df # get the final concat df, which labelled by category
#            
#        return top_funding

##### with same col df, use pd.concat([list of df]).reset_index(drop=True) to make concatenation


#        # return agency list under the category, and the category name of interest
#        agency, category_name = self.category_agency()
#        funding = data_interest.loc[input_df['Agency Name'].isin(agency)] 
#
#         # group by agency name and sort in descend order (DataFrame)
#        top_funding = pd.pivot_table(funding, index='Agency Name', values='Value', aggfunc=np.sum) \
#             .sort_values(by='Value', ascending=False)
#        print(type(top_funding))
#        top_funding.loc['Total'] = top_funding['Value'].sum()
#        top_funding['Category of Interest'] = category_name
#         # return top_funding # return sth to client
##        print(top_funding)
#        return top_funding
    
    # # question 1    
    # def visual_q1(self,input_df):
    #     # return a dataframe with an addition column ['Category of Intresest'] -- ['Categories of Intresest','Rest of Categories']
    #     self.updated_data = self.match_interest(input_df, self.match_df)
    #     # print(self.updated_data.shape) # (698111, 36)
    #    # print(list(self.updated_data)) # 'Filter UNSPSC of Interest' new column

       
