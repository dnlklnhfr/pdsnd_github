import time
from datetime import timedelta
from os import system, name
import re
import sys
import pandas as pd

CITY_DATA = { 'chi': 'chicago.csv',
              'nyc': 'new_york_city.csv',
              'wdc': 'washington.csv' }
cities = { 'chi': 'Chicago',
           'nyc': 'New York City',
           'wdc': 'Washington'
         }
months = { 'jan': 'January', 
           'feb': 'February', 
           'mar': 'March',
           'apr': 'April',
           'may': 'May', 
           'jun': 'June',
           'all': 'all'
         }
days   = { 'mo': 'Monday',
           'tu': 'Tuesday',
           'we': 'Wednesday', 
           'th': 'Thursday',
           'fr': 'Friday',
           'sa': 'Saturday',
           'su': 'Sunday',
           'all': 'all'
         }
exit_command = 'exit'
exit_message = '\nExiting script ...\n\nByebye, see you next time ;)'
divider = 40*'*'+'\n'
header = 80*'#'

def generate_user_prompt(requested_content, iterable):
    """ Consolidated user prompt to gather the information about the users filter preferences
    
    Parameters:
        (str)  requested_content - the topic the user is asked to choose, e.g. 'city'
        (dict) iterable - the options that can be selected where {key} is the option and {value} is the label

    Returns:
        (str) user_input - the choice the user entered, if it was a valid input
    """
    
    prompt_text = 'Please select a {} by abbreviation: \n'.format(requested_content)
    for key, value in iterable.items():
        prompt_text += '{}: {}\n'.format(key, value)
    prompt_text += '\n{}: Leave script\n'.format(exit_command)
    
    while True:
        user_input = input(prompt_text).lower()
        if (user_input in iterable.keys()):
            clear()
            return user_input
        elif user_input == exit_command:
            print(divider)
            print(exit_message)
            time.sleep(2)
            sys.exit(0)
        else:
            clear()
            print('Invalid input. Please retry ...\n')
            print(divider)
            continue


            
def clear():
    """ Clear the console output (cross-platform, as I don't know on which system you guys are working)
        source: https://www.geeksforgeeks.org/clear-screen-python/
    """
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        
        

def get_filters():
    """ Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    
    print('Hello! Let\'s explore some US bikeshare data!\n')
    print(divider)
    # get user input for city (Chicago, New York City, Washington).
    city = generate_user_prompt('city', cities)

    # get user input for month (all, january, february, ... , june)
    month = generate_user_prompt('month', months)
    
    # get user input for day of week (all, monday, tuesday, ... sunday)
    day = generate_user_prompt('day', days)
    
    print(divider)
    print('Your choices:\n# City: {}\n# Month: {}\n# Day: {}\n'.format(cities[city], months[month], days[day]))
    print(divider)
    return city, month, day



def load_data(city, month, day):
    """ Load data for the specified city and filters by month and day if applicable.

    Parameters:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        (pd.DataFrame) df - city data filtered by month and day
    """
    df = pd.read_csv(CITY_DATA[city])
    
    # convert the Start Time column to datetime and determine month and day from it
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['month'] = df['Start Time'].dt.month_name()
    # In case of compatibility issues: Udacity sample solution in project chp.10 'Solution #3' says weekday_name 
    # this property does not exist in pd[v1.1.5].Series.dt - used pd.Series.dt.day_name() instead, refer to official documentation:
    # https://pandas.pydata.org/pandas-docs/version/1.1.5/reference/series.html#datetime-methods
    df['day_of_week'] = df['Start Time'].dt.day_name() 

    # now apply the user-requested filters on the dataset
    if month != 'all':
        df = df[df['month'] == months[month]]
    if day != 'all':
        df = df[df['day_of_week'] == days[day]]
    
    return df



def time_stats(df, month, day):
    """Displays statistics on the most frequent times of travel.
    
    Parameters:
        (pd.DataFrame) df - the dataset to analyze
        (str) month - {key} of the month to filter by, or "all" if no filter is applied
        (str) day - {key} of the day of week to filter by, or "all" if no filter is applied
    """
    
    print('### Most frequent times of travel')
    print(header)
    start_time = time.time()

    # display the most common month, but only if all months are requested, otherwise this KPI doesn't make sense
    if month == 'all':
        print('Month:\t{}'.format(df['month'].mode()[0]))

    # display the most common day of week, but only if all days are requested, otherwise this KPI doesn't make sense
    if day == 'all':
        print('Day:\t{}'.format(df['day_of_week'].mode()[0]))

    # extract the hour-info from the start date as a new column and display the most common start hour
    # formatting the time with padding: https://pyformat.info/#string_pad_align
    df['hour'] = df['Start Time'].dt.hour
    print('Hour:\t{:0>2}:00'.format(df['hour'].mode()[0]))

    print("\nCalculation took %s seconds." % (time.time() - start_time))
    print(divider)

    

def station_stats(df):
    """Displays statistics on the most popular stations and trip.
    
    Parameters:
        (pd.DataFrame) df - the dataset to analyze
    """
    
    print('### Most popular stations and trips')
    print(header)
    start_time = time.time()

    # display most commonly used start station
    print('Start Station:\t{}'.format(df['Start Station'].mode()[0]))

    # display most commonly used end station
    print('End Station:\t{}'.format(df['End Station'].mode()[0]))

    # display most frequent combination of start station and end station trip
    # inspired by: https://stackoverflow.com/a/53037757
    most_popular_trip = df.groupby(['Start Station', 'End Station']).size().idxmax()
    print('Trip:\t\t{} -> {}'.format(most_popular_trip[0], most_popular_trip[1]))
    
    print("\nCalculation took %s seconds." % (time.time() - start_time))
    print(divider)

    

def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration.
    
    Parameters:
        (pd.DataFrame) df - the dataset to analyze
    """
    
    print('### Trip duration info')
    print(header)
    start_time = time.time()

    # display total travel time
    print('Total travel time:\t{}'.format(timedelta(seconds=int(df['Trip Duration'].sum()))))
    
    # display mean travel time
    print('Mean travel time:\t{}'.format(timedelta(seconds=int(df['Trip Duration'].mean()))))

    print("\nCalculation took %s seconds." % (time.time() - start_time))
    print(divider)

    

def user_stats(df):
    """Displays statistics on bikeshare users.
    
    Parameters:
        (pd.DataFrame) df - the dataset to analyze
    """
    
    print('### User Statistics')
    print(header)
    start_time = time.time()

    # Display counts of user types
    print('## Types of users:\n{}'.format(re.sub(' +',':\t', df['User Type'].value_counts().to_string())))

    # Display counts of gender if gender data is available
    print('\n## Gender distribution:')
    if 'Gender' in df.columns:
        print('{}'.format(re.sub(' +',':\t\t', df['Gender'].value_counts().to_string())))
    else:
        print('\t{}'.format('No data'))

    # Display earliest, most recent, and most common year of birth if birth year data is available
    print('\n## Birth year information:')
    if 'Birth Year' in df.columns:
        year_of_birth = df['Birth Year']
        print('Earliest:\t{}'.format(int(year_of_birth.min())))
        print('Latest:\t\t{}'.format(int(year_of_birth.max())))
        print('Most common:\t{}'.format(int(year_of_birth.mode()[0])))
    else:
        print('\t{}'.format('No data'))

    print("\nCalculation took %s seconds." % (time.time() - start_time))
    print(divider)


    
def main():
    while True:
        city, month, day = get_filters()
        df = load_data(city, month, day)
        
        time_stats(df, month, day)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)

        print('\nWhat would you like to do now? Choose one of the following options: \n')
        print('n:\tNew analysis')
        print('i:\tInspect (prefiltered) raw data')
        print('e:\tExit')
        
        choice = input()
        if(choice.lower() == 'i'):
            pd.set_option('display.max_columns',200)
            print('\n\nDisplaying five rows of raw data based on your filters ...')
            print('For next five rows hit \'Enter\', to Exit enter anything and confirm\n')
            print('Available rows:\t{}\n'.format(len(df.index)))
            # Well, here it would be interesting to know, why 
            # df.iloc[current_row_index:current_row_index+5] doesn't work and if there's a more elegant solution than mine.
            current_row_index = 0
            while (current_row_index+5) <= len(df.index):
                next_five = current_row_index+5
                print(df.iloc[current_row_index:next_five]) 
                current_row_index += 5
                if input() == '':
                    continue
                else:
                    clear()
                    break
        elif choice.lower() == 'e':
            print(exit_message)
            time.sleep(2)
            break
        else:
            clear()
            continue


if __name__ == "__main__":
	main()