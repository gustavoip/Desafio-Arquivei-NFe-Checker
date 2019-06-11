import requests

from nfe_checker.arquivei_api import ArquiveiAPI
from nfe_checker.routes import index
from nfe_checker.services import NfesCollectorService
from nfe_checker.shared import db, app

app.add_url_rule("/", index)
db.init_app(app)
db.create_all()


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

    app.run(port=5000, debug=True, host=('0.0.0.0'))
