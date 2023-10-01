from urllib.parse import urlparse
from flask import request


def make_book_listing(book_listing):
    user = {
        "id": book_listing.user.id,
        "username": book_listing.user.username,
        "display_name": book_listing.user.display_name,
        "permissions": book_listing.user.permissions,
        "email_is_public": book_listing.user.email_is_public,
        "registration_timestamp": book_listing.user.registration_timestamp,
    }

    if book_listing.user.email_is_public:
        user["email"] = book_listing.user.email
    else:
        user["email"] = "redacted@" + urlparse(request.base_url).hostname

    book_dict = {
        "id": book_listing.post_id,
        "user_id": book_listing.user_id,
        "user": user,
        "title": book_listing.title,
        "timestamp": book_listing.timestamp,
        "wear_rating": book_listing.wear_rating,
        "year": book_listing.year,
        "location": book_listing.location,
        "additional_information": book_listing.additional_information,
        "author": book_listing.author,
        "genre": book_listing.genre,
        "tags": book_listing.tags,
        "cover_image_url": book_listing.cover_image_url,
        "amount_of_requests": book_listing.amount_of_requests,
    }

    return book_dict


def make_book_request_listing(current_request):
    user = {
        "id": current_request.user.id,
        "username": current_request.user.username,
        "display_name": current_request.user.display_name,
        "permissions": current_request.user.permissions,
        "email_is_public": current_request.user.email_is_public,
        "registration_timestamp": current_request.user.registration_timestamp,
    }

    if current_request.user.email_is_public:
        user["email"] = current_request.user.email
    else:
        user["email"] = "redacted@" + urlparse(request.base_url).hostname

    book_request_dict = {
        "user_id": current_request.user_id,
        "user": user,
        "post_id": current_request.post_id,
        "comment": current_request.comment,
        "request_timestamp": current_request.request_timestamp,
        "is_approved": current_request.is_approved,
    }

    return book_request_dict
