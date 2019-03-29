import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# PYCHARM DISPLAY OPTIONS
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
pd.options.display.max_rows = 9999
pd.options.display.max_columns = 9999
pd.options.display.float_format = '{:.2f}'.format

# PARAMETERS
CHARTS_FOLDER = r'charts/'
F_TYPE = '.png'
f_platforms = 'Data.csv'
f_budget    = 'Budget.csv'

# ==================================================================================================================== #
#                                                                                                                      #
#               IIIIIII  II     II  II    II  IIIIIIII  IIIIIIIIII  II       III       II    II    IIIIII              #
#               II       II     II  IIII  II  II            II      II     II   II     IIII  II   III                  #
#               IIIIIII  II     II  II  IIII  II            II      II    II      II   II  IIII    IIIIII              #
#               II       II     II  II    II  II            II      II     II   II     II    II       III              #
#               II         IIIII    II    II  IIIIIII       II      II       III       II    II   IIIIII               #
#                                                                                                                      #
# ==================================================================================================================== #

def folder_for_charts():
    # CHECK IF FOLDER EXISTS
    if not os.path.exists(CHARTS_FOLDER):
        os.makedirs(CHARTS_FOLDER)

    # REMOVE ALL THE FILES FROM CHARTS_FOLDER DIRECTORY
    files = glob.glob(CHARTS_FOLDER + '*')
    for file in files:
        os.remove(file)

# ==================================================================================================================== #
#                                                                                                                      #
#               IIIIIII   II   II  IIIIIII  IIIIIII  II     II   IIIIIIII  II       III       II    II                 #
#               II         II II   II       II       II     II      II     II     II   II     IIII  II                 #
#               IIIIIII     II     IIIIIII  II       II     II      II     II    II     II    II  IIII                 #
#               II         II II   II       II       II     II      II     II     II   II     II    II                 #
#               IIIIIII   II    II IIIIIII  IIIIIII    IIIII        II     II       III       III   II                 #
#                                                                                                                      #
# ==================================================================================================================== #


platforms = pd.read_csv(f_platforms)
budget    = pd.read_csv(f_budget)

# changing "date" column type to datetime:
platforms['date'] = pd.to_datetime(platforms['date'])
budget['date']    = pd.to_datetime(budget['date'])

# Making WIDE data LONG:
# pd.melt() is "melting" multiple columns into one. Preserve columns from melting and add them to id_vars = []
platforms = pd.melt(platforms, id_vars = 'date',var_name='platform',value_name='clicks')
budget = pd.melt(budget,	   id_vars = 'date',var_name='platform',value_name='budget')

# JOIN both dataframes:
df = pd.merge(platforms, budget,  how='left', left_on=['date','platform'], right_on = ['date','platform'])

# KPI definition: Cost per Click:
df['CpC'] = df['budget'] / df['clicks']

# CLEANING UP: zero clicks divided by budget results with 'inf' value, which needs to be replaced by 0
# convert inf to NaN
df.replace([np.inf], np.nan, inplace=True)
# fill NaN with 0s
df['CpC'].fillna(0,inplace=True)

# Adding column YEAR_WEEK
df['year_week'] = df['date'].dt.strftime('%Y-%U')


# ========== [ PLOTTING the results ] ============================
folder_for_charts()

platform_lst = list(df['platform'].unique())

for i in platform_lst:
    fig, ax = plt.subplots(figsize=(15, 3))

    ax.plot(df[df['platform']==i]['date'],
            df[df['platform']==i]['CpC'])
    ax.plot(df[df['platform']==i]['date'],
            df[df['platform']==i]['clicks'])

    ax.legend(['CpC','clicks'])
    ax.set(xlabel='date',
           ylabel='CpC',
           title=i)
    plt.savefig(CHARTS_FOLDER + str(i) + '.png')

# plt.show()


# ========== [ PIVOT for CSV export ] ============================
pvt = pd.pivot_table(df,
                     values=['CpC','clicks','budget'],
                     index=['date','year_week'],
                     columns='platform'
                    ,fill_value=0)

pvt.to_csv(CHARTS_FOLDER+'data.csv', header=True, float_format='%.3f')

print('Done...')
