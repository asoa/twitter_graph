import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import json
import twitter
import authenticate

# TODO: create make_twitter decorater to wrap calls to this function
# TODO: create exception decorator using this tutorial: https://dzone.com/articles/python-how-to-create-an-exception-logging-decorato


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    """Code from Mining the Social Web, 3rd Edition by Matthew A. Russell; Mikhail Klassen

    Args:
        twitter_api_func: (api object)
        max_errors: (int) counter of errors to handle
        *args: positional arguments to function
        **kw: keyword arguments to function

    Returns: None

    """
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600:  # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e

        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes

        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429:
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60 * 15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e  # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds' \
                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5  # increase the wait period by 50%
            return wait_period  # return to caller ->  while True loop first except block
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:  # Continues to call the twitter api (twitter_api_func)
        try:
            return twitter_api_func(*args, **kw)  # make api call search/trends/friends.ids/followers.ids/etc.
        except twitter.api.TwitterHTTPError as e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)  # determines the wait period according to the exception handler
            if wait_period is None:  # if error is 401 (not authorized) or 404(not found) keep trying
                return  # returns to caller-->friends.get_friends_followers_ids
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise  # terminates execution
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise  # terminates execution

