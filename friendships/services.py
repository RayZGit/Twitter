from friendships.models import Friendship

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):

        friendships = Friendship.objects.filter(
            to_user=user
        ).prefetch_related('from_user')

        return [friendships.from_user for friendship in friendships]

