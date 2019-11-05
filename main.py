import yaml, os, multiprocessing
from requests_oauthlib import OAuth1
from time import sleep
import random, math, numpy
from keyword_user import get_keywords_userList
from user_tweets import get_oneuser_tweets, get_friends


os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'https://127.0.0.1:1080'

# the predefined parameter
with open('config.yaml') as fd_conf:
    config = yaml.load(fd_conf, Loader=yaml.SafeLoader)
# the token to enter the twitter
token = random.choice([config['token_1'], config['token_2'], config['token_3'], config['token_4']])
auth = OAuth1(token['consumer_key'], token['consumer_secret'], token['oauth_token'], token['oauth_secret'])

''' the path for output '''
if not os.path.exists(config['fd_out']):
    os.makedirs(config['fd_out'])
if not os.path.exists(config['pf_out']):
    os.makedirs(config['pf_out'])



if __name__ == '__main__':
    pool = multiprocessing.Pool(3)  # only can be runned under if __name__ == '__main__'

    # if config['crawl_way'] == 'single' and config['crawl_require'] == 'keywords'  and len(config['keywords']) > 0:
    #     ''' config['crawl_way'] == 'single' and config['crawl_require'] == 'keywords': only download the relative tweets '''

    if config['crawl_way'] == 'net' and config['crawl_require'] == 'keywords' and len(config['keywords']) > 0:
        ''' if config['crawl_way'] == 'net' and config['crawl_require'] == 'keywords': download the relative users' tweets '''
        # get the relative users and record them into file: 'users.txt'
        get_keywords_userList(config['keywords'], config)
        users = {}
        with open('users.txt', 'r', encoding='UTF-8', errors='ignore') as file:
            for line in file.readlines():
                list_ = line.strip('\n').strip('\t').split('\t\t')
                if len(list_) != 25:
                    continue
                for screen_name in list_:
                    if screen_name not in users.keys():
                        users[screen_name] = 0
                    users[screen_name] += 1
        if len(users):
            # pick out the users who mention keywords many times
            avg = math.ceil(numpy.average(list(users.values())))
            user_Dict = dict(filter(lambda i: i[-1] >= avg, users.items()))
            print(avg, len(user_Dict))
            # according to the keywords to get the relative users
            recorded_set = [str(f).split('.txt')[0] for f in os.listdir("OUTPUT-keywords/")]
            for screen_name in set(user_Dict.keys()) - set(recorded_set):
                if not os.path.exists("OUTPUT-keywords/" + str(screen_name) + ".txt"):
                    pool.apply_async(get_oneuser_tweets, (screen_name, config, "OUTPUT-keywords/", 'Profile-keywords/'))
                    sleep(3)
            pool.close()
            pool.join()

    elif config['crawl_way'] == 'single' and config['crawl_require'] == 'users' and len(config['users']) > 0:
        ''' if config['crawl_way'] == 'single' and config['crawl_require'] == 'users': download tweets of the specific users '''
        for screen_name in config['users']:
            recorded_set = set([str(f).split('.txt')[0] for f in os.listdir(config['fd_out'])])
            # get info and tweets of user (parallel)
            if screen_name not in recorded_set:
                pool.apply_async(get_oneuser_tweets, (screen_name, config, config['fd_out'], config['pf_out']))
                sleep(3)
        pool.close()
        pool.join()

    elif config['crawl_way'] == 'net' and config['crawl_require'] == 'users' and len(config['users']) > 0:
        ''' if config['crawl_way'] == 'net' and config['crawl_require'] == 'users': download tweets of the specific users as well as their friends '''
        user_stack = list(config['users']).copy()
        while len(user_stack) > 0:
            # get the target user by the rule of stack
            screen_name = user_stack[0]; user_stack.pop(0)
            recorded_set = set([str(f).split('.txt')[0] for f in os.listdir(config['fd_out'])])
            # get info and tweets of user (parallel)
            if screen_name not in recorded_set:
                pool.apply_async(get_oneuser_tweets, (screen_name, config, config['fd_out'], config['pf_out']))
                sleep(3)
            # add friends into stack (serial)
            friend_names = get_friends(screen_name, config)
            user_stack.extend(list(set(friend_names) - set(user_stack)))
        pool.close()
        pool.join()


