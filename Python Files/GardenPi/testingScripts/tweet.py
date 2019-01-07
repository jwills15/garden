from twython import Twython

C_key = "rRjHAXnZawtpqmbTwIqtws8SO"
C_secret = "91Q7kDJefRor7Jg9Zp8HEX1oBTmPShDG4ORFndId4VhMNB8qOI"
A_token = "1009920921820262400-GxLK5wZXE4AMR8ob5eSVNdWdjKfjyH"
A_secret = "hKzwWsE240O2bKCcd0myGS90LiKnF4gDhPctowSijG6vx"

def tweet(message):    
    myTweet = Twython(C_key, C_secret, A_token, A_secret)
    myTweet.update_status(status=message)

try:
    tweet('This is a test.')
except:
    print('did not tweet')
    pass
print('tweeted')
