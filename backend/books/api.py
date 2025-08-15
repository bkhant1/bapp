from datetime import datetime
from typing import List

from ninja import Router
from pydantic import BaseModel

router = Router()


# Basic schemas - we'll expand these later
class BookSchema(BaseModel):
    id: int
    title: str
    author_names: str
    isbn_13: str
    publication_date: datetime = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response=List[BookSchema])
def list_books(request):
    """List all books"""
    from .models import Book

    return Book.objects.all()[:20]


@router.get("/{book_id}", response=BookSchema)
def get_book(request, book_id: int):
    """Get book by ID"""
    from django.shortcuts import get_object_or_404

    from .models import Book

    book = get_object_or_404(Book, id=book_id)
    return book
