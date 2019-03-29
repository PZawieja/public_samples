import pandas as pd
import numpy as np
import json
import os
import re
from urllib.request import urlretrieve
from pandas.io.json import json_normalize #package for flattening json in pandas df

# pd.set_option('display.height', 1000)
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)

# PYCHARM DISPLAY OPTIONS
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
pd.options.display.max_rows = 999
pd.options.display.max_columns = 999
pd.options.display.float_format = '{:.2f}'.format

# PARAMETERS
JSON_FILE      = 'recipes'
F_TYPE         = '.json'
JSON_FULL_NAME = JSON_FILE + F_TYPE

############### Read JSON file ################
# 1 METHOD: from server
url = 'https://s3-eu-west-1.amazonaws.com/dwh-test-resources/recipes.json'
urlretrieve(url, JSON_FULL_NAME)

# 2 METHOD: from file saved locally
# JSON_FULL_NAME = 'recipes.json'
with open(JSON_FULL_NAME) as f:
    data = [json.loads(line) for line in f]

# create dataframe
df = json_normalize(data)


# Write a script in Python that reads the recipes json, extracts every recipe
# that has “Chilies” as one of the ingredients. Please allow for
# mispelling of the word for example Chiles as well as the singular form of the word.
df = df[df['ingredients'].str.contains('Chil',flags=re.IGNORECASE) == True]

# Add an extra field to each of the extracted recipes with the name difficulty.
# The difficulty field would have a value of "Hard" if the total of prepTime
# and cookTime is greater than 1 hour, "Medium" if the total is between 30 minutes and 1 hour,
# "Easy" if the total is less than 30 minutes, and "Unknown" otherwise.


# Function checks if the PT is provided. If not it returns -9999.
# In any other case RE returns the values for Hours and Minutes.
# Hours are conveted to minutes
def clear_time(s):
    hours   = re.findall(r"(\d+)H",s)
    minutes = re.findall(r"(\d+)M",s)
    if (len(hours) == 0 | len(minutes) == 0):
        return -9999
    elif len(hours) > 0:
        time = int(hours[0]) * 60
        if len(minutes) > 0:
            return  time + int(minutes[0])
        else:
            return time
    else:
        time = int(minutes[0])
        return time

df['cookTime_new'] = df['cookTime'].apply(clear_time)
df['prepTime_new'] = df['prepTime'].apply(clear_time)

# labels
df['time_total'] = df['cookTime_new'] + df['prepTime_new']

def labels(time_total):
    if time_total <0:
        return 'unknown'
    elif time_total <30:
        return 'Easy'
    elif time_total <60:
        return 'Medium'
    else:
        return 'Hard'

df['diff_level'] = df['time_total'].apply(labels)

# Writing to CSV:
final_file = df[['cookTime', 'datePublished', 'description', 'image', 'ingredients',
       'name', 'prepTime', 'recipeYield', 'url','diff_level']]
final_file.to_csv('output.csv',sep=',', encoding='utf-8')

print('Done...')
