from core import DataBase as _DataBase
from core import Table as _Table


class Table(_Table):
    def _get_random_params(self):
        values = {}

        for field in self._get_fields():
            value = None
            if field["type"] == "integer":
                value = self.content_gen.get_int(0, 9999)
            elif field["type"] == "text":
                value = self.content_gen.get_text(255)

            values[field["name"]] = value

        return values

    def _get_fields(self):
        if hasattr(self, "fields"):
            return self.__fields

        c = self.get_cursor()

        self.__fields = []

        sql = "PRAGMA table_info({0})".format(self.name)
        for (num, name, f_type, _, _, _) in c.execute(sql):
            self.__fields.append({"name": name, "type": f_type})

        return self.__fields


class DataBase(_DataBase):
    _table_cls = Table

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column"""
        return "SELECT name FROM sqlite_master WHERE type='table'"
