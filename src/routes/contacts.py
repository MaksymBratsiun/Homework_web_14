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
    contacts = await repository_contacts.get_contacts(current_user.id, limit, offset, db)
    return contacts


@router.post("/", response_model=ContactResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))]
             )
async def create_contact(body: ContactModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
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
    result = await repository_contacts.get_search(find_item, current_user.id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result


@router.get("/birthday/", response_model=List[ContactResponse],
            name="Birthday in 7 days",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def birthday_7(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    result = await repository_contacts.birthday_7(current_user.id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return result
