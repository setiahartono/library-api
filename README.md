# Library API

## Overview

An API to do basic function of a library. This repository covers the API, admin page, fixture data and prepopulated database.

## How to run

### Using Virtual Environment

1.  Install the dependencies by either using pip or pipenv. Virtual Environment is optional, but recommended.

2. The database should be prepopulated, but if you want to start fresh you can follow step 3 to 5

3.  Make migration by running `python manage.py makemigrations` and run the migration by `python manage.py migrate`, by default the database will get connected to sqlite3.

4. Create superuser to access admin page (optional) `python manage.py createsuperuser`

5. Load fixture data (optional) (https://docs.djangoproject.com/en/4.2/howto/initial-data/)

6. Run the server `python manage.py runserver`


## PREPOPULATED USERS
When using prepopulated database, you may use the credentials below for authentication purposes.

```
--- Librarian ---
Username: librarian
password: password123!

--- Student ---
Username: student01
password: password123!

Username: student02
password: password123!

```

## ADMIN PAGE
You can login to admin page on `<URL>/admin`. You can use the librarian user from prepopulated user above

### Books

Most of the endpoints are protected by token authorization which can be acquired through admin page or by visiting `<URL>/auth/token/login` and input credentials above

- Show Book List: `GET /api/books/`
    - Description:
        - Show a list of book data
        - Page size can be configured in Django config
        - Show available book count and earliest date book return if the book is not available
    - Parameters
        - page: for pagination purpose
    - Response (200)  
        ```json
        {
            "count": 3,
            "next": null,
            "previous": null,
            "results": [
                {
                "title": "Book A",
                "author": "Author A",
                "available_stock": 10,
                "description": "Book A Description",
                "earliest_return_date": "-"
                },
                {
                "title": "Book B",
                "author": "Author B",
                "available_stock": 10,
                "description": "Book B Description",
                "earliest_return_date": "-"
                },
                {
                "title": "Book C",
                "author": "Author C",
                "available_stock": 1,
                "description": "Book C Description",
                "earliest_return_date": "-"
                }
            ]
        }
        ```
    - cURL Import
        ```cURL
        curl  -X GET \
            '<URL>/api/books' \
            --header 'Accept: */*' \
            --header 'Content-Type: application/json'
        ```

- Show Loan Info: `GET /api/loans`
    - Description:
        - Shows unreturned books along with the deadline for student user
        - Librarians can see all loans data
    - Parameters
        - page: for pagination purpose
    - Response (200)  
        ```json
        {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
            "loan_detail_id": 38,
            "book_info": "Book B by Author B",
            "book": 2,
            "is_returned": false,
            "extension_requested_at": "2023-08-18",
            "expected_return_date": "2023-09-17"
            },
            {
            "loan_detail_id": 39,
            "book_info": "Book A by Author A",
            "book": 1,
            "is_returned": false,
            "extension_requested_at": null,
            "expected_return_date": "2023-09-17"
            }
        ]
        }
        ```
    - cURL Import
        ```cURL
        curl  -X GET \
            '<URL>/api/loans' \
            --header 'Accept: */*' \
            --header 'Content-Type: application/json' \
            --header 'Authorization: Token <YOUR_TOKEN>' \
        ```

- Make a new loan: `POST /api/loans`
    - Description:
        - Create a new book loan data
        - Only librarian can use this endpoint
        - `loaner` represents the user id of the loaner
        - `book` represents the book id (can be seen in `GET /api/books`)
    - Request
        ```
        {
        "loan_details": [
                {
                    "book": 1
                },
                {
                    "book": 2
                }
           ]
        }
        ```
    - Response (201)  
        ```json
        {"message": "Loan is successful"}
        ```
    - cURL Import
        ```cURL
        curl  -X POST \
        '<URL>/api/loans' \
        --header 'Accept: */*' \
        --header 'Authorization: Token <YOUR_TOKEN>' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "loaner": 3,
            "loan_details": [
                {
                    "book": 1
                },
                {
                    "book": 2
                }
            ]
        }'
        ```

- Make a loan extension: `PUT /api/extensions/<loan_detail_id>`
    - Description:
        - Extend a book loan during first 30 days period
        - Can be used by student to extend loan
        - `loan_detail_id` represents an item/book to be extended
    - Response (200)  
        ```json
        {
            "extension_requested_at": "2023-08-18",
            "is_returned": false,
            "expected_return_date": "2023-09-17"
        }
        ```
    - cURL Import
        ```cURL
        curl  -X POST \
        '<URL>/api/extensions/<loan_detail_id>' \
        --header 'Accept: */*' \
        --header 'Authorization: Token <YOUR_TOKEN>' \
        --header 'Content-Type: application/json' \
        ```


- Show histories: `GET /api/histories`
    - Description:
        - Shows loan history of a user
        - Librarians can see all loan history
    - Parameters
        - page: for pagination purpose
    - Response (200)
        ```json
        {
            "count": 6,
            "next": null,
            "previous": null,
            "results": [
                {
                    "loaner": 2,
                    "loan_id": 29,
                    "loan_details": [
                        {
                        "loan_detail_id": 35,
                        "book_info": "Book A by Author A",
                        "book": 1,
                        "is_returned": true,
                        "extension_requested_at": null,
                        "expected_return_date": "2023-09-17"
                        }
                    ]
                },
                {
                    "loaner": 2,
                    "loan_id": 30,
                    "loan_details": [
                        {
                        "loan_detail_id": 36,
                        "book_info": "Book A by Author A",
                        "book": 1,
                        "is_returned": true,
                        "extension_requested_at": null,
                        "expected_return_date": "2023-09-17"
                        }
                    ]
                },
                .....
            ]
        }
        ```
    - cURL Import
        ```cURL
        curl  -X GET \
            '<URL>/api/histories' \
            --header 'Accept: */*' \
            --header 'Content-Type: application/json' \
            --header 'Authorization: Token <YOUR_TOKEN>' \
        ```

- Return books: `POST /api/returns`
    - Description:
        - Return books
        - Only librarian can use this endpoint
        - `loan_detail_ids` represents the list of book being returned
    - Request
        ```
        {
            "loan_detail_ids": [33]
        }
        ```
    - Response (200)  
        ```json
        {
            "message": "Valid loaned books returned successfully",
            "details": [
                {
                "loan_detail_id": 39,
                "book_info": "Book A by Author A",
                "book": 1,
                "is_returned": true,
                "extension_requested_at": null,
                "expected_return_date": "2023-09-17"
                }
            ]
        }
        ```
    - cURL Import
        ```cURL
        curl  -X POST \
        '<URL>/api/loans' \
        --header 'Accept: */*' \
        --header 'Authorization: Token <YOUR_TOKEN>' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "loan_detail_ids": [33]
        }'
        ```

## Author Information

### Bayu Sasrabau Setiahartono

[LinkedIn](https://linkedin.com/in/setiahartono)