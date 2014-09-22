import core
import re


class Table(core.Table):

    def __init__(self, *args, **kargs):
        super(Table, self).__init__(*args, **kargs)
        self.__fields = None

    def _create_insert_sql(self):
        field_names = [i.get_name() for i in self._get_fields()]

        return "INSERT INTO {0} VALUES ({1})".format(
            self.name,
            ", ".join([":{0}".format(i) for i in field_names])
        )

    def _get_fields(self):
        if self.__fields is not None:
            return self.__fields

        c = self.get_cursor()

        self.__fields = []

        sql = "PRAGMA table_info({0})".format(self.name)
        for (num, name, f_type, _, _, _) in c.execute(sql):
            f_type = f_type.lower()
            type = TypeAffinity
            if TypeAffinity(f_type).type in ["integer", "numeric"]:
                field = IntegerField(name, 0, 9999)
            elif TypeAffinity(f_type).type == "text":
                field = TextField(name, 255)
            elif TypeAffinity(f_type).type == "real":
                field = RealField(name)
            elif TypeAffinity(f_type).type == "none":
                field = NoneField(name, 255)
            else:
                raise Exception("Unexpected column type '{0}'".format(f_type))

            self.__fields.append(field)

        return self.__fields

    def get_relations(self):
        c = self.get_cursor()

        relations = []

        sql = "SELECT sql FROM sqlite_master WHERE name = ?"
        c.execute(sql, (self.name,))

        sql = c.fetchone()[0]

        # @todo - Change this to use
        # "PRAGMA foreign_key_list(table-name);" statement
        return self._parse_relations(sql)

    def _parse_relations(self, sql):
        pattern = r".*FOREIGN KEY \((.*?)\).*?REFERENCES (.*?)\((.*?)\).*"

        relations = []
        for line in sql.splitlines(True):
            result = re.match(pattern, line)

            if result is not None:
                relation = {
                    "ref_table": result.group(2).strip(),
                    "columns": [
                        c.strip() for c in result.group(1).split(",")],
                    "ref_columns": [
                        c.strip() for c in result.group(3).split(",")],
                }

                relations.append(relation)

        return relations


class TypeAffinity(object):
    """
    Implementation of rules in SQLite's affinity specification:
    See more in http://www.sqlite.org/datatype3.html#affname

    Examples:
    TypeAffinity("BIGINT").type == "integer"
    TypeAffinity("VARCHAR").type == "text"
    ...
    """

    def __init__(self, typename):
        self.typename = typename

    @property
    def type(self):
        if "int" in self.typename.lower():
            return "integer"

        for type in ["char", "clob", "text"]:
            if type in self.typename.lower():
                return "text"

        for type in ["real", "floa", "doub"]:
            if type in self.typename.lower():
                return "real"

        if "blob" in self.typename.lower():
            return "none"

        if self.typename.lower() == "":
            return "none"

        return "numeric"


class IntegerField(core.Field):
    def __init__(self, name, min, max):
        super(IntegerField, self).__init__(name)
        self.min = min
        self.max = max

    def _get_random_value(self):
        return self.content_gen.get_int(self.min, self.max)


class TextField(core.Field):
    def __init__(self, name, length):
        super(TextField, self).__init__(name)
        self.length = length

    def _get_random_value(self):
        return self.content_gen.get_text(self.length)


class NoneField(TextField):
    pass


class BlobField(TextField):
    pass


class RealField(core.Field):
    _range = 99999

    def _get_random_value(self):
        return float(
            "{0}.{1}".format(
                self.content_gen.get_int(0, self._range),
                self.content_gen.get_int(0, self._range)
            )
        )


class DataBase(core.DataBase):
    _table_cls = Table

    def __init__(self, content_gen, name, engine="sqlite3"):
        super(DataBase, self).__init__(content_gen)
        self._engine = engine
        self._name = name

    def get_conn(self):
        if hasattr(self, '_conn'):
            return self._conn

        eng = __import__(self._engine)
        self._conn = eng.connect(self._name)
        return self._conn

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column"""
        return "SELECT name FROM sqlite_master WHERE type='table'"
