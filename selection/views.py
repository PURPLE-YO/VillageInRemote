from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
import pandas as pd
import time
import sys

sys.path.append('/Users/NAN/Desktop/real_project')
import manage


start_situation = 0
items = {}
flag = 0
df = pd.DataFrame()
corpus = {}


# class UserForm(forms.Form):
# 	username = forms.CharField(label = 'UserName', max_length = 100)
# 	password = forms.CharField(label = 'Password', widget = forms.PasswordInput())
@csrf_exempt
def query(request):
    global df, start_situation, corpus,items
    if request.method == 'POST':            # acquire user inputs when submit botton clicked
        category1 = request.POST.get('category')
        precurement = request.POST.get('Precurement')
        agency = request.POST.get('agency')
        contract_id = request.POST.get('contract_ID')
        bottom_v1 = request.POST.get('valueB')
        top_v1 = request.POST.get('valueT')
        start_date1 = request.POST.get('Start_date')
        end_date1 = request.POST.get('End_date')
        panel1 = request.POST.get('p-radio','')
        contract_flag1 = request.POST.get('con-radio','')
        out_flag1 = request.POST.get('out-radio','')
        consultancy_flag1 = request.POST.get('Consultancy-radio','')
        supplier = request.POST.get('supplier_name')
        keywords = request.POST.get('keywords')
        comparison = request.POST.get('compare')
        name1 = request.POST.get('name1')
        name2 = request.POST.get('name2')
        
        # generate date range
        date_range = {}
        date_range['Start Date'] = str(start_date1) 
        date_range['End Date'] = str(end_date1)
        date_range1 = []
        if (date_range['End Date'] == '') and (date_range['Start Date']==''):  
            pass
        else:
            date_range1.append(date_range)
        

        # split category
        cate_list = category1.split(',')
        categories = []
        for t in cate_list:
            n = t.lower().strip()
            categories.append(n)

        # generate value
        values = []
        if (bottom_v1=='') and (top_v1==''):
            pass
        else:
            values = [bottom_v1, top_v1]

        #generate comparison list
        
        n1 = name1.strip()
        n2 = name2.strip()
        compare_list = [n1, n2]
        
        #switch falg values
        #panel
        if panel1 == 'none':
        	panel2 = ''
        else:
        	panel2 = panel1
        #contract_flag
        if contract_flag1 == 'none':
        	contract_flag2 = ''
        else:
        	contract_flag2 = contract_flag1
        #out_flag
        if out_flag1 == 'none':
        	out_flag2 = ''
        else:
        	out_flag2 = out_flag1
        #consultancy_flag
        if consultancy_flag1 == 'none':
        	consultancy_flag2 = ''
        else:
        	consultancy_flag2 = consultancy_flag1
        
        #switch selection values
        #keywords
        if keywords == '-- Select one Method --':
        	keywords1 = 'Agency Name'
        else:
        	keywords1 = keywords
        #precurement
        if precurement == '-- Select one Method --':
        	precurement1 = ''
        else:
        	precurement1 = precurement
        #conparison
        if comparison == '-- Select one Method --':
        	comparison1 = ''
        else:
        	comparison1 = comparison

        # generate comparison dict
        comparison_dict = {}
        if comparison1 == "":
            pass
        else:
            comparison_dict[comparison1] = compare_list



        # generate dictionary
        if categories != '':
            items['Category'] = categories
        if len(date_range1)>0:            
            items['Date Range'] = date_range1
        if agency !='':            
            items['Agency Name'] = agency
        if bool(values):
            items['Value'] = values
        if contract_id !='':
            items['Contract ID'] = contract_id
        if precurement1 !='':
            items['Precurement Method'] = precurement1
        if panel2 !='':
            items['Panel Arrangement'] = panel2
        if contract_flag2 !='':
            items['Confidentiality Contract Flag'] = contract_flag2
        if out_flag2 !='':
            items['Confidentiality Outputs Flag'] = out_flag2
        if consultancy_flag2 !='':
            items['Consultancy Flag'] = consultancy_flag2
        if supplier !='':
            items['Supplier Name'] = supplier
        if keywords1 !='':
            items['Keywords'] = keywords1
        if bool(comparison_dict):
            items['Compare'] = comparison_dict
        items['Timestamp'] = 0
        
        
        '''
        =================================================================================
        @Text analysing and ploting process
        =================================================================================
        '''
        # change working directory
        sys.path.append('/Users/NAN/Desktop/real_project/selection')
        from dashV5 import Dashboard
        from backendV5 import Pre_process,TextAnalysis
        start_time = time.time()
        pr = Pre_process()
        ta = TextAnalysis()
        dash = Dashboard()
        
        print("======================backend objects have been established in %s seconds ======================" % (time.time() - start_time))
        
        if manage.flag == 0:
            pr.upload_file('/Users/NAN/Desktop/Qt Project/All_data.csv')            
            df = pr.cleaned_Dataframe.sort_values(by='Value',ascending=False)
       
            manage.flag += 1
            print("======================dataset has been cleaned in %s seconds======================"% (time.time() - start_time))
        
            ta.title_dict(df)
            corpus = ta.index_dict
            print("======================corpus has been created======================in %s seconds="% (time.time() - start_time))
        
#        print(df.shape)
#        print(len(corpus))         
        keyword = items
#        print(keyword)
        
        
        while keyword['Timestamp'] == 0:
            print("======================keyword confirmed======================in %s seconds="% (time.time() - start_time))
            
            output = ta.find_match(keyword, df)
            print(len(output))
            print("======================output confirmed======================in %s seconds="% (time.time() - start_time))
            
            df_new = df.loc[output]
            print(df_new.shape)
            print("======================new df selected======================in %s seconds="% (time.time() - start_time))
            
            print(keyword)
            
            dash.scatter_plot(keyword=keyword['Keywords'],dataframe=df_new)
            dash.pie_plot_by_key(filtered_df=df_new,searching_dict=keyword)
            dash.hbar_by_key(dataframe=df_new,keyword=keyword['Keywords'],Procurement=keyword['Precurement Method'])
            if "Category" in keyword.keys():
                df_filtered = dash.select_rows(df_new,corpus,searching_dict=keyword)
                dash.hbar_by_cat(df_filtered,keyword['Precurement Method'])
            if "Compare" in keyword.keys():
                dash.compare_entity(df_new,com_key=keyword['Compare'],proc=True)
            dash.table_plot(df_new)
                        
            # change Timestamp to 1, thus, before new query is coming, backend will not process new plot
            keyword['Timestamp'] = 1
            
        '''
        =================================================================================
        @Text analysing and ploting process
        =================================================================================
        '''      
        return HttpResponseRedirect("/dashboard")

    else:
        return render(request, 'query_page.html')

@csrf_exempt
def upload_file(request): 
    global flag
    if request.method == "POST":    # process request when request is 'POST'  
        myFile = request.FILES.get("myfile", None)
#        print ('===========file read===========', type(myFile))    # acquire uploaded file, return None when no file detected 
        if myFile == None:  
            return HttpResponse("no files for upload!")
        else:
            destination = open(os.path.join("/Users/NAN/Desktop/real_project",myFile.name),'wb+')    # open a new file on the destination folder 
            for chunk in myFile.chunks():      # write content into new file by chunks  
                destination.write(chunk)  
            destination.close()  
            return HttpResponseRedirect("/query")
            flag = 1
            print(flag)
    else:
        return render(request, "upload_file.html")



@csrf_exempt
def login(request):
	if request.method == 'POST':
		#print(request.POST)               
		uname = request.POST.get('user')               #acquire user inputs 
		pword = request.POST.get('password')
		user1 = uname.lower().strip()
		pword1 = pword.lower().strip()
		user = auth.authenticate(username = user1, password = pword1)   # test whether user&password pair is leagal and create user object 
		print (type(user))
		if user is not None:
			auth.login(request, user)             #login user object
			#return render(request, 'upload_file.html')
			
			return HttpResponseRedirect("/upload")
		else:
			#return render(request, 'login.html')
			
			return HttpResponseRedirect("/login")
	else:
		return render(request, 'login.html')
@csrf_exempt
def register(request):
	if request.method == 'POST':     #acquire user inputs
		name = request.POST.get('username')
		pword = request.POST.get('password')
		username1 = name.lower().strip()
		password1 = pword.lower().strip()
		user_Add = User.objects.create_user(username = username1, password = password1, is_staff = False, is_superuser = False)# create user object
		user_Add.set_password(password1)#set user password
		user_Add.save()#save user
		return HttpResponseRedirect("/login")
	else:
		return render(request, 'register.html')

# @csrf_exempt
# def logout(request):
# 	auth.logout(request)
# 	return HttpResponseRedirect("/lock")

@csrf_exempt
def dashboard(request):
    if request == 'POST':
        return HttpResponseRedirect("/query")
    else:
        return render(request, 'dashboard.html')
