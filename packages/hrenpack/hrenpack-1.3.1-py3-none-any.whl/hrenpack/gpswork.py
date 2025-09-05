import gps
from gps import WATCH_ENABLE
from time import sleep
from logging import error
from typing import Literal


class GPS:
    """Пока не работает"""

    class GPSError(Exception):
        pass

    def __init__(self, mode: Literal['READ_ONLY_MODE', 'WATCH_ENABLE', 'WATCH_DISABLE'] = 'READ_ONLY_MODE',
                 raise_errors: bool = False):
        try:
            self.raise_errors = raise_errors
            self.session = gps.gps(mode=eval(f'gps.{mode}'))
            self.session.stream(eval(f'gps.{mode}'))
            self._success = True
        except ConnectionRefusedError as e:
            self._success = False
            if not raise_errors:
                e = '[GPS] ' + str(e)
            self._error(e)

    def __call__(self, while_no_result: bool = False, timeout: float = 1):
        if self._success:
            if while_no_result:
                while True:
                    report = self.session.next()
                    if report['class'] == 'TPV':
                        return report
                    sleep(timeout)
            return self.session.next()
        else:
            raise self.GPSError('GPS is not working')

    def _error(self, e):
        if self.raise_errors:
            raise self.GPSError(e)
        else:
            error(e)
