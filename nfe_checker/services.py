import threading
import time

from nfe_checker.arquivei_api import ArquiveiAPI
from nfe_checker.models import Nfe, CursorPosition
from nfe_checker.shared import logger, db


class NfesCollectorService(threading.Thread):
    def __init__(self, arquivei_api: ArquiveiAPI):
        super().__init__()
        self.arquivei_api = arquivei_api
        self.service_name = "NFEs Collector Service"

    def run(self):
        logger.info(f"Starting {self.service_name}")
        last_cursor = CursorPosition.query.order_by(-CursorPosition.id).first()
        if last_cursor is None:
            last_cursor = 0
        else:
            last_cursor = last_cursor.cursor_position
        while True:
            try:
                nfes, last_cursor = self.arquivei_api.get_last_nfes(cursor=last_cursor)
                nfes = [Nfe(**nfe) for nfe in nfes]
                last_cursor = CursorPosition(cursor_position=last_cursor)
                db.session.add_all(nfes + [last_cursor])
                db.session.commit()

            except Exception as e:
                # TODO: Be more specific here... Lack of test cases
                logger.exception(f"Exception in the" f"{self.service_name} loop", e)
            else:
                logger.info(
                    f"Success! {len(nfes) + 1} were inserted in the " f"database"
                )

            time.sleep(5 * 60)
