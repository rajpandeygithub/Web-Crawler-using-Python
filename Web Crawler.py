# -*- coding: utf-8 -*-
"""
@author: Rajkumar Pandey

"""
#importing the required modules

import requests
import re
import pandas as pd

# Method to get content from a URL

def get_page_content(url):
    r = requests.get(url)
    html_text = r.text
    html_text = re.sub("\s+", " ", html_text)
    return html_text

# Method to get all the categories links

def extract_sic_codes_businesses(content):
    sic_url_regex = re.compile(r'<a href="(https://siccode.com/sic-code-hierarchy/.*?)"')
    results = re.findall(sic_url_regex, content)
    return results

# Method to extract subcategories links

def extract_sic_categories(url):
    content = get_page_content(url)
    sic_categories_regex = re.compile(r'<a href="(https://siccode.com/sic-code/.*?)"')
    results = re.findall(sic_categories_regex, content)
    return results
    
# Method to get the 4 digit sic code from the subcategory link

def extract_sic_codes(url):
    sic_codes_regex = re.compile(r'(?:\D|^)(\d{4})(?:\D|$)')
    results = re.findall(sic_codes_regex,url)
    return results

# Method to get all the 4 digit SIC Codes

def get_sic_codes(url):
    content = get_page_content(url)
    result = extract_sic_codes_businesses(content)
    res=[]
    temp=[]
    for j in range(1, len(result)):
        temp.extend(extract_sic_categories(result[j]))
    for i in range(1, len(temp)):
        res.extend(extract_sic_codes(temp[i]))
    res.sort
    return res

# Method to get the link for a given company belonging to an SIC code

def get_businesses(sic_code):
    url = "https://siccode.com/search-business/sic:"+str(sic_code)
    content = get_page_content(url)
    business_name_regex = re.compile(r'<a href="(https://siccode.com/business/.*?)"')
    results = re.findall(business_name_regex, content)
    if results!=[] : 
        return results[0] # To limit one business link for an SIC code

# Method to get the values for required attributes for each company

def get_business_details(url1):
    content = get_page_content(url1)
    business_name_regex = re.compile(r'<span class="bold color-dark p-postal-code">(.*?)</span>')
    zips = re.findall(business_name_regex, content)
    state_regex=re.compile(r'<span class="bold color-dark p-region">(.*?)</span>')
    state = re.findall(state_regex, content)
    city_regex=re.compile(r'<span class="bold color-dark p-locality">(.*?)</span>')
    city = re.findall(city_regex, content)
    NAICS_regex=re.compile(r'title="More Details About NAICS Code (.*?)">')
    NAICS = re.findall(NAICS_regex, content)
    SIC_regex=re.compile(r'title="More Details About SIC Code (.*?)">')
    SIC = re.findall(SIC_regex, content)
    Business_regex=re.compile(r'<span itemprop="description">&#34;<b>(.*?)</b>')
    Business = re.findall(Business_regex, content)
    category_regex=re.compile(r'<p class="digit"> <span>(.*?)</span>')
    category=re.findall(category_regex,content)
    revenue_regex=re.compile(r'<span>Est. Annual Revenue:</span> <span class="bold color-dark icon-score-(.*?)">')
    revenue=re.findall(revenue_regex,content)
    size_regex=re.compile(r'<span>Est. Company Size:</span> <span class="bold color-dark icon-score-(.*?)">')
    size=re.findall(size_regex,content)
    return Business[0],category[0],SIC[0],NAICS[0],city[0],state[0],zips[0],'$'*int(revenue[0]),size[0]

#Code to get a consolidated list for all the attributes 

url = "https://siccode.com/sic-code-lookup-directory"
codes=get_sic_codes(url)
business=[]
ans=[]

for y in range(0,150): # To limit the time taken to fetch all the business links we are limiting to 150 instead of complete set of codes  
    if get_businesses(codes[y]) is not None :
        business.append(get_businesses(codes[y]))
for z in range(0,len(business)):
   ans.append(get_business_details(business[z]))


#Creating dataframe from the list

my_python_list = ans
new_df = pd.DataFrame(columns=['Business Name', 'Category','my_column_name_3', 'my_column_name_4','City', 'State','Zip Code', 'Est. Annual Revenue','my_column_name_9'], data=my_python_list)
new_df['SIC Code'] = new_df.my_column_name_3.str.split("-",expand=True)[0]
new_df['SIC Description'] = new_df.my_column_name_3.str.split("-",expand=True)[1]
new_df['NAICS Code'] = new_df.my_column_name_4.str.split("-",expand=True)[0]
new_df['NAICS Description'] = new_df.my_column_name_4.str.split("-",expand=True)[1]
new_df.loc[new_df['my_column_name_9'] == '1', 'Est. Company Size'] = 'Small' 
new_df.loc[new_df['my_column_name_9'] == '2', 'Est. Company Size'] = 'Medium' 
new_df.loc[new_df['my_column_name_9'] == '3', 'Est. Company Size'] = 'Large' 

#Creating the final dataframe
final = new_df[['Business Name', 'Category','SIC Code','SIC Description', 'NAICS Code','NAICS Description','City', 'State','Zip Code', 'Est. Annual Revenue','Est. Company Size']].iloc[0:100]

#Exporting results in an excel file
final.to_excel("C:/Raj/Output.xlsx",index = False) 







