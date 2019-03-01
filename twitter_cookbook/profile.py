from twitter_request import make_twitter_request

"""
code derived from Mining the Social Web, 3rd Edition (Mikhail Klassen, Matthew A. Russell)

"""

class Profile(object):
    def __init__(self, *args, **kwargs):
        """get profile information about a list of user_names or user_ids.

        Args:
            twitter_api: (api object) authenticated twitter api
            screen_names: (str) comma separated string names
            user_ids: (str) comma separated ids
            follower_count: (dict) key = user_id/screen_name, value = follower_count

        Returns: 'unordered' json array
        """
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.twitter_api = self.kwargs.get('twitter_api', None)
        self.screen_names = self.kwargs.get('screen_names', None)
        self.user_ids = self.kwargs.get('user_ids', None)
        self.items_to_info = None
        self.follower_count = {}
        if self.kwargs.get('get_names', None):
            self.get_screen_name()
        else:
            self.get_user_profile()

    def get_user_profile(self):
        # Must have either screen_name or user_id (logical xor)
        assert (self.screen_names != None) != (self.user_ids != None), \
            "Must have screen_names or user_ids, but not both"

        self.items_to_info = {}

        items = self.screen_names or self.user_ids

        while len(items) > 0:

            # Process 100 items at a time per the API specifications for /users/lookup.
            # See http://bit.ly/2Gcjfzr for details.

            items_str = ','.join([str(item) for item in items[:100]])
            items = items[100:]

            if self.screen_names:
                response = make_twitter_request(self.twitter_api.users.lookup,
                                                screen_name=items_str)
            else:  # user_ids
                response = make_twitter_request(self.twitter_api.users.lookup,
                                                user_id=items_str)

            for user_info in response:
                if self.screen_names:
                    self.items_to_info[user_info['screen_name']] = user_info
                else:  # user_ids
                    self.items_to_info[user_info['id']] = user_info

        return self.items_to_info

    def get_top_friends(self, iterable=None, key='followers_count', n=5):
        """sorts reciporcal friends by followers_count

        Args:
            iterable: (collection)
            key: (str) key to sort collection
            n: (int) number of items to return

        Returns: top n friends

        """
        assert (self.screen_names != None) != (self.user_ids != None), \
            "Must have screen_names or user_ids, but not both"

        if iterable is None:
            sorted_items = sorted(self.items_to_info.items(), key=lambda x: (x[1][key]), reverse=True)
            sorted_reciprocal_friends = [x[0] for x in sorted_items]
            # for x in sorted_items:
            #     print(x[0], x[1].get('followers_count'))
            return sorted_reciprocal_friends[:5]
        else:
            sorted_items = sorted(iterable.items(), key=lambda x: (x[1][key]), reverse=True)
            sorted_reciprocal_friends = [x[0] for x in sorted_items]
            # for x in sorted_items:
            #     print(x[0], x[1].get('followers_count'))
            return sorted_reciprocal_friends[:5]

    def get_screen_name(self):
        id_name = {}
        ids = ','.join(str(id) for id in self.user_ids)
        response = make_twitter_request(self.twitter_api.users.lookup, user_id=ids)
        for user_info in response:
            id_name[user_info['id']] = user_info['screen_name']

        return id_name

