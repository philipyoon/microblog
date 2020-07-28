from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelTest(unittest.TestCase):
    # Python unittest allows you to define setUp() and tearDown() methods which gets performed before and after each test method
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # using 'sqlite://' creates a new in-memory SQLite database, not existing database
        db.create_all()  # create all database table
    def tearDown(self):
        db.session.remove()  # in config.py SQLALCHEMY_COMMIT_ON_TEARDOWN is set to True, so if not for calling this function changes would be auto-committed
        db.drop_all()

    def test_password_hashing(self):
        philip = User(username='philip')
        philip.set_password('angel')
        self.assertFalse(philip.check_password('dog'))  # check to make sure wrong password is checked correctly
        self.assertTrue(philip.check_password('angel'))  # check to make sure correct password is checked correctly

    def test_follow(self):
        john = User(username='john', email='john@email.com')
        peter = User(username='peter', email='peter@email.com')
        db.session.add(john)
        db.session.add(peter)
        db.session.commit()
        self.assertEqual(john.followed.all(), [])  # check that john isn't following anyone
        self.assertEqual(john.followers.all(), [])  # check that john doesn't have any followers

        # check following works
        john.follow(peter)
        db.session.commit()
        self.assertTrue(john.is_following(peter))
        self.assertEqual(john.followed.count(), 1)
        self.assertEqual(john.followed.first().username, 'peter')
        self.assertEqual(peter.followers.count(), 1)
        self.assertEqual(peter.followers.first().username, 'john')

        # check unfollowing works
        john.unfollow(peter)
        db.session.commit()
        self.assertFalse(john.is_following(peter))
        self.assertEqual(john.followed.count(), 0)
        self.assertEqual(peter.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@email.com')
        u2 = User(username='susan', email='susan@email.com')
        u3 = User(username='mary', email='mary@email.com')
        u4 = User(username='david', email='david@email.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))  # post from john with time now + 1 second
        p2 = Post(body="post from susan", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup following
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])  # check to see john's followed posts includes susan's, david's, and his own
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)  # runs all tests
