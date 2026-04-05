"""
services/customer_service.py
-----------------------------
Business logic for Customer operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.customer import Customer
from schemas.customer import CustomerCreate


async def create_customer(db: AsyncSession, payload: CustomerCreate) -> Customer:
    """Persist a new customer and return it."""
    customer = Customer(name=payload.name, email=payload.email)
    db.add(customer)
    await db.flush()
    await db.refresh(customer)
    return customer


async def get_customer_by_email(db: AsyncSession, email: str) -> Customer | None:
    """Return the customer with the given email, or None."""
    result = await db.execute(select(Customer).where(Customer.email == email))
    return result.scalars().first()


async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Customer | None:
    """Return a customer by primary key, or None."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    return result.scalars().first()


async def get_or_create_customer(
    db: AsyncSession, name: str, email: str
) -> tuple[Customer, bool]:
    """
    Look up a customer by email; create one if they don't exist.
    Returns (customer, created) where `created` is True for new records.
    """
    customer = await get_customer_by_email(db, email)
    if customer:
        return customer, False
    customer = await create_customer(db, CustomerCreate(name=name, email=email))
    return customer, True
