from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.model import Contact


async def get_contacts(current_user: int, limit: int, offset: int, db: Session):
    contacts = db.query(Contact).filter_by(user_id=current_user).limit(limit).offset(offset).all()
    return contacts


async def create_contact(body, current_user: int, db: Session):
    contact = db.query(Contact).filter(and_(Contact.email == body.email, Contact.user_id == current_user)).first()
    if not contact:
        contact = Contact(**body.dict())
        contact.user_id = current_user
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


async def get_contact_by_id(contact_id: int, current_user: int, db: Session):
    print('before contact')
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user)).first()
    print('after contact')
    return contact


async def get_search(find_item: str, current_user: int, db: Session):
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
