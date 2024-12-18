from fastapi import FastAPI,Path,Query,HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

class BookRequest(BaseModel):# This is the request model that the user will use to send data
    id: Optional[int] = Field(description= 'ID is not needed on create', default=None)  # id is optional when creating a new book
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int= Field(gt=1999,lt=2025)

    model_config = {
        "json_schema_extra":{
            "example":{
                "title": "A new book",
                "author": "John Doe",
                "description": "A new description for a book",
                "rating":3,
                "publishing-date":2023
            }
        }
    }

# Sample books
book1 = Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", description="A novel set in the 1920s that explores themes of wealth, love, and the American Dream.", rating=4,published_date=2022)
book2 = Book(id=2, title="1984", author="George Orwell", description="A dystopian novel that critiques totalitarianism and extreme political ideology.", rating=3,published_date=2021 )
book3 = Book(id=3, title="To Kill a Mockingbird", author="Harper Lee", description="A story of racial injustice and childhood in the Depression-era South.", rating=5,published_date=2020)
book4 = Book(id=4, title="The Catcher in the Rye", author="J.D. Salinger", description="A coming-of-age novel about a disillusioned teenager in New York City.", rating=2,published_date=2022)
book5 = Book(id=5, title="Moby-Dick", author="Herman Melville", description="The journey of the obsessive Captain Ahab as he hunts the elusive white whale, Moby Dick.", rating=5,published_date=2024)

BOOKS = [book1, book2, book3, book4, book5]

@app.get("/books",status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.get("/books/by_publishing_date/",status_code=status.HTTP_200_OK)
async def get_books_by_publishing_date(publishing_date:int=Query(gt=1999,lt=2025)):
    books_to_return=[]
    for book in BOOKS:
        if (book.published_date==publishing_date):
            books_to_return.append(book)

    return books_to_return

@app.get("/books/",status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int=Query(gt=-1, lt=6)):
    books_to_return=[]
    for book in BOOKS:
        if (book.rating==book_rating):
            books_to_return.append(book)

    return  books_to_return

@app.put("/books/update-book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed=False
    for i in range (len(BOOKS)):
        if (BOOKS[i].id == book.id):
            BOOKS[i]=book
            book_changed=True

    if not book_changed:
        raise HTTPException(status_code=404,detail="Book not found")


@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id :int=Path(gt=0)):
    book_changed=False
    for book in BOOKS:
        if(book.id==book_id):
            BOOKS.remove(book)
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=404,detail="Book not found")

@app.post("/create-book",status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_id = find_book_id()
    new_book = Book(id=new_id, **book_request.dict(exclude={"id"}))
    BOOKS.append(new_book)
    return new_book

def find_book_id():
    if len(BOOKS) > 0:
        return BOOKS[-1].id + 1
    return 1
