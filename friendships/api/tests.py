from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.rayz = self.create_user('rayz')
        self.rayz_client = APIClient()
        self.rayz_client.force_authenticate(self.rayz)

        self.mit = self.create_user('mit')
        self.mit_client = APIClient()
        self.mit_client.force_authenticate(self.mit)

        # create followings and followers for mit
        for i in range(2):
            follower = self.create_user('rayz_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.rayz)

        for i in range(3):
            following = self.create_user('rayz_following{}'.format(i))
            Friendship.objects.create(from_user=self.rayz, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.mit.id)

        # need user authentication to follow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # use get to follow
        response = self.rayz_client.get(url)
        self.assertEqual(response.status_code, 405)

        # check follow self
        response = self.mit_client.post(url)
        self.assertEqual(response.status_code, 400)

        # follow successful
        response = self.rayz_client.post(url)
        self.assertEqual(response.status_code, 201)

        # repeat follow successful
        response = self.rayz_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        count = Friendship.objects.count()
        response = self.mit_client.post(FOLLOW_URL.format(self.rayz.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.mit.id)

        # need authenticate to unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # check unfollow with get
        response = self.rayz_client.get(url)
        self.assertEqual(response.status_code, 405)

        # cannot unfollow self
        response = self.mit_client.post(url)
        self.assertEqual(response.status_code, 400)

        #unfollow successful
        Friendship.objects.create(from_user=self.rayz, to_user=self.mit)
        count = Friendship.objects.count()
        response = self.rayz_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # not follow and follow
        count = Friendship.objects.count()
        response = self.rayz_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.rayz.id)

        #post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        #get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        #check the order -> make sure its reverse
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'rayz_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'rayz_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'rayz_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.rayz.id)

        #post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get should be fine
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']),2)

        # 确保按照时间倒序
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'rayz_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'rayz_follower0',
        )








