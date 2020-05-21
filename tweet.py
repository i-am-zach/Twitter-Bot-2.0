import json
import tweepy
import asyncio
import re
from datetime import time, datetime

def get_credentials(filename):
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
    api.update_status(message)
    with open(filename, 'r') as f:
        data = json.load(f)
        data['days'] += 1

    with open(filename, 'w') as f:
        json.dump(data, f)


def log_next_tweet(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

        print('~' * 35)
        print("JSON data for next tweet")
        formatted_json = json.dumps(data, indent=1)
        print(formatted_json)
        print('~' * 35)

async def tweet_main(filename="tweet.json"):
    log_next_tweet(filename)
    
    time_regex = re.compile(r'(\d{1,2}):(\d{1,2})')

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

    while 1:
        now = datetime.now().time()
        if now.hour == tweet_time.hour and now.minute == tweet_time.minute:
            send_tweet(api, message, filename)
            log_next_tweet(filename)
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)

async def main():
    tweet_task = asyncio.create_task(
        tweet_main()
    )

    await tweet_task


if __name__ == "__main__":
    asyncio.run(main())