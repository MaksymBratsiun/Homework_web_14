from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.model import Contact


async def get_contacts(current_user: int, limit: int, offset: int, db: Session):
    """
    The get_contacts function returns a list of contacts for the current user.
        Args:
            current_user (int): The id of the user whose contacts are being retrieved.
            limit (int): The number of results to return per page. Defaults to 10 if not specified by client request.
            offset (int): The number of results to skip before returning any data, used for pagination purposes.
            Defaults to 0 if not specified by client request.

    :param current_user: int: Get the contacts of a specific user
    :param limit: int: Limit the number of results returned
    :param offset: int: Determine the number of contacts to skip
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=current_user).limit(limit).offset(offset).all()
    return contacts


async def create_contact(body, current_user: int, db: Session):
    """
    The create_contact function creates a new contact in the database.
        Args:
            body (ContactCreate): The contact to create.
            current_user (int): The user id of the currently logged-in user.

    :param body: Get the data from the request body
    :param current_user: int: Get the user id of the current logged in user
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.email == body.email, Contact.user_id == current_user)).first()
    if not contact:
        contact = Contact(**body.dict())
        contact.user_id = current_user
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


async def get_contact_by_id(contact_id: int, current_user: int, db: Session):
    """
    The get_contact_by_id function returns a contact by its id.
        Args:
            contact_id (int): The id of the contact to be returned.
            current_user (int): The user who is making the request for a specific contact. This is used to ensure that
            only contacts belonging to this user are returned, and not those belonging to other users
            in the database.
            db (Session): A connection with an open session with our database, which will allow us access
            and manipulation of data within it.

    :param contact_id: int: Identify the contact to be retrieved
    :param current_user: int: Get the current user id from the token
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user)).first()
    return contact


async def update_contact(body, contact, db: Session):
    """
    The update_contact function updates a contact in the database.
        Args:
            body (Contact): The updated contact object to be stored in the database.
            db (Session): A connection to the SQLite3 database.

    :param body: Get the data from the request
    :param contact: Get the contact from the database
    :param db: Session: Access the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone = body.phone
    contact.born_date = body.born_date
    contact.add_data = body.add_data
    db.commit()
    return contact


async def remove_contact(contact, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact (Contact): The Contact object to be removed from the database.
            db (Session): The SQLAlchemy Session object that will be used to remove the Contact object.

    :param contact: Pass the contact object to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    db.delete(contact)
    db.commit()
    return contact


async def get_search(find_item: str, current_user: int, db: Session):
    """
    The get_search function takes in a string, the current user's id, and the database session.
    It then searches for contacts that match the search string in their first name, last name or email.
    The results are returned as a list of Contact objects.

    :param find_item: str: Search for a contact in the database
    :param current_user: int: Get the user id of the current user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts that match the search criteria
    :doc-author: Trelent
    """
    result = []
    if find_item:
        contacts_f_name = db.query(Contact).filter(and_(Contact.user_id == current_user,
                                                        Contact.first_name.like(f'%{find_item}%'))).all()
        if contacts_f_name:
            result.extend(contacts_f_name)

        contacts_l_name = db.query(Contact).filter(and_(Contact.user_id == current_user,
                                                        Contact.last_name.like(f'%{find_item}%'))).all()
        if contacts_l_name:
            result.extend(contacts_l_name)

        contacts_email = db.query(Contact).filter(and_(Contact.user_id == current_user,
                                                       Contact.email.like(f'%{find_item}%'))).all()
        if contacts_email:
            result.extend(contacts_email)
        result = list(set(result))
    return result


async def birthday_7(current_user: int, db: Session):
    """
    The birthday_7 function returns a list of contacts whose birthday is within the next 7 days.
        Args:
            current_user (int): The id of the user who's contacts are being searched.
            db (Session): A database session object to query for data.

    :param current_user: int: Specify the user id of the current user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthdays are in the next 7 days
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user_id=current_user).all()
    result = []
    today = datetime.now()
    for contact in contacts:
        if contact.born_date.month > today.month:
            contact_birthday = datetime(year=today.year, month=contact.born_date.month, day=contact.born_date.day)
        elif contact.born_date.month < today.month:
            contact_birthday = datetime(year=today.year+1, month=contact.born_date.month, day=contact.born_date.day)
        else:
            if contact.born_date.day > today.day:
                contact_birthday = datetime(year=today.year, month=contact.born_date.month, day=contact.born_date.day)
            else:
                contact_birthday = datetime(year=today.year+1, month=contact.born_date.month, day=contact.born_date.day)
        delta = contact_birthday - today
        if delta <= timedelta(days=7):
            result.append(contact)
    return result
