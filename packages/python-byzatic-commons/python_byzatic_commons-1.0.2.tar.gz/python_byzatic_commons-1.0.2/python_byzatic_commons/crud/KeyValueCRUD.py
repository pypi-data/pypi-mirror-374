#
#
#
from python_byzatic_commons.exceptions.NotImplementedException import NotImplementedException
from python_byzatic_commons.crud.interfaces.KeyValueCRUDInterface import KeyValueCRUDInterface


class KeyValueCRUD(KeyValueCRUDInterface):
    def create(self, entry_id: any, data: any) -> any:
        raise NotImplementedException

    def read(self, entry_id: any) -> any:
        raise NotImplementedException

    def update(self, entry_id: any, data: any) -> any:
        raise NotImplementedException

    def delete(self, entry_id: any) -> any:
        raise NotImplementedException
