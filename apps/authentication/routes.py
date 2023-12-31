from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_user, logout_user

from apps import login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass


@blueprint.route("/")
def route_default():
    return redirect(url_for("home_blueprint.connect_input_tool"))


@blueprint.route("/User_data")
def default_user_data():
    return redirect(url_for("home_blueprint.User_info"))



# Login & Registration
@blueprint.route("/login", methods=["GET", "POST"])
def login():
    print("login routes")
    login_form = LoginForm(request.form)
    if "login" in request.form:
        # read form da ta
        username = request.form["username"]
        password = request.form["password"]
        # Locate user
        user = Users.query.filter_by(email=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for("authentication_blueprint.default_user_data"))

        # Something (user or pass) is not ok
        return render_template(
            "accounts/login.html", msg="Wrong user or password", form=login_form
        )

    if not current_user.is_authenticated:
        return render_template("accounts/login.html", form=login_form)
        # return redirect(url_for("home_blueprint.User_info"))
        
    return redirect(url_for("home_blueprint.User_info"))


@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("authentication_blueprint.login"))


# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("authentication_blueprint.login"))


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template("home/page-403.html"), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template("home/page-404.html"), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template("home/page-500.html"), 500
