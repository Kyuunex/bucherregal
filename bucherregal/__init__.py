#!/usr/bin/env python3
"""
This file stitches the whole flask app together
"""

from flask import Flask, url_for, redirect, render_template

from bucherregal.reusables.context import db_connection
from bucherregal.reusables.context import website_context
from bucherregal.reusables.user_validation import get_user_context

from bucherregal.blueprints.administration import administration
from bucherregal.blueprints.bookshelf import bookshelf
from bucherregal.blueprints.bookshelf_api_v1 import bookshelf_api_v1
from bucherregal.blueprints.user_management import user_management

app = Flask(__name__)
app.register_blueprint(administration)
app.register_blueprint(bookshelf)
app.register_blueprint(bookshelf_api_v1)
app.register_blueprint(user_management)


@app.route('/server_shutdown')
def server_shutdown():
    """
    This endpoint provides the website administrator a way to
    safely commit database changes before shutting the app down

    :return: if logged in, the string response if success, if not logged in, a redirect to the login form
    """

    user_context = get_user_context()
    if not user_context:
        return redirect(url_for("user_management.login_form"))
    if not user_context.permissions >= 9:
        return "you do not have permissions to perform this action"

    db_connection.commit()
    db_connection.close()
    return "server ready for shutdown"


@app.route('/cookies')
def cookies():
    user_context = get_user_context()
    return render_template("cookies.html", WEBSITE_CONTEXT=website_context, USER_CONTEXT=user_context)
