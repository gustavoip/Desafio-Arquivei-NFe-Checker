import threading
import time

from nfe_checker.arquivei_api import ArquiveiAPI
from nfe_checker.config import logger, Session
from nfe_checker.models import Nfe, Cursor


class NfesCollectorService(threading.Thread):
    def __init__(self, arquivei_api: ArquiveiAPI):
        super().__init__()
        self.arquivei_api = arquivei_api
        self.service_name = "NFEs Collector Service"

    def run(self):
        logger.info(f"Starting {self.service_name}")
        session = Session()
        last_cursor = Cursor.query.order_by('-id').first()
        last_cursor = last_cursor.cursor_position
        while True:
            try:
                nfes, last_cursor = self.arquivei_api.get_last_nfes(cursor=last_cursor)
                nfes = [Nfe(**nfe) for nfe in nfes]
                last_cursor = Cursor(cursor_position=last_cursor)

                session.add_all(nfes + [last_cursor])
                session.commit()

            except Exception as e:
                # TODO: Be more specific here... Lack of test cases
                logger.exception(f"Exception in the"
                                 f"{self.service_name} loop", e)
            else:
                logger.info(f"Success! {len(nfes) + 1} were inserted in the "
                            f"database")

            time.sleep(5 * 60)
