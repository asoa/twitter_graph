from friends import Friends
from mongo import save_to_mongo
from profile import Profile
import json

"""
code derived from Mining the Social Web, 3rd Edition (Mikhail Klassen, Matthew A. Russell)

"""

class Crawl(object):
    def __init__(self, *args, **kwargs):
        """crawls a twitter graph starting from the root node and building a queue of reciprocal friends/followers
        i.e. root -> set(friend/followers) -> set(friend/followers) ... self.node.count

        Args:
            twitter_api: (twitter api) authenticated twitter api obj
            screen_name: (str) twitter screen name
            node_max: (int) maximum amount of nodes to crawl, default:100
            file_output: (file obj) file to write nodes to
            seed_id: (int) starting point of crawl
        """
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.twitter_api = self.kwargs.get('twitter_api', None)
        self.screen_name = self.kwargs.get('screen_name', None)
        self.node_count = 0
        self.node_max = self.kwargs.get('node_max', 100)
        self.seed_id = None
        self.queue = None
        self.next_queue = None
        self.follower_ids = None
        self.file_output = open(f'twitter_graph_{self.screen_name}.txt', 'w')
        self.node_list = []

    def crawl_followers(self, **mongo_conn_kw):
        # Resolve the ID for screen_name and start working with IDs for consistency
        # in storage

        self.seed_id = str(self.twitter_api.users.show(screen_name=self.screen_name)['id'])  # get the twitter id

        # gets friends and followers for specified user_id-> unpacks into _, next_queue
        friends, self.next_queue = Friends(twitter_api=self.twitter_api, user_id=self.seed_id).get_friends_followers_ids()
        self.next_queue = self.get_reciprocal_friends(friends, self.next_queue)  # add to the queue
        self.node_count += len(self.next_queue) + 1
        self.node_list = self.next_queue  # initialize with initial queue
        self.write_to_disk(self.seed_id, 'reciprocal', self.next_queue)  # write the root and reciprocal friends

        while self.node_count <= self.node_max:
            # set queue to next_queue and next_queue to empty list in preparation for another call to
            # get_friends_followers_ids()
            (self.queue, self.next_queue) = (self.next_queue, [])
            print(self.queue)
            for fid in self.queue:  # get the friends and followers for each id in the queue
                # variables returned from call to Friends.get_friends_followers_ids
                friend_ids, follower_ids = Friends(twitter_api=self.twitter_api, user_id=fid).get_friends_followers_ids()
                if len(friend_ids) == 0 or len(follower_ids) == 0:
                    continue
                reciprocal_friends = self.get_reciprocal_friends(friend_ids, follower_ids)  # returns top 5 sorted by followers_count
                if len(reciprocal_friends) == 0:
                    self.write_to_disk(fid, 'reciprocal', reciprocal_friends)
                    continue
                nodes_no_root = [node for node in reciprocal_friends if node != int(self.seed_id)]  # removes the root node if present to prevent recursion
                self.node_count += len([node for node in nodes_no_root if node not in self.node_list])  # increment count of nodes
                self.next_queue.extend(nodes_no_root)  # add to the queue
                self.node_list.extend(nodes_no_root)  # add to node list
                print("{} nodes added to the queue".format(len(nodes_no_root)))
                print(f"{self.node_count} total nodes")
                self.write_to_disk(fid, 'reciprocal', reciprocal_friends)  # writes all reciprocal friends--including root--if present
                if self.node_count > self.node_max:
                    break

    def get_reciprocal_friends(self, friend_ids, follower_ids):
        """sort reciprocal friends by popularity

        Args:
            friends: (list) of friends returned by call to Friends.get_friends_followers_ids()

        Returns: top 5 reciprocal friends
        """
        reciprocal_friends = list(set(friend_ids) & set(follower_ids))  # get intersection of two lists
        # get top 5 reciprocal friends by followers_count
        top_reciprocal_friends = Profile(twitter_api=self.twitter_api, user_ids=reciprocal_friends).get_top_friends()
        top_rfriends_no_recur = [id for id in top_reciprocal_friends if id != int(self.seed_id)]
        return top_rfriends_no_recur

    def write_to_disk(self, user_id, label, ids, screen_name=None):
        if screen_name:
            # writes a nested dict to file i.e. {'Russell Wilson: {'friends': [1,2,3]}
            self.file_output.write(json.dumps({screen_name: {label: ids}}))
            self.file_output.write("\n")

        else:
            self.file_output.write(json.dumps({user_id: {label: ids}}))
            self.file_output.write("\n")
