import sys
from functools import partial
from twitter_cookbook.twitter_request import make_twitter_request


# TODO: sort reciprocal friends by most popular (get the most robust graph)

class Friends:
    def __init__(self, *args, **kwargs):
        """
        Args:
            api: (api object) twitter authenticated api object
            name: (str)
            user_id: (int)
            friends_ids: (list)
            followers_ids:
            friends_limit:
            followers_limit: (int)
        """
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.twitter_api = self.kwargs.get('twitter_api')
        self.screen_name = self.kwargs.get('screen_name', None)
        self.user_id = self.kwargs.get('user_id', None)
        self.friends_ids = []
        self.followers_ids = []
        self.friends_limit = 5000
        self.followers_limit = 5000

    def get_friends_followers_ids(self, _user_id=None):
        """Given a twitter name or id, get her friend ids and followers id

        Returns: tuple of friends ids and followers ids

        """
        # Must have either screen_name or user_id (logical xor)
        assert (self.screen_name != None) != (self.user_id != None), \
            "Must have screen_name or user_id, but not both"

        # See http://bit.ly/2GcjKJP and http://bit.ly/2rFz90N for details
        # on API parameters

        get_friends_ids = partial(make_twitter_request, self.twitter_api.friends.ids, count=5000)
        get_followers_ids = partial(make_twitter_request, self.twitter_api.followers.ids, count=5000)

        # uses variable unpacking by iterating over the list of lists
        for partial_call, limit, ids, label in [
            [get_friends_ids, self.friends_limit, self.friends_ids, "friends"],
            [get_followers_ids, self.followers_limit, self.followers_ids, "followers"]
        ]:

            if limit == 0: continue

            cursor = -1  # initialy sets the cursor (page) to the first page
            while cursor != 0:  # loops until there aren't any more friends/followers to get

                # Use make_twitter_request via the partially bound callable...
                if self.screen_name:
                    response = partial_call(screen_name=self.screen_name, cursor=cursor)

                elif not self.user_id and _user_id:
                    response = partial_call(user_id=_user_id, cursor=cursor)
                else:  # user_id
                    response = partial_call(user_id=self.user_id, cursor=cursor)

                if response is not None:
                    ids += response['ids']  # append returned friend/follower ids
                    cursor = response['next_cursor']  # points the cursor to the next page of results

                print('Fetched {0} total {1} ids for {2}'.format(len(ids),
                        label, (self.user_id or self.screen_name)), file=sys.stderr)

                # XXX: You may want to store data during each iteration to provide an
                # an additional layer of protection from exceptional circumstances

                if len(ids) >= limit or response is None:  # if the ids returned for
                    break

        # Do something useful with the IDs, like store them to disk...
        return self.friends_ids[:self.friends_limit], self.followers_ids[:self.followers_limit]
