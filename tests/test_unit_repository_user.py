import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.model import User
from src.repository.users import (get_user_by_email,
                                  create_user,
                                  update_token,
                                  update_avatar,
                                  confirmed_email)
from src.schemas import  UserModel


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, username='Test', email='example@ex.ua')

    async def test_get_user_by_email(self):
        self.session.query(User).filter_by().first.return_value = self.user
        result = await get_user_by_email('example', self.session)
        self.assertEqual(result.email, self.user.email)

    async def test_create_user(self):
        body = UserModel(
            username='Test',
            email='example@ex.ua',
            password='qwerty'
        )
        g = Gravatar(body.email)
        result = await create_user(body, self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, g.get_image())
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_avatar(self):
        self.session.query(User).filter_by().first.return_value = self.user
        new_url = 'http://new_avatar_url'
        result = await update_avatar('example@ex.ua', new_url, self.session)
        self.assertEqual(result.avatar, new_url)

