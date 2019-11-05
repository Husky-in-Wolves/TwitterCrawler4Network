#!/usr/bin/env python
import sys, os, json, random
import requests
from time import sleep
from requests_oauthlib import OAuth1
import random

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:1080'


def writeProfile(Dict, profile_path):
    profile_file = os.path.join(profile_path, 'user_information.txt')
    with open(profile_file, 'a', encoding='UTF-8') as file:
        for key in Dict.keys():
            val = str(Dict[key]).strip("\n").strip()
            file.write(key + ":\t" + val + "\n")
        file.write("\n")


def writeFile(tweet, output_file, ):
    try:
        keys = tweet.keys()
        last_id = tweet["id"]
        with open(output_file, "a", encoding='UTF-8') as file:
            for key in keys:
                val = str(tweet[key]).strip("\n").strip()
                file.write(key + ":\t" + val + "\n")
            file.write("\n")
    except:
        return False, None
    else:
        return True, last_id




def get_information(user_id, screen_name, config):
    # the token to enter the twitter
    token = random.choice([config['token_1'], config['token_2'], config['token_3'], config['token_4']])
    auth = OAuth1(token['consumer_key'], token['consumer_secret'], token['oauth_token'], token['oauth_secret'])
    # the parameter for requests
    if screen_name != None:
        args = {'screen_name': screen_name,
                'include_entities': 'False', }
    elif user_id != None and screen_name == None:
        args = {'user_id': user_id,
                'include_entities': 'False', }
    else:
        return None
    # get the result
    try:
        response = requests.get(config['url_user_name'], params=args, auth=auth, stream=True)
        detail = response.json()
        Dict = {}
        Dict['id'] = detail["id"]
        Dict['screen_name'] = detail["screen_name"]
        Dict['description'] = detail['description']
        Dict['friends_count'] = detail['friends_count']
        Dict['statuses_count'] = detail['statuses_count']
        Dict['verified'] = detail['verified']
    except:

        return None
    else:
        if Dict['friends_count'] >= 25 and Dict['statuses_count'] >= 500:
            return Dict
        else:
            return None


''' get his friend list '''
def get_friends(screen_name, config):
    # the token to enter the twitter
    token = random.choice([config['token_1'], config['token_2'], config['token_3'], config['token_4']])
    auth = OAuth1(token['consumer_key'], token['consumer_secret'], token['oauth_token'], token['oauth_secret'])
    ''' the parameter for requests '''
    args = {
        'cursor': -1,
        'screen_name': screen_name,
        'count': config['friends_count'], }
    ''' get the friend list of screen_name '''
    try:
        response = requests.get(config['url_friend_user'], params=args, auth=auth, stream=True)
        detail = response.json()
        friend_ids, friend_names = detail['ids'], []
        for friend_id in friend_ids:
            Dict = get_information(friend_id, None, config)
            if Dict != None:  # and Dict['screen_name'] not in recorded_set:
                friend_names.append(Dict['screen_name'])
    except:
        sys.stderr.write("fail to get the friends of: {0}\n".format(screen_name))
        return []
    else:
        sys.stderr.write('we have finish get the friends of %s\n' % (screen_name))
        sleep(config['wait'] / 2)
        return friend_names




def get_tweets(screen_name, config, fd_out, output_format = 'txt'):
    # the token to enter the twitter
    token = random.choice([config['token_1'], config['token_2'], config['token_3'], config['token_4']])
    auth = OAuth1(token['consumer_key'], token['consumer_secret'], token['oauth_token'], token['oauth_secret'])
    ''' -- start -- '''
    sys.stderr.write("retrieving tweets for screen name: {0}\n".format(screen_name))
    # set the name of output file
    file_name = str(screen_name) + "." + output_format
    output_file = os.path.join(fd_out, file_name)
    # clean the output file
    if os.path.exists(output_file):  # with open('test.txt', "w", encoding='UTF-8') as file:
        os.remove(output_file)  # file.truncate()

    ''' --- get the tweets of user: screen_name --- '''
    # parameters of the request, four of which are fixed and one change for more tweets
    args = {
        'include_entities': 'true',
        'include_rts': 'true',
        'screen_name': screen_name,
        'count': config['tweets_count'], }
    iters, retrieved = 0, 0
    max_id, new_tweets = None, [" ", ]
    # tweets come from the most recent to the oldest, thus at each iteration, we update max_id
    while len(new_tweets) > 0 and retrieved < config["max_amount"]:
        args['max_id'] = max_id
        response = requests.get(config['url_user'], params=args, auth=auth, stream=True)
        new_tweets = response.json()  # new_tweets = get_tweets(auth, screen_name, config, max_id)
        for i, tweet in enumerate(new_tweets):
            if type(tweet) == 'str':  tweet = eval(tweet)
            elif type(tweet) == 'json': tweet = json.loads(tweet)
            success, last_id = writeFile(tweet, output_file, )
            if success == True and last_id != None:
                max_id = last_id - 1
                retrieved += 1
        iters += 1
        print("%s: , we have finished the %d-th batch, %d tweets have been downloaded, wait %ds to start the next one..." % (str(screen_name), iters, retrieved, config['wait']))
        sleep(config['wait'])
        if retrieved < iters * config['tweets_count'] * 0.35:
            break
    print("finish download %s's tweets, target amount is %d, achieve %d." % (str(screen_name), config['max_amount'], retrieved))



# def get_net_tweets(screen_name, user_stack, config, fd_out, pf_out,):
#     recorded_set = set([str(f).split('.txt')[0] for f in os.listdir(fd_out)])
#     if screen_name not in recorded_set:
#         ''' get the information and tweets of his friend '''
#         Dict = get_information(None, screen_name, config)
#         writeProfile(Dict, pf_out)  # write the profile of this user
#         get_tweets(screen_name, config, fd_out)
#
#                 # writeProfile(Dict, pf_out)
#     # print('get_net_tweets', len(user_stack), user_stack)

def get_oneuser_tweets(screen_name, config, fd_out, pf_out):
    if not os.path.exists(fd_out):
        os.makedirs(fd_out)
    if not os.path.exists(pf_out):
        os.makedirs(pf_out)
    try:
        Dict = get_information(None, screen_name, config)
        writeProfile(Dict, pf_out)  # write the profile of this user
        get_tweets(screen_name, config, fd_out)
    except:
        sys.stderr.write("error responds for user %s.\n"%(screen_name))

