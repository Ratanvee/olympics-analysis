import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# import plotly.express as px

# import seaborn as sns
# import matplotlib.pyplot as plt


events_df = pd.read_csv('templates/datasets/athlete_events.csv')
region_df = pd.read_csv('templates/datasets/noc_regions.csv')


def preprocess(events_df, region_df):
    events_df_summer = events_df[events_df['Season'] == 'Summer']
    events_df_summer_merge = events_df_summer.merge(region_df, on="NOC", how="left")
    events_df_summer_merge.drop_duplicates(inplace=True)

    events_df_summer_merge = pd.concat([events_df_summer_merge,pd.get_dummies(events_df_summer_merge['Medal']).replace({True: 1, False: 0})],axis=1)

    return events_df_summer_merge


def medal_tally(df):

    medal_tally = df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'])
    medal_tally1 = medal_tally.groupby('region').sum()[['Gold','Silver','Bronze']].sort_values('Gold',ascending=False).reset_index()
    medal_tally1['Total'] = medal_tally1['Gold'] + medal_tally1['Silver'] + medal_tally1['Bronze']

    
    return medal_tally1

def country_year_list(df):
    events_years = df['Year'].unique().tolist()
    events_years.sort()
    events_years.insert(0, 'Overall')

    events_country = np.unique(df['region'].dropna().values).tolist()
    events_country.sort()
    events_country.insert(0,'Overall')

    return events_years, events_country



def fetch_medal_tally(year,country):

    flag = 0
    
    df = preprocess(events_df,region_df)
   
    if year == 'Overall' and country == 'Overall':
        temp_df = df

    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = df[df['region'] == country]

    elif year != 'Overall' and country == 'Overall':
        temp_df = df[df['Year'] == int(year)]

    elif year != 'Overall' and country != 'Overall':
        temp_df = df[(df['Year'] == int(year)) & (df['region'] == country)]

    else: 
        print('some error')

    if flag == 1: 
        medal_tally = temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'])
        medal_tally1 = medal_tally.groupby('Year').sum()[['Gold','Silver','Bronze']].sort_values('Year').reset_index()

    else:
        medal_tally = temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'])
        medal_tally1 = medal_tally.groupby('region').sum()[['Gold','Silver','Bronze']].sort_values('Gold',ascending=False).reset_index()

    medal_tally1['Total'] = medal_tally1['Gold'] + medal_tally1['Silver'] + medal_tally1['Bronze']
    
    return medal_tally1
        
    

def top_statics(events_df_summer_merge):
    editions = events_df_summer_merge['Year'].unique().shape[0] - 1
    cities = events_df_summer_merge['City'].unique().shape[0]
    sports = events_df_summer_merge['Sport'].unique().shape[0]
    events = events_df_summer_merge['Event'].unique().shape[0]
    athlets = events_df_summer_merge['Name'].unique().shape[0]
    nations = events_df_summer_merge['region'].unique().shape[0]

    # print('Editions :',editions)
    # print('cities :',cities)
    # print('sports :',sports)
    # print('events :',events)
    # print('athlets :',athlets)
    # print('nations :',nations)
    return editions, cities, sports, events, athlets, nations
    

def charts_over_time(df,types):
    nations_over_time = df.drop_duplicates(['Year',types])['Year'].value_counts().reset_index().sort_values('Year')
    nations_over_time.rename(columns={'Year':'Editions','count':f'{types}'},inplace=True)
    # px.title(f'{types} over Year')
    return nations_over_time



def heatmap_df(df):
    x = df.drop_duplicates(['Year','Sport','Event'])
    x.pivot_table(index='Sport',columns='Year',values='Event',aggfunc='count').fillna(0).astype('int')
    # print(x.pivot_table(index='Sport',columns='Year',values='Event',aggfunc='count').fillna(0).astype('int'))
    # plt.figure(figsize=(20,20))

    # return sns.heatmap(x.pivot_table(index='Sport',columns='Year',values='Event',aggfunc='count').fillna(0).astype('int'),annot=True)
    return x.pivot_table(index='Sport',columns='Year',values='Event',aggfunc='count').fillna(0).astype('int')
    
    

def most_succesful(df,sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != "Overall":
        temp_df = temp_df[temp_df['Sport'] == sport]

    x = temp_df['Name'].value_counts().reset_index().merge(df,on='Name',how='left')[['Name','count','Sex','Age','Sport','region']].drop_duplicates('Name').reset_index()

    x.rename(columns={'count':'Medals'},inplace=True)
    x.drop(columns=['index'], inplace=True)

    return x


def countries_medal(df,region):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'],inplace=True)

    new_df = temp_df[temp_df['region'] == region]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    # return px.line(final_df,x='Year',y='Medal',title=f"Medals of {region} over the year")
    loli = pd.DataFrame(final_df)
    return loli



def heatmap_countries_game(df,region):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'],inplace=True)

    new_df = temp_df[temp_df['region'] == region]
    # plt.figure(figsize=(20,20))
    # return sns.heatmap(new_df.pivot_table(index='Sport',columns='Year',values='Medal',aggfunc='count').fillna(0).astype('int'),annot=True)
    # return new_df
    return new_df.pivot_table(index='Sport',columns='Year',values='Medal',aggfunc='count').fillna(0).astype('int')