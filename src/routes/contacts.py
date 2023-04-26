from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.model import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactResponse, ContactModel
from src.services import auth as auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse],
            name="Get contacts",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))]
            )
async def get_contacts(current_user: User = Depends(auth_service.get_current_user),
                       limit: int = Query(10, le=500),
                       offset: int = 0,
                       db: Session = Depends(get_db)):
    """
    The get_contacts function returns a list of contacts for the current user.

    :param current_user: User: Get the current user from the database
    :param limit: int: Limit the number of contacts returned
    :param le: Set a limit to the number of contacts that can be returned
    :param offset: int: Specify the number of records to skip before returning the results
    :param db: Session: Pass the database session to the repository layer
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(current_user.id, limit, offset, db)
    return contacts


@router.post("/", response_model=ContactResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))]
             )
async def create_contact(body: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
        It takes an email, first_name, last_name and phone number like input parameters.
        The function returns the newly created contact object.

    :param body: ContactModel: Get the request body of the post request
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository
    :return: A ContactModel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.create_contact(body, current_user.id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is exists")
    return contact


@router.get("/{contact_id}", response_model=ContactResponse,
            name="Get contact by id",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))]
            )
async def get_contact_by_id(contact_id: int = Path(ge=1),
                            current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    """
    The get_contact_by_id function is used to retrieve a contact by its id.
        The function will return the contact if it exists, otherwise it will raise an HTTPException
            with status code 404.

    :param contact_id: int: Specify the id of the contact to retrieve
    :param current_user: User: Get the user id from the current_user object
    :param db: Session: Get the database session
    :return: A contact object which is defined in the models
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse,
            name="Update contact by id",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))]
            )
async def update_contact_by_id(body: ContactModel, contact_id: int = Path(ge=1),
                               current_user: User = Depends(auth_service.get_current_user),
                               db: Session = Depends(get_db)):
    """
    The update_contact_by_id function updates a contact in the database.
        The function takes an id of a contact and returns the updated contact.
        If no such user exists, it raises an HTTPException with status code 404 (Not Found).

    :param body: ContactModel: Get the contact model from the request body
    :param contact_id: int: Get the contact id from the url
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone = body.phone
    contact.born_date = body.born_date
    contact.add_data = body.add_data
    db.commit()
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               name="Remove contact by id",
               dependencies=[Depends(RateLimiter(times=2, seconds=5))]
               )
async def remove_contact_by_id(contact_id: int = Path(ge=1),
                               current_user: User = Depends(auth_service.get_current_user),
                               db: Session = Depends(get_db)):
    """
    The remove_contact_by_id function removes a contact from the database.
        The function takes in an integer representing the id of the contact to be removed,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(contact)
    db.commit()
    return contact


@router.get("/search/{find_item}",
            response_model=List[ContactResponse],
            name="Find contact by first_name, last_name, email",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_search(find_item: str,
                     current_user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    """
    The get_search function is used to search for a contact in the database.
        The function takes in a string and returns all contacts that contain the string.
        If no contacts are found, an HTTP 404 error is returned.

    :param find_item: str: Search for a contact by name
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository
    :return: A list of contacts that match the search item
    :doc-author: Trelent
    """
    result = await repository_contacts.get_search(find_item, current_user.id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result


@router.get("/birthday/", response_model=List[ContactResponse],
            name="Birthday in 7 days",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def birthday_7(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The birthday_7 function returns a list of contacts with birthdays in the next 7 days.

    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of contacts whose birthday is within a week
    :doc-author: Trelent
    """
    result = await repository_contacts.birthday_7(current_user.id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result
