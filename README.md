# TwitterCrawler4Network

A crawler for twitter.  

The requirement can be a set of screen names or keywords, and the downloaded tweets can belong to the specified users, or their friends in the social networks.


## Running

The config file `config.yaml`contains all default values, which can be changed according to your own needs.  

Some important settings:  

config['crawl_way'] == 'net' and config['crawl_require'] == 'keywords': download the tweets of users who mentioned the keywords  

config['crawl_way'] == 'single' and config['crawl_require'] == 'users': download tweets of the specific users  

config['crawl_way'] == 'net' and config['crawl_require'] == 'users': download tweets of the specific users as well as their friends

## Reference

https://github.com/valeriobasile/twittercrawler.git


