
from twitter_cookbook.twitter_request import make_twitter_request
from sys import maxsize as maxint
from profile import Profile
import sys


class Friends:
    def __init__(self, *args, **kwargs):
        """gets reciprocal friends/followers and returns their ids back to Crawl

        Args:
            api: (api object) twitter authenticated api object
            screen_name: (str) twitter screen name
            user_id: (int) twitter user id
            friends_ids: (list) of friends ids
            followers_ids: (list) of followers ids
            friends_limit: (int) maximum amount of friend ids to get
            followers_limit: (int) maximum amount of follower ids to get
        """
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.twitter_api = self.kwargs.get('twitter_api')
        self.screen_name = self.kwargs.get('screen_name', None)
        self.user_id = self.kwargs.get('user_id', None)
        self.friends_ids = []
        self.followers_ids = []
        self.friends_limit = 5000
        self.followers_limit = 5000
        self.found_reciprocal = False
        self.reciprocal_friends_count = 0
        self.friends_cursor = -1
        self.follower_cursor = -1
        self.no_response = False

    def get_friends_followers_ids(self, _user_id=None):
        """use twitter friend.ids/follower.ids api to get friend/follower ids

        Args:
            _user_id: (int) optional argument passed from caller--not class object

        Returns: (tuple) of two friend and follower lists

        """
        # Must have either screen_name or user_id (logical xor)
        assert (self.screen_name != None) != (self.user_id != None), \
            "Must have screen_name or user_id, but not both"

        while not self.found_reciprocal and (self.friends_cursor != 0 or self.follower_cursor != 0):  # loop until 5 or more reciprocal friends are found

            # get friends/follower ids in two sequential for loops to check for reciprocal friends after each batch of
            # 5000 friends/follower ids  TODO: generalize this into a function i.e get_ids(api) -> id_list
            for ids, label in [[self.friends_ids, 'friends']]:  # using for loop to encapsulate variable scope
                if self.friends_cursor == 0:  # break out of loop if there are no more friends
                    break
                if self.screen_name:
                    response = make_twitter_request(self.twitter_api.friends.ids, count=5000,
                                                    screen_name=self.screen_name, cursor=self.friends_cursor)
                elif not self.user_id and _user_id:  # _user_id passed as argument to function not class constructor
                    response = make_twitter_request(self.twitter_api.friends.ids, count=5000,
                                                    user_id=_user_id, cursor=self.friends_cursor)
                else:  # user_id
                    response = response = make_twitter_request(self.twitter_api.friends.ids, count=5000,
                                                    user_id=self.user_id, cursor=self.friends_cursor)

                if response is not None:
                    self.friends_ids += response['ids']  # append returned friend ids
                    self.friends_cursor = response['next_cursor']  # points the cursor to the next page of results
                else:
                    print('No response')
                    break
                print(f"Got {len(response['ids'])} total {label} ids for {self.screen_name or self.user_id}")
                break  # don't need break here?

            # get_follower ids
            for ids, label in [[self.followers_ids, 'followers']]:  # using for loop to encapsulate variable scope
                if self.follower_cursor == 0:  # break out of loop if there are no more followers
                    break
                if self.screen_name:
                    response = make_twitter_request(self.twitter_api.followers.ids, count=5000,
                                                    screen_name=self.screen_name, cursor=self.follower_cursor)
                elif not self.user_id and _user_id:  # _user_id passed as argument to function not class constructor
                    response = make_twitter_request(self.twitter_api.followers.ids, count=5000,
                                                    user_id=_user_id, cursor=self.follower_cursor)
                else:  # user_id
                    response = response = make_twitter_request(self.twitter_api.followers.ids, count=5000,
                                                               user_id=self.user_id, cursor=self.follower_cursor)

                if response is not None:
                    # ids += response['ids']
                    self.followers_ids += response['ids']  # append returned follower ids
                    self.follower_cursor = response['next_cursor']  # points the cursor to the next page of results
                else:
                    self.no_response = True  # possible 401 error for protected account
                    print('No response')
                    break
                print(f"Got {len(response['ids'])} total {label} ids for {self.screen_name or self.user_id}")
                # check for reciprocal friends

            self.found_reciprocal = self._check_reciprocal()

        return self.friends_ids[:maxint], self.followers_ids[:maxint]

    def _check_reciprocal(self):
        """gets set intersection (reciprocal friends) of friends and follower lists

        Returns: (boolean) returns True if reciprocal friends are found or if no friends were returned
        """
        self.reciprocal_friends = list(set(self.friends_ids) & set(self.followers_ids))
        if len(self.reciprocal_friends) >= 5:
            self._get_top_friends()
            return True
        elif len(self.friends_ids) > self.friends_limit or len(self.followers_ids) > self.friends_limit:
            print(f"Maximum friends/followers count of {self.friends_limit} reached. No reciprocal friends found for {self.user_id}")
            return True  # causes while loop to end and send emtpy reciprocal friend list back to caller
        elif self.friends_cursor == 0 or self.follower_cursor == 0:
            print(f"No reciprocal friends found for {self.screen_name or self.user_id}, and cursor is 0")
            return True
        elif self.no_response:
            return True
        else:
            print(f"No reciprocal friends found for {self.screen_name or self.user_id}, getting more friends and followers")
        return False

    def _get_top_friends(self):
        """creates Profile object and calls its get_top_friends method to get the sorted top 5 ids by followers_count

        Returns: (list) of top 5 follower ids

        """
        self.top_reciprocal_friends = Profile(twitter_api=self.twitter_api, user_ids=self.reciprocal_friends).get_top_friends()
