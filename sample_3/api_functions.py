import pandas as pd
import json
def get_credentials(api,c_path):
	"""Reads API credentials from given txt file"""
	# reading credentials from the 2nd line in the txt file and assigning it to variable 'params'
	with open(c_path, 'r') as file:
		for line in file:
			credentials = json.loads(line)  # string must have double quotes to use json!
			try:
				return credentials[api]
			except:
				print('API name not recognized.')

def parse_response(report):
    """Parses and prints the Analytics Reporting API V4 response"""
    #Initialize results, in list format because two dataframes might return
    result_list = []

    #Initialize empty data container for the two dateranges (if there are two that is)
    data_csv = []
    data_csv2 = []

    #Initialize header rows
    header_row = []

    #Get column headers, metric headers, and dimension headers.
    columnHeader = report.get('columnHeader', {})
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    dimensionHeaders = columnHeader.get('dimensions', [])

    #Combine all of those headers into the header_row, which is in a list format
    for dheader in dimensionHeaders:
        header_row.append(dheader)
    for mheader in metricHeaders:
        header_row.append(mheader['name'])

    #Get data from each of the rows, and append them into a list
    rows = report.get('data', {}).get('rows', [])
    for row in rows:
        row_temp = []
        dimensions = row.get('dimensions', [])
        metrics = row.get('metrics', [])
        for d in dimensions:
            row_temp.append(d)
        for m in metrics[0]['values']:
            row_temp.append(m)
            data_csv.append(row_temp)

        #In case of a second date range, do the same thing for the second request
        if len(metrics) == 2:
            row_temp2 = []
            for d in dimensions:
                row_temp2.append(d)
            for m in metrics[1]['values']:
                row_temp2.append(m)
            data_csv2.append(row_temp2)

    #Putting those list formats into pandas dataframe, and append them into the final result
    result_df = pd.DataFrame(data_csv, columns=header_row)
    result_list.append(result_df)
    if data_csv2 != []:
        result_list.append(pd.DataFrame(data_csv2, columns=header_row))

    return result_list