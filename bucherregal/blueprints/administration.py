"""
This file provides endpoints for everything bookshelf related
"""
from flask import Blueprint, request, redirect, url_for, render_template

from bucherregal.reusables.context import db_cursor
from bucherregal.reusables.context import db_connection
from bucherregal.reusables.context import website_context
from bucherregal.reusables.user_validation import get_user_context

from bucherregal.classes.User import *

administration = Blueprint("administration", __name__)


@administration.route('/administration')
def admin():
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 9:
        return "you do not have permissions to perform this action"

    return render_template("admin_panel.html", WEBSITE_CONTEXT=website_context, USER_CONTEXT=user_context)


@administration.route('/administration/sql_form')
def sql_form():
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 9:
        return "you do not have permissions to perform this action"

    return render_template(
        "sql.html",
        WEBSITE_CONTEXT=website_context,
        USER_CONTEXT=user_context
    )


@administration.route('/administration/sql_exec', methods=['POST'])
def sql_exec():
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 9:
        return "you do not have permissions to perform this action"

    if request.method == 'POST':
        sql_query = request.form['sql_query']

        sql_results = tuple(db_cursor.execute(sql_query))
        db_connection.commit()

        return render_template(
            "sql.html",
            WEBSITE_CONTEXT=website_context,
            USER_CONTEXT=user_context,
            SQL_RESULTS=sql_results
        )


@administration.route('/user_list')
def user_listing():
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 9:
        return "you do not have permissions to perform this action"

    info_db = tuple(db_cursor.execute("SELECT id, email, username, display_name, permissions, email_is_public, "
                                      "registration_timestamp "
                                      "FROM users"))

    users = []
    for one_info_db in info_db:
        users.append(User(one_info_db))

    return render_template(
        "user_listing.html",
        WEBSITE_CONTEXT=website_context,
        USER_LISTING=users,
        USER_CONTEXT=user_context
    )
