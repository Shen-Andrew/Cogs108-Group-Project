import pandas as pd
from datetime import date, datetime,timedelta

# Cleans the listings csv and returns a new dataframe
def clean_listings(df_listings):
    #get needed columns
    listings = df_listings[['id','accommodates','bedrooms','beds', 'zipcode', 'review_scores_rating']]
    return listings

# Cleans the calendar csv and returns a new dataframe
def clean_calendar(df_calendar):
    #get needed columns
    calendar = df_calendar[['listing_id','date','price']]
    #drop rows with missing data
    calendar.dropna()
    #convert price column to number
    calendar['price'] = calendar['price'].apply(dollar_to_number)
    #convert data column to datetime object
    calendar['date'] = pd.to_datetime(calendar['date'])
    return calendar

#Helper Function for clean_calendar
def dollar_to_number(string):
    string = string.replace('$', '')
    string = string.replace(',', '')
    string = string.replace('.', '')
    number = int(string)/100
    return number

# returns a df with rooms that meet room critera
def filter_room_details(df_listings, num_guests, num_bedrooms, num_beds, area, review):
    # get rooms greater than max_num_guests
    df_filtered_room = df_listings[(df_listings['accommodates'] ==  num_guests)
                        & (df_listings['bedrooms']  >=  num_bedrooms)
                        & (df_listings['beds']  >=  num_beds)
                        & (df_listings['review_scores_rating']  >=  review)]
    # if area is given get rooms in area
    if area != 0:
        df_filtered_room = df_filtered_room.loc[df_filtered_room['zipcode']  ==  area]
    return df_filtered_room


# returns a df with rooms that meet time critera
def filter_timespan(df_listings, df_calendar, start_date, end_date):

    # get a list of days in the timespan
    day_list = []
    day_count = (end_date - start_date).days + 1
    for day in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:
        day_list.append(day)

    # get listing ids from df_listings
    id_list = df_listings['id'].to_list()

    #remove ids from df_calendar that are not in id_list
    df_calendar_filtered = df_calendar[df_calendar['listing_id'].isin(id_list)]

    #remove dates from df_calendar that are not in day_list
    df_calendar_filtered = df_calendar[df_calendar['date'].isin(day_list)]

    # at this point calendar only contains the listings that meet our criteria
    # we can drop the listing_id column
    df_calendar_filtered = df_calendar_filtered.drop('listing_id', axis = 1)

    # group items by date and find the average price on that day
    df_calendar_filtered = df_calendar_filtered.groupby(['date']).mean()

    #convert and return as series
    series = pd.Series(df_calendar_filtered['price'])
    return series


# Timeseries function
# df_listings and df_calendar must be clean!
def create_timeseries(df_listings, df_calendar, num_guests, start_date, end_date, min_num_bedrooms, min_num_beds, zipcode, minimum_review):
    df_room_details = filter_room_details(df_listings, num_guests, min_num_bedrooms, min_num_beds, zipcode, minimum_review)
    timeseries = filter_timespan(df_room_details, df_calendar, start_date, end_date)
    return timeseries
