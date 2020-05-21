import json
import tweepy
import asyncio
import re
from datetime import time, datetime

def get_credentials(filename):
    """
    Helper method to get credentials to authenticate twitter api

    Parameters
    ----------
    filename: str
        The filename of the json object that stores the credentials
    """
    with open(filename) as f:
        data = json.load(f)
        return (
            data['access token'],
            data['access token secret'],
            data['api key'],
            data['api secret key']
        )
    return None

access_token, access_token_secret, consumer_key, consumer_secret = get_credentials("credentials.json")
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def send_tweet(api, message, filename):
    """
    Method that sends a tweet to the twitter developer account
    After the tweet is sent, the json file that stores tweet information is updated
    
    Parameters
    -----------
    api: tweepy.API
        The tweepy api object that sends the tweet
    message: str
        The message that will be tweeted
    filename: str
        The file name of the json file that stores tweet information
    """
    api.update_status(message)

    with open(filename, 'r') as f:
        data = json.load(f)
        data['days'] += 1

    with open(filename, 'w') as f:
        json.dump(data, f)


def log_next_tweet(filename):
    """
    Sends a terminal message with the JSON data for the next tweet
    
    Parameters
    ----------
    filename: str
        The file name of the json file that stores tweet information
    """
    with open(filename, 'r') as f:
        data = json.load(f)

        print('~' * 35)
        print("JSON data for next tweet")
        formatted_json = json.dumps(data, indent=1)
        print(formatted_json)
        print('~' * 35)

async def tweet_main(filename="tweet.json"):
    """
    The main event loop which sends tweets
    Runs an infinite while with asynchornous stopping ponits after every iteration
    
    The while loop goes throught the process:
        1.) Loads data from the tweet json object
        2.) Gets the current time
        3.) Checks if the current hour and current minute are the same
        4.) If the current hours and minute are the same, send the tweet and sleep for a minute
        5.) If not, sleep for a second

    Parameters
    ----------
    filename: str, optional
        The file name of the json file that stores tweet information
    """
    log_next_tweet(filename)
    
    time_regex = re.compile(r'(\d{1,2}):(\d{1,2})')

    while 1:
        with open(filename) as f:
            data = json.load(f)
            # Extract the time from the json object
            time_str = data['time']
            mo = time_regex.match(time_str)
            hour, minute = int(mo.group(1)), int(mo.group(2))
            tweet_time = time(hour=hour, minute=minute)

            # Extract tweet message
            message = data['message']
            days = data['days']
            message = message % days

        now = datetime.now().time()
        if now.hour == tweet_time.hour and now.minute == tweet_time.minute:
            send_tweet(api, message, filename)
            log_next_tweet(filename)
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)

async def main():
    """
    Main asynchrounous method that is ran when the python file is executed
    """
    tweet_task = asyncio.create_task(
        tweet_main()
    )

    await tweet_task


if __name__ == "__main__":
    asyncio.run(main())