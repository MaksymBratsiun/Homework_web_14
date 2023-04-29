import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.model import Contact, User
from src.repository.contacts import (get_contacts,
                                     create_contact,
                                     get_contact_by_id,
                                     update_contact,
                                     remove_contact,
                                     get_search,
                                     birthday_7)
from src.schemas import ContactModel


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, username='Test', email='example@ex.ua')

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query(Contact).filter_by(user_id=self.user).limit().offset().all.return_value = contacts
        result = await get_contacts(self.user, 10, 0, self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactModel(
            first_name='Test',
            last_name='Test',
            email='example@test.ua',
            phone='+380991234567',
            born_date=datetime.now(),
            add_data='Test'
        )
        self.session.query(Contact) \
            .filter(and_(Contact.email == body.email, Contact.user_id == self.user.id)) \
            .first \
            .return_value = None
        result = await create_contact(body, self.user.id, self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.born_date, body.born_date)
        self.assertEqual(result.add_data, body.add_data)
        self.assertTrue(hasattr(result, 'id'))

    async def test_get_contact_by_id_found(self):
        contact = Contact()
        self.session.query(Contact) \
            .filter(and_(Contact.id == 1, Contact.user_id == self.user.id)) \
            .first.return_value = contact
        result = await get_contact_by_id(1, self.user.id, self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query(Contact) \
            .filter(and_(Contact.id == 1, Contact.user_id == self.user.id)) \
            .first.return_value = None
        result = await get_contact_by_id(1, self.user.id, self.session)
        self.assertIsNone(result)

    async def test_update_contact(self):
        contact = Contact(
            first_name='test',
            last_name='test',
            email='example@test.ua',
            phone='+380991234567',
            born_date=datetime.now(),
            add_data='Test'
        )
        body = ContactModel(
            first_name='TestUp',
            last_name='TestUp',
            email='example_up@test.ua',
            phone='+380997654321',
            born_date=datetime.now(),
            add_data='Test updated'
        )
        result = await update_contact(body, contact, self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.born_date, body.born_date)
        self.assertEqual(result.add_data, body.add_data)
        self.assertTrue(hasattr(result, 'id'))

    async def test_remove_contact(self):
        contact = Contact(id=1)
        self.session.query(Contact).filter(Contact.id == 1).first.return_value = contact
        result = await remove_contact(contact, self.session)
        self.assertEqual(result, contact)

    async def test_get_search_by_first_name(self):
        contacts = [Contact(first_name='test')]
        self.session.query(Contact).filter().all.return_value = contacts
        result = await get_search('es', self.user.id, self.session)
        self.assertTrue(result[0].first_name)
        self.assertEqual(result[0].first_name, contacts[0].first_name)

    async def test_get_search_by_last_name(self):
        contacts = [Contact(last_name='test')]
        self.session.query(Contact).filter().all.return_value = contacts
        result = await get_search('es', self.user.id, self.session)
        self.assertTrue(result[0].last_name)
        self.assertEqual(result[0].last_name, contacts[0].last_name)

    async def test_get_search_by_email(self):
        contacts = [Contact(email='test@test.com')]
        self.session.query(Contact).filter().all.return_value = contacts
        result = await get_search('es', self.user.id, self.session)
        self.assertTrue(result[0].email)
        self.assertEqual(result[0].email, contacts[0].email)

    async def test_birthday_7(self):
        born_date_test = datetime.now() - timedelta(days=363)
        contacts = [Contact(born_date=born_date_test)]
        self.session.query(Contact).filter_by().all.return_value = contacts
        result = await birthday_7(self.user.id, self.session)
        self.assertEqual(result, contacts)
