#
#
from python_byzatic_commons.exceptions.BaseErrorException import BaseErrorException


class NotImplementedException(BaseErrorException):
    def __init__(self, *args):
        super().__init__(*args)
