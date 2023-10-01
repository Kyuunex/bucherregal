# API v1 Documentation

## Authorization
Authorization is done by supplying your token in the `Authorization` header.  
To generate or re-generate a token, visit `/api/v1/request_access_form` in your browser while logged in.  
To create an account, visit `/registration_form` in your browser.  

## Endpoints
Documentation is incomplete for now.

### Get a list of book listings.
#### `GET/POST` `/api/v1/book_listing`
- returns: json with a list of all book listings

```bash
curl http://127.0.0.1:8089/api/v1/book_listing
```
```json
[
    {
        "id": "a4a140a3-e316-4e50-a14a-672e238a3594",
        "user_id": "0cfa1df5-7b9f-4f98-8d37-4b1244888d4b",
        "user": {
            "id": "0cfa1df5-7b9f-4f98-8d37-4b1244888d4b",
            "username": "sel",
            "display_name": "sel",
            "permissions": 2,
            "email_is_public": 0,
            "registration_timestamp": 1696080198,
            "email": "redacted@127.0.0.1"
        },
        "title": "A Conjuring of Light: A Novel",
        "timestamp": 1696080397,
        "wear_rating": 2,
        "year": 2017,
        "location": "Kutaisi, Georgia",
        "additional_information": "idk why i have this but i don't want it.",
        "author": "V. E. Schwab",
        "genre": "Historical",
        "tags": "",
        "cover_image_url": "https://static.wikia.nocookie.net/shadesofmagic/images/2/25/ACOL_US_Cover_1.png",
        "amount_of_requests": 0
    },
    {
        "id": "fb441eb2-1892-45cd-8c2d-339a87d5b3db",
        "user_id": "4dc7eb39-126d-414b-962f-fe1a07d5968c",
        "user": {
            "id": "4dc7eb39-126d-414b-962f-fe1a07d5968c",
            "username": "qnx",
            "display_name": "qnx",
            "permissions": 9,
            "email_is_public": 0,
            "registration_timestamp": 1695970959,
            "email": "redacted@127.0.0.1"
        },
        "title": "The Alchemist",
        "timestamp": 1695917553,
        "wear_rating": 4,
        "year": 1988,
        "location": "Saburtalo, Tbilisi, Georgia",
        "additional_information": "This book was given to me by my grandfather but this was very long time ago and I have too many books, so I think it will serve someone else better. :)",
        "author": "Paulo Coelho",
        "genre": "Fantasy",
        "tags": "",
        "cover_image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c4/TheAlchemist.jpg",
        "amount_of_requests": 2
    }
]
```

---

### Make post
#### `POST` `/api/v1/make_post`
- `title`: 
- `author`: 
- `genre`: 
- `wear_rating`:
- `year`: 
- `tags`: 
- `cover_image_url`: 
- `location`: 
- `additional_information`:

---

### Get book details
#### `GET` `/api/v1/post_view/<post_id>`

---

### Delete a post
#### `POST` `/api/v1/delete_post/<post_id>`

---

### Edit post
#### `POST` `/api/v1/edit_post/<post_id>`
- `title`: 
- `author`: 
- `genre`: 
- `wear_rating`: 
- `year`: 
- `tags`: 
- `cover_image_url`: 
- `location`: 
- `additional_information`:

---

### Request a book
#### `POST` `/api/v1/request_book/<post_id>`

---

### List book requests
#### `GET` `/api/v1/book_request_listing/<post_id>`

---

### Update book request status
#### `GET` `/api/v1/update_book_request_status/<post_id>/<user_id>/<action_id>`
