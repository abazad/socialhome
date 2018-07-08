from ddt import data, ddt
from django.test import RequestFactory

from socialhome.content.forms import ContentForm
from socialhome.enums import Visibility
from socialhome.tests.utils import SocialhomeTestCase
from socialhome.users.tests.factories import UserFactory, ProfileFactory


@ddt
class TestContentForm(SocialhomeTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory()
        cls.profile = ProfileFactory(visibility=Visibility.PUBLIC, handle='profile1@example.com')
        cls.profile2 = ProfileFactory(visibility=Visibility.SITE, handle='profile2@example.com')
        cls.self_profile = ProfileFactory(visibility=Visibility.SELF, handle="self@example.com")

    def setUp(self):
        super().setUp()
        self.req = RequestFactory().get("/")
        self.req.user = self.user

    @data(
        ("profile1@example.com", True),
        ("profile1@example.com,profile2@example.com", True),
        ("profile1@example.com,foobar", False),
        ("self@example.com", False),
        ("foobar", False),
    )
    def test_clean__recipients(self, values):
        recipients, result = values
        form = ContentForm(
            data={"text": "barfoo", "visibility": Visibility.LIMITED.value, "recipients": recipients},
            user=self.user,
        )
        form.full_clean()
        self.assertTrue(form.is_valid() is result, values)

    def test_clean__recipients_and_include_following_cant_both_be_empty(self):
        form = ContentForm(data={"text": "barfoo", "visibility": Visibility.LIMITED.value}, user=self.user)
        form.full_clean()
        self.assertFalse(form.is_valid())

        form = ContentForm(
            data={"text": "barfoo", "visibility": Visibility.LIMITED.value, "recipients": self.user.profile.handle},
            user=self.user,
        )
        form.full_clean()
        self.assertTrue(form.is_valid())

        form = ContentForm(
            data={"text": "barfoo", "visibility": Visibility.LIMITED.value, "include_following": True},
            user=self.user,
        )
        form.full_clean()
        self.assertTrue(form.is_valid())

    @data(Visibility.SELF, Visibility.SITE, Visibility.PUBLIC)
    def test_clean__recipients_ignored_if_not_limited(self, visibility):
        form = ContentForm(
            data={"text": "barfoo", "visibility": visibility.value, "recipients": "foobar"},
            user=self.user,
        )
        form.full_clean()
        self.assertTrue(form.is_valid())
