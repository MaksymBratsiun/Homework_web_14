import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.model import Contact, User
from src.repository.users import (get_user_by_email,
                                  create_user,
                                  update_token,
                                  update_avatar,
                                  confirmed_email)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, username='Test', email='example@ex.ua')

    async def test_user_by_email(self):
        pass


