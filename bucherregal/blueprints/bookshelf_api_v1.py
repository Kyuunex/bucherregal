"""
This file provides endpoints for everything bookshelf related
"""
import time
import uuid
import json
import hashlib

from flask import Blueprint, request, make_response, redirect, url_for, render_template

from bucherregal.reusables.rng import get_random_string
from bucherregal.reusables.context import db_cursor
from bucherregal.reusables.context import db_connection
from bucherregal.reusables.context import website_context
from bucherregal.reusables.iptools import ip_decode
from bucherregal.reusables.user_validation import get_user_context
from bucherregal.reusables.api_user_validation import get_api_user_context
from bucherregal.reusables.api_user_validation import is_api_user_original_poster_or_admin
from bucherregal.reusables.api_skeleton import make_book_listing
from bucherregal.reusables.api_skeleton import make_book_request_listing

from bucherregal.classes.BookPost import *
from bucherregal.classes.BookPostUser import *
from bucherregal.classes.BookPostDeletedUser import *
from bucherregal.classes.BookRequest import *
from bucherregal.classes.User import *
from bucherregal.classes.DeletedUser import *

bookshelf_api_v1 = Blueprint("bookshelf_api_v1", __name__)


@bookshelf_api_v1.route('/api/v1/book_listing', methods=['GET', 'POST'])
def index():
    """
    Get book listing with filtering

    :return: json structure of book listing
    """

    user_id = request.form.get('user_id', request.args.get('user_id', ""))
    title = request.form.get('title', request.args.get('title', ""))
    author = request.form.get('author', request.args.get('author', ""))
    genre = request.form.get('genre', request.args.get('genre', ""))
    tags = request.form.get('tags', request.args.get('tags', ""))
    wear_rating = request.form.get('wear_rating', request.args.get('wear_rating', ""))
    location = request.form.get('location', request.args.get('location', ""))
    year = request.form.get('year', request.args.get('year', ""))

    base_query = ("SELECT id, user_id, title, timestamp, wear_rating, year, location, "
                  "additional_information, author, last_edit_timestamp, genre, tags, "
                  "cover_image_url FROM book_listings")

    where_conditions = []
    params = []

    if len(user_id) > 0:
        where_conditions.append("user_id = ?")
        params.append(user_id)

    if len(title) > 0:
        where_conditions.append("title LIKE ?")
        params.append("%" + title + "%")

    if len(author) > 0:
        where_conditions.append("author LIKE ?")
        params.append("%" + author + "%")

    if len(genre) > 0:
        where_conditions.append("genre = ?")
        params.append(genre)

    if len(year) > 0:
        where_conditions.append("year = ?")
        params.append(year)

    if len(tags) > 0:
        where_conditions.append("tags LIKE ?")
        params.append("%" + tags + "%")

    if len(wear_rating) > 0:
        where_conditions.append("wear_rating = ?")
        params.append(wear_rating)

    if len(location) > 0:
        where_conditions.append("location LIKE ?")
        params.append("%" + location + "%")

    if where_conditions:
        where_clause = " WHERE " + " AND ".join(where_conditions)
    else:
        where_clause = ""

    final_query = base_query + where_clause + " ORDER BY timestamp DESC"

    post_db_lookup = tuple(db_cursor.execute(final_query, params))

    book_listings = []
    for post in post_db_lookup:
        current_post = BookPost(post)
        current_post_user = tuple(
            db_cursor.execute("SELECT id, email, username, display_name, permissions, email_is_public, "
                              "registration_timestamp FROM users WHERE id = ?",
                              [current_post.user_id]))
        if current_post_user:
            current_post.user = BookPostUser(current_post_user[0])
        else:
            current_post.user = BookPostDeletedUser(current_post.user_id)

        requests_db = tuple(db_cursor.execute("SELECT user_id FROM book_requests WHERE post_id = ?",
                                              [str(current_post.post_id)]))
        current_post.amount_of_requests = len(requests_db)

        book_listings.append(current_post)

    dicts = []
    for book_listing in book_listings:
        dicts.append(make_book_listing(book_listing))

    response = make_response(json.dumps(dicts), 200)
    response.headers.set("Content-Type", "application/json")
    return response


@bookshelf_api_v1.route('/api/v1/make_post', methods=['POST'])
def make_post():
    """
    This endpoint handles the POST data submitted through post_maker_form.
    It will process user input and properly insert it into the database.

    :return: a redirect to an endpoint used to view the newly made book post
    """

    user_context = get_api_user_context()
    if not user_context:
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        wear_rating = request.form['wear_rating']
        year = request.form['year']
        tags = request.form['tags']
        cover_image_url = request.form['cover_image_url']
        location = request.form['location']
        additional_information = request.form['additional_information']
        posix_timestamp = int(time.time())

        post_id = uuid.uuid4()
        db_cursor.execute("INSERT INTO book_listings (id, user_id, title, timestamp, wear_rating, year, location, "
                          "additional_information, author, last_edit_timestamp, genre, tags, cover_image_url) "
                          "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          [str(post_id), user_context.id, title, posix_timestamp, wear_rating, int(year), location,
                           additional_information, author, posix_timestamp, genre, tags, cover_image_url])
        db_connection.commit()

        response = make_response(json.dumps({"status": "success", "post_id": post_id}), 200)
        response.headers.set("Content-Type", "application/json")
        return response


@bookshelf_api_v1.route('/api/v1/post_view/<post_id>')
def post_view(post_id):
    """
    This endpoint reads the database and renders a json page containing the specified book post.

    :param post_id: ID of the book post
    :return: An json page render containing the book post
    """

    user_context = get_api_user_context()

    post_db_lookup = tuple(db_cursor.execute("SELECT id, user_id, title, timestamp, wear_rating, year, location, "
                                             "additional_information, author, last_edit_timestamp, genre, tags, "
                                             "cover_image_url FROM book_listings "
                                             "WHERE id = ?", [post_id]))
    if not post_db_lookup:
        return json.dumps({
            "error": "404 Post not found"
        }), 404

    book_listing = BookPost(post_db_lookup[0])
    book_listing_author = tuple(
        db_cursor.execute("SELECT id, email, username, display_name, permissions, "
                          "email_is_public, registration_timestamp FROM users WHERE id = ?",
                          [book_listing.user_id]))
    if book_listing_author:
        book_listing.user = BookPostUser(book_listing_author[0])
    else:
        book_listing.user = BookPostDeletedUser(book_listing.user_id)

    requests_db = tuple(db_cursor.execute("SELECT user_id FROM book_requests "
                                          "WHERE post_id = ?",
                                          [str(post_id)]))
    book_listing.amount_of_requests = len(requests_db)

    dict_resp = make_book_listing(book_listing)
    if user_context:
        dict_resp["current_user_request_approved"] = bool(
            tuple(
                db_cursor.execute("SELECT is_approved FROM book_requests "
                                  "WHERE post_id = ? AND user_id = ? AND is_approved = ?",
                                  [str(post_id), str(user_context.id), 1])))
    else:
        dict_resp["current_user_request_approved"] = False

    response = make_response(json.dumps(dict_resp), 200)
    response.headers.set("Content-Type", "application/json")
    return response


@bookshelf_api_v1.route('/api/v1/delete_post/<post_id>')
def delete_post(post_id):
    user_context = get_api_user_context()
    if not user_context:
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401
    if not is_api_user_original_poster_or_admin(post_id):
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401

    db_cursor.execute("DELETE FROM book_listings WHERE id = ?", [post_id])

    response = make_response(json.dumps({"status": "success"}), 200)
    response.headers.set("Content-Type", "application/json")
    return response


@bookshelf_api_v1.route('/api/v1/edit_post/<post_id>', methods=['POST'])
def edit_post(post_id):
    """
    This endpoint handles the POST data submitted through post_edit_form.
    It will process user input and properly update everything in the database.

    :return: a redirect to an endpoint used to view the newly made book post
    """

    user_context = get_api_user_context()
    if not user_context:
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401
    if not is_api_user_original_poster_or_admin(post_id):
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        wear_rating = request.form['wear_rating']
        year = request.form['year']
        tags = request.form['tags']
        cover_image_url = request.form['cover_image_url']
        location = request.form['location']
        additional_information = request.form['additional_information']
        posix_timestamp = int(time.time())

        db_cursor.execute("UPDATE book_listings "
                          "SET title = ?, wear_rating = ?, year = ?, location = ?, additional_information = ?, "
                          "author = ?, last_edit_timestamp = ?, genre = ?, tags = ?, cover_image_url = ? "
                          "WHERE id = ?",
                          [title, wear_rating, int(year), location, additional_information,
                           author, posix_timestamp, genre, tags, cover_image_url, post_id])
        db_connection.commit()

        response = make_response(json.dumps({"status": "success", "post_id": post_id}), 200)
        response.headers.set("Content-Type", "application/json")
        return response


@bookshelf_api_v1.route('/api/v1/request_book/<post_id>', methods=['POST'])
def request_book(post_id):
    user_context = get_api_user_context()
    if not user_context:
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401

    already_requested = tuple(db_cursor.execute("SELECT post_id FROM book_requests "
                                                "WHERE post_id = ? AND user_id = ?",
                                                [str(post_id), str(user_context.id)]))

    if already_requested:
        return json.dumps({
            "error": "you already requested this book"
        }), 400

    comment = request.form['comment']

    db_cursor.execute("INSERT INTO book_requests (user_id, post_id, comment, request_timestamp, is_approved) "
                      "VALUES (?, ?, ?, ?, ?)", [str(user_context.id), str(post_id), comment, int(time.time()), 0])
    db_connection.commit()

    response = make_response(json.dumps({"status": "success"}), 200)
    response.headers.set("Content-Type", "application/json")
    return response


@bookshelf_api_v1.route('/api/v1/book_request_listing/<post_id>')
def book_request_listing(post_id):
    user_context = get_api_user_context()
    if not user_context:
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401
    if not is_api_user_original_poster_or_admin(post_id):
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401

    request_list_db = tuple(db_cursor.execute("SELECT user_id, post_id, comment, request_timestamp, is_approved "
                                              "FROM book_requests WHERE post_id = ? "
                                              "ORDER BY request_timestamp ASC", [post_id]))

    request_listing = []
    for book_request in request_list_db:
        current_request = BookRequest(book_request)
        current_request_user = tuple(db_cursor.execute("SELECT id, email, username, display_name, permissions, "
                                                       "email_is_public, registration_timestamp "
                                                       "FROM users WHERE id = ?", [current_request.user_id]))
        if current_request_user:
            current_request.user = User(current_request_user[0])
        else:
            current_request.user = DeletedUser(current_request.user_id)
        request_listing.append(current_request)

    dicts = []
    for one_request in request_listing:
        dicts.append(make_book_request_listing(one_request))

    response = make_response(json.dumps(dicts), 200)
    response.headers.set("Content-Type", "application/json")
    return response


@bookshelf_api_v1.route('/api/v1/update_book_request_status/<post_id>/<user_id>/<action_id>', methods=['GET'])
def update_book_request_status(post_id, user_id, action_id):
    user_context = get_api_user_context()
    if not user_context:
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401
    if not is_api_user_original_poster_or_admin(post_id):
        return json.dumps({
            "error": "401 Unauthorized"
        }), 401

    book_request = tuple(db_cursor.execute("SELECT post_id FROM book_requests WHERE post_id = ? AND user_id = ?",
                                           [str(post_id), str(user_id)]))

    if not book_request:
        return json.dumps({
            "error": "404 Not Found"
        }), 404

    db_cursor.execute("UPDATE book_requests SET is_approved = ? WHERE user_id = ? AND post_id = ?",
                      [action_id, str(user_id), str(post_id)])
    db_connection.commit()

    response = make_response(json.dumps({"status": "success"}), 200)
    response.headers.set("Content-Type", "application/json")
    return response


@bookshelf_api_v1.route('/api/v1/request_access_form')
def request_access_form():
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login"))

    user_api_key_db = tuple(db_cursor.execute("SELECT api_key FROM api_keys WHERE user_id = ?",
                                              [str(user_context.id)]))

    if not user_api_key_db:
        return redirect(url_for("bookshelf_api_v1.generate_api_key"))

    return render_template(
        "api_key_show_form.html",
        WEBSITE_CONTEXT=website_context,
        USER_CONTEXT=user_context,
        API_KEY=user_api_key_db[0][0]
    )


@bookshelf_api_v1.route('/api/v1/generate_api_key')
def generate_api_key():
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login"))

    new_session_token = get_random_string(32)

    client_ip_address_is_ipv6, client_ip_address_int = ip_decode(request)

    db_cursor.execute("INSERT OR REPLACE INTO api_keys (user_id, api_key, timestamp, ip_address, ipv6) "
                      "VALUES (?, ?, ?, ?, ?)",
                      [str(user_context.id), str(new_session_token), int(time.time()),
                       int(client_ip_address_int), int(client_ip_address_is_ipv6)])
    db_connection.commit()

    return redirect(url_for("bookshelf_api_v1.request_access_form"))


@bookshelf_api_v1.route('/api/v1/418')
def make_tea():
    return json.dumps({
        "error": "503 Service Unavailable"
    }), 503
