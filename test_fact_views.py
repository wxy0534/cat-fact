"""Message View tests."""

# run these tests like:
# FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Fact, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///number_db-test"

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class FactViewTestCase(TestCase):
    """Test views for facts."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Fact.query.delete()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                    password="testuser")
                                    

        db.session.commit()

    def test_add_fact(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/facts/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Fact.query.one()
            self.assertEqual(msg.text, "Hello")
