"""
This file provides endpoints for everything bookshelf related
"""
import time
import uuid
from feedgen.feed import FeedGenerator
from urllib.parse import urlparse

from flask import Blueprint, request, make_response, redirect, url_for, render_template

from bucherregal.reusables.context import db_cursor
from bucherregal.reusables.context import db_connection
from bucherregal.reusables.context import website_context
from bucherregal.reusables.user_validation import get_user_context

from bucherregal.classes.BookPost import *
from bucherregal.classes.BookPostUser import *
from bucherregal.classes.BookPostDeletedUser import *

bookshelf = Blueprint("bookshelf", __name__)


@bookshelf.route('/', methods=['GET', 'POST'])
@bookshelf.route('/rss.xml', methods=['GET', 'POST'], endpoint="rss")
def index():
    """
    This endpoint provides the index page, which is a listing of the recent bookshelf posts

    :return: html render of the recent bookshelf posts
    """

    user_context = get_user_context()
    if user_context:
        user_permissions = user_context.permissions
    else:
        user_permissions = 1

    print(request.form)

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

    # print(final_query)
    post_db_lookup = tuple(db_cursor.execute(final_query, params))

    # post_db_lookup = tuple(db_cursor.execute("SELECT id, user_id, title, timestamp, wear_rating, year, location, "
    #                                          "additional_information, author, last_edit_timestamp, genre, tags, "
    #                                          "cover_image_url FROM book_listings "
    #                                          # f"{lookup_conditions_str} "
    #                                          "ORDER BY timestamp DESC"))

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
        book_listings.append(current_post)

    if request.endpoint == "bookshelf.rss":
        feed = FeedGenerator()
        feed.title(website_context["title"])
        feed.description("In cases of constant automated scrapers, avoid scraping more than once per few hours.")
        feed.link(href=request.host_url)
        url_parsed = urlparse(request.base_url)

        for book_listing in book_listings:
            feed_entry = feed.add_entry()
            feed_entry.title(book_listing.title)
            if book_listing.user.email_is_public:
                author_email = book_listing.user.email
            else:
                # author_email = book_listing.user_id + "@" + url_parsed.hostname
                author_email = "redacted@" + url_parsed.hostname
            feed_entry.author(name=book_listing.user.display_name, email=author_email)
            feed_entry.description(f"Location: {book_listing.location}\n\n{book_listing.additional_information}")
            feed_entry.pubDate(book_listing.timestamp_utc)
            feed_entry.link(href=url_for("bookshelf.post_view", post_id=book_listing.post_id, _external=True))
            feed_entry.guid(url_for("bookshelf.post_view", post_id=book_listing.post_id, _external=True),
                            permalink=True)
            # if book_listing.cover_image_url:
            #     feed_entry.image(url=book_listing.cover_image_url)

        response = make_response(feed.rss_str())
        response.headers.set("Content-Type", "application/rss+xml")
    else:
        normal_template = render_template(
            "post_listing.html",
            WEBSITE_CONTEXT=website_context,
            USER_CONTEXT=user_context,
            BOOK_LISTINGS=book_listings
        )
        response = make_response(normal_template)
    return response


@bookshelf.route('/post_maker_form')
def post_maker_form():
    """
    This endpoint provides a blog post form to a user, to be filled up and submitted

    :return: html render of a blog post form
    """

    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 2:
        return "you do not have permissions to perform this action"

    return render_template("post_maker_form.html", WEBSITE_CONTEXT=website_context, USER_CONTEXT=user_context)


@bookshelf.route('/make_post', methods=['POST'])
def make_post():
    """
    This endpoint handles the POST data submitted through post_maker_form.
    It will process user input and properly insert it into the database.

    :return: a redirect to an endpoint used to view the newly made post
    """

    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 2:
        return "you do not have permissions to perform this action"

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

        resp = make_response(redirect(url_for("bookshelf.post_view", post_id=post_id)))

        return resp


@bookshelf.route('/post_view/<post_id>')
def post_view(post_id):
    """
    This endpoint reads the database and renders an html page containing the specified blog post.

    :param post_id: ID of the blog post
    :return: An html page render containing the blog post
    """

    user_context = get_user_context()
    if user_context:
        user_permissions = user_context.permissions
    else:
        user_permissions = 1

    post_db_lookup = tuple(db_cursor.execute("SELECT id, user_id, title, timestamp, wear_rating, year, location, "
                                             "additional_information, author, last_edit_timestamp, genre, tags, "
                                             "cover_image_url FROM book_listings "
                                             "WHERE id = ?", [post_id]))
    if not post_db_lookup:
        return make_response(redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

    book_listing = BookPost(post_db_lookup[0])
    book_listing_author = tuple(
        db_cursor.execute("SELECT id, email, username, display_name, permissions, "
                          "email_is_public, registration_timestamp FROM users WHERE id = ?",
                          [book_listing.user_id]))
    if book_listing_author:
        book_listing.author = BookPostUser(book_listing_author[0])
    else:
        book_listing.author = BookPostDeletedUser(book_listing.user_id)

    requests_db = tuple(db_cursor.execute("SELECT user_id FROM book_requests "
                                          "WHERE post_id = ?",
                                          [str(post_id)]))
    book_listing.amount_of_requests = len(requests_db)

    return render_template(
        "post_view.html",
        WEBSITE_CONTEXT=website_context,
        USER_CONTEXT=user_context,
        BOOK_LISTING=book_listing,
        USER_PERMISSIONS=user_permissions
    )


@bookshelf.route('/post_edit_form/<post_id>')
def post_edit_form(post_id):
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 5:
        return "you do not have permissions to perform this action"
    user_permissions = user_context.permissions
    ## TODO ONLY ORIGINAL POSTER CAN EDIT

    post_db_lookup = tuple(db_cursor.execute("SELECT id, user_id, title, timestamp, wear_rating, year, location, "
                                             "additional_information, author, last_edit_timestamp, genre, tags, "
                                             "cover_image_url FROM book_listings "
                                             "WHERE id = ? ", [post_id]))

    if not post_db_lookup:
        return make_response(redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

    book_listing = BookPost(post_db_lookup[0])

    return render_template(
        "post_edit_form.html",
        WEBSITE_CONTEXT=website_context,
        USER_CONTEXT=user_context,
        BOOK_LISTING=book_listing
    )


@bookshelf.route('/delete_post/<post_id>')
def delete_post(post_id):
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 5:
        return "you do not have permissions to perform this action"
    ## TODO ONLY ORIGINAL POSTER CAN DELET

    db_cursor.execute("DELETE FROM book_listings WHERE id = ?", [post_id])

    return redirect(url_for("bookshelf.index"))


@bookshelf.route('/edit_post/<post_id>', methods=['POST'])
def edit_post(post_id):
    """
    This endpoint handles the POST data submitted through post_maker_form.
    It will process user input and properly insert it into the database.

    :return: a redirect to an endpoint used to view the newly made post
    """

    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 5:
        return "you do not have permissions to perform this action"
    ## TODO ONLY ORIGINAL POSTER CAN EDIT

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

        resp = make_response(redirect(url_for("bookshelf.post_view", post_id=post_id)))

        return resp


@bookshelf.route('/search_form')
def search_form():
    user_context = get_user_context()

    return render_template("search_form.html",
                           WEBSITE_CONTEXT=website_context,
                           USER_CONTEXT=user_context)


@bookshelf.route('/request_book_form/<post_id>')
def request_book_form(post_id):
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 2:
        return "you do not have permissions to perform this action"

    post_db_lookup = tuple(db_cursor.execute("SELECT id, user_id, title, timestamp, wear_rating, year, location, "
                                             "additional_information, author, last_edit_timestamp, genre, tags, "
                                             "cover_image_url FROM book_listings "
                                             "WHERE id = ? ", [post_id]))

    if not post_db_lookup:
        return make_response(redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

    book_listing = BookPost(post_db_lookup[0])

    return render_template(
        "request_book_form.html",
        WEBSITE_CONTEXT=website_context,
        USER_CONTEXT=user_context,
        BOOK_LISTING=book_listing
    )


@bookshelf.route('/request_book/<post_id>', methods=['POST'])
def request_book(post_id):
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))

    already_requested = tuple(db_cursor.execute("SELECT post_id FROM book_requests "
                                                "WHERE post_id = ? AND user_id = ?",
                                                [str(post_id), str(user_context.id)]))

    if already_requested:
        return "You have already requested this book."

    comment = request.form['comment']

    db_cursor.execute("INSERT INTO book_requests (user_id, post_id, comment, request_timestamp) "
                      "VALUES (?, ?, ?, ?)", [str(user_context.id), str(post_id), comment, int(time.time())])
    db_connection.commit()

    resp = make_response(redirect(url_for("bookshelf.post_view", post_id=post_id)))

    return resp
