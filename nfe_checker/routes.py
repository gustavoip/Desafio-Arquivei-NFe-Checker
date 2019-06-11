from nfe_checker.shared import app
from flask import render_template, request
from wtforms import Form, validators, StringField

from nfe_checker.models import Nfe


class ReusableForm(Form):
    access_token = StringField("Access Token:", validators=[validators.required()])


@app.route("/", methods=["GET", "POST"])
def index():
    """Endpoint to create a user."""
    form = ReusableForm(request.form)
    value = None
    not_found_msg = False
    if request.method == "POST":
        access_token = request.form["access_token"]
        if form.validate():
            nfe = Nfe.query.filter_by(access_key=access_token).first()
            if not nfe:
                not_found_msg = True
            else:
                value = nfe.value

    return render_template(
        "index.html", form=form, not_found_msg=not_found_msg, value=value
    )
