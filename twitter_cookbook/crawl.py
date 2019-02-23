from friends import Friends
from mongo import save_to_mongo
from profile import Profile
import json


class Crawl(object):
    def __init__(self, *args, **kwargs):
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.twitter_api = self.kwargs.get('twitter_api', None)
        self.screen_name = self.kwargs.get('screen_name', None)
        self.limit = self.kwargs.get('limit', 5000)
        self.nodes = 0
        # self.friend_obj = Friends(self.twitter_api, self.screen_name)
        self.seed_id = None
        self.queue = None
        self.next_queue = None
        self.follower_ids = None
        self.file_output = open('twitter_graph.txt', 'w')

    def crawl_followers(self, **mongo_conn_kw):
        # Resolve the ID for screen_name and start working with IDs for consistency
        # in storage

        self.seed_id = str(self.twitter_api.users.show(screen_name=self.screen_name)['id'])  # get the twitter id

        # gets friends and followers for specified user_id-> unpacks into _, next_queue
        friends, self.next_queue = Friends(twitter_api=self.twitter_api, user_id=self.seed_id).get_friends_followers_ids()
        self.next_queue = self.get_reciprocal_friends(friends, self.next_queue)  # set reciprocal friends value
        self.nodes += len(self.next_queue)

        self.write_to_disk(self.seed_id, 'reciprocal', self.next_queue)  # write the root and reciprocal friends

        while self.nodes < 100:
            # set queue to next_queue and next_queue to empty list in preparation for another call to
            # get_friends_followers_ids()
            (self.queue, self.next_queue) = (self.next_queue, [])
            for fid in self.queue:  # get the friends and followers for each id in the queue
                # variables returned from call to Friends.get_friends_followers_ids
                friend_ids, follower_ids = Friends(twitter_api=self.twitter_api, user_id=fid).get_friends_followers_ids()
                reciprocal_friends = self.get_reciprocal_friends(friend_ids, follower_ids)
                # sorted_reciprocal_friends = self.get_top_reciprocal_friends(reciprocal_friends)
                # TODO: create function to get screen_name and followers_count

                # Store a fid => follower_ids mapping in MongoDB

                # save_to_mongo({'followers': [_id for _id in follower_ids]},
                #               'followers_crawl', '{0}-follower_ids'.format(fid))

                # next_queue += follower_ids
                self.next_queue.extend(reciprocal_friends)
                self.nodes += len(reciprocal_friends)
                print("{} nodes added to the queue".format(self.nodes))
                if self.nodes > 100:
                    break
                self.write_to_disk(fid, 'reciprocal', reciprocal_friends)

    def get_reciprocal_friends(self, friend_ids, follower_ids):
        """sort reciprocal friends by popularity

        Args:
            friends: (list) of friends returned by call to Friends.get_friends_followers_ids()

        Returns: top n reciprocal friends
        """
        reciprocal_friends = list(set(friend_ids) & set(follower_ids))  # get intersection of two lists
        # get top 5 reciprocal friends by followers_count
        top_reciprocal_friends = Profile(twitter_api=self.twitter_api, user_ids=reciprocal_friends).get_top_friends()
        return top_reciprocal_friends

    def write_to_disk(self, user_id, label, ids, screen_name=None):
        if screen_name:
            # writes a nested dict to file i.e. {'Russell Wilson: {'friends': [1,2,3]}
            self.file_output.write(json.dumps({screen_name: {label: ids}}))
            self.file_output.write("\n")

        else:
            self.file_output.write(json.dumps({user_id: {label: ids}}))
            self.file_output.write("\n")
