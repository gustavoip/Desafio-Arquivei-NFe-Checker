import requests
from flask import Flask
from flask import render_template, request
from wtforms import Form, validators, StringField

from nfe_checker.arquivei_api import ArquiveiAPI
from nfe_checker.config import db
from nfe_checker.services import NfesCollectorService
from nfe_checker.models import Nfe

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ANY_SUFFICIENTLY_ADVANCED_TECHNOLOGY_IS_INDISTINGUISHABLE_FROM_MAGIC'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
db.create_all()


class ReusableForm(Form):
    access_token = StringField('Access Token:',
                               validators=[validators.required()])


@app.route('/', methods=['GET', 'POST'])
def index():
    """Endpoint to create a user."""
    form = ReusableForm(request.form)
    value = None
    not_found_msg = False
    if request.method == 'POST':
        access_token = request.form["access_token"]
        if form.validate():
            nfe = Nfe.query.filter_by(access_key=access_token).first()
            if not nfe:
                not_found_msg = True
            else:
                value = nfe.value

    return render_template('index.html', form=form,
                           not_found_msg=not_found_msg,
                           value=value)


if __name__ == "__main__":
    client = requests.Session()
    # To avoid dealing with local machine SSL certification details,
    # we disable security verification. It's not a production-ready
    # solution, obviously.
    client.verify = False

    api = ArquiveiAPI(
        client,
        credentials={
            "x-api-id": "e021f345e68de190b17becb313e81f7874479bcb",
            "x-api-key": "c0d24ab7b6a1732189cabf4d7d4896031c8a25dc",
            "content-type": "application/json",
        },
    )

    service = NfesCollectorService(api)
    service.start()

    app.run(port=5000, debug=True)
