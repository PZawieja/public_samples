# Weekly visits per country for my own blog: freedams.pl

# Packages needed for authentication:
import httplib2 as lib2
from oauth2client import client
# Packages needed for connecting to Google API:
from googleapiclient.discovery import build as google_build
# Data processing packages:
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
# customized function from a file in this directory
from api_functions import get_credentials, parse_response

# Choose API and file with credentials stored
api = 'google_analytics'
c_path = 'API_credentials.txt'         # sorry, this is a private one
store_path = 'sessions_p_country.txt'

params = get_credentials(api,c_path)

access_token  = params[0]
refresh_token = params[1]
client_id     = params[2]
client_secret = params[3]

#This is consistent for all Google services
token_uri = 'https://accounts.google.com/o/oauth2/token'

#We are essentially setting the expiry date to 1 day before today, which will make it always expire
token_expiry = datetime.now() - timedelta(days = 1)
user_agent = 'my-user-agent/1.0'

#The real code that initalized the client
credentials = client.GoogleCredentials(access_token=access_token, refresh_token=refresh_token,
                                       client_id=client_id, client_secret=client_secret,
                                       token_uri=token_uri, token_expiry=token_expiry,
                                       user_agent=user_agent)

#Initialize Http Protocol
http = lib2.Http()

#Authorize client
authorized = credentials.authorize(http)

api_name = 'analyticsreporting'
api_version = 'v4'

#Let's build the client
api_client = google_build(serviceName=api_name, version=api_version, http=authorized)

# weekly report
w_sessions = {
      'viewId': '168172428',
      'dateRanges': {
          'startDate': datetime.strftime(datetime.now() - timedelta(days = 7),'%Y-%m-%d'),
          'endDate': datetime.strftime(datetime.now(),'%Y-%m-%d')
      },
      #'dimensions': [{'name': 'ga:country'},{'name': 'ga:city'}],
	  'dimensions': [{'name': 'ga:country'}],
      'metrics': [{'expression': 'ga:sessions'}
                    ,{'expression': 'ga:users'} ]
    }

response = api_client.reports().batchGet(
      body={
        'reportRequests': w_sessions
      }).execute()

# Call parser and get the report in tabular form:
response_data = response.get('reports', [])[0]
parse_response(response_data)[0]
report_temp = parse_response(response_data)[0]

# data preparation for export
df = pd.DataFrame(report_temp)
df.columns = ['country','sessions','users']
df['sessions'] = pd.to_numeric(df['sessions'])
df = df.sort_values(by = 'sessions',ascending=False)

# Save results to CSV:
df.to_csv(store_path,index=False)
print('Results saved to txt file...')
print(df)
