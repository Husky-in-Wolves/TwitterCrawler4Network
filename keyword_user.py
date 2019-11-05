import requests, json, random, numpy
from requests_oauthlib import OAuth1


def byte2dict2screen_name(line):
    global false, null, true
    false = null = true = ""
    try:
        s = str(line, encoding = "UTF-8")
        d = eval(s)
        screen_name = d['user']['screen_name']
    except:
        return None
    else:
        return screen_name

def list2dict(screen_name):
    global NUM, user_id_D, user_num_D
    if not screen_name in user_id_D.keys():
        user_id_D[screen_name] = NUM
        user_num_D[NUM] = 0
        NUM += 1
    user_num_D[NUM] += 1
    return user_id_D[screen_name]


def get_keywords_userList(keywords, config):
    # the token to enter the twitter
    token = random.choice([config['token_1'], config['token_2'], config['token_3'], config['token_4']])
    auth = OAuth1(token['consumer_key'], token['consumer_secret'], token['oauth_token'], token['oauth_secret'])
    # POST data: list of keywords to search
    data = {'track':keywords, "language":config['language'], 'tweet_mode': 'extended'}
    response = requests.post(config['url_filter'], data=data, auth=auth, stream=True)
    # get relative users
    screen_name_list = map(lambda line: byte2dict2screen_name(line), response.iter_lines())
    print('finish map')
    screen_name_list = filter(lambda screen_name: screen_name != None, screen_name_list)
    print('finish filter')

    L, D = [], {}
    for i, screen_name in enumerate(screen_name_list):
        if not screen_name in D.keys():
            D[screen_name] = 0
        D[screen_name] += 1
        L.append(screen_name)

        if len(L) >= 25:
            string = str("\t\t".join(L))
            with open('users.txt', 'a', encoding='UTF-8') as file:
                file.write(string + '\n')
            print(len(D), string)
            L = []


