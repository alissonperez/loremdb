import random
from datetime import date, timedelta, datetime
import re
from os import linesep


_phrases = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
    "Pellentesque in diam cursus, convallis nisl quis, pulvinar sapien",
    "Donec id lacus nec leo ullamcorper auctor auctor eu elit",
    "Curabitur imperdiet urna nec ligula tristique pulvinar",
    "Proin euismod nisi vel risus tempor, condimentum sodales ipsum vehicula",
    "Praesent sit amet justo sed metus lacinia congue",
    "Nunc ut neque vel arcu dictum ornare eget vitae erat",
    "Etiam nec sem eget ipsum ullamcorper auctor sit amet vitae nulla",
    "Sed id lorem id velit tincidunt semper eu ac dui",
    "Sed nec lorem sagittis, elementum odio eget, vehicula quam",
    "Donec non magna mollis, sollicitudin justo id, lacinia justo",
    "In ullamcorper elit pretium tincidunt ultrices",
    "Quisque blandit velit ut erat iaculis, quis tristique massa volutpat",
    "Sed eu nisi rutrum, faucibus eros vel, hendrerit nisi",
    "Morbi pretium risus ac libero posuere ultricies",
    "Maecenas varius urna quis consequat accumsan",
    "Suspendisse luctus est et magna lacinia, quis placerat ligula aliquet",
    "Nullam bibendum lacus ultrices, cursus ipsum at, euismod nunc",
    "Fusce ac metus feugiat, sodales tellus at, tincidunt leo",
    "Sed tempor nulla a eleifend tempor",
    "Nulla porttitor dui at sollicitudin porta",
    "Phasellus ut odio sed magna varius facilisis ut quis diam",
    "Cras quis neque ut mi iaculis fringilla",
    "Ut posuere enim ac ante laoreet commodo",
    "Proin convallis nulla eu arcu consequat, id pellentesque nibh ultrices",
    "Mauris iaculis nulla nec eros accumsan suscipit",
    "Suspendisse vel urna eu sem commodo viverra",
    "Nunc eu neque pretium, adipiscing enim ut, bibendum urna",
    "Maecenas et metus et ligula luctus faucibus",
    "Vivamus ullamcorper dui nec diam gravida, sed semper mi tristique",
    "Suspendisse adipiscing nibh at lacus condimentum, et fermentum ante elei",
    "Donec blandit elit id libero consectetur, nec congue est hendrerit",
    "Integer ac quam vel erat tincidunt rhoncus ut ac elit",
    "Sed et erat a mauris convallis pretium non in mi",
    "Nam sed nunc et ante rhoncus interdum ut eu odio",
    "Phasellus condimentum purus eu libero rhoncus vehicula",
    "Vivamus luctus tellus sit amet sem pellentesque placerat at ac lorem",
    "Nulla pellentesque justo ut urna tempus, sed ultrices tortor tempor",
    "Integer ut ligula iaculis, pellentesque tellus non, condimentum tellus",
    "Mauris volutpat tellus in diam lobortis tempor",
    "Fusce nec felis id erat fermentum rhoncus",
    "Vestibulum eget erat et dui sollicitudin semper",
]


class ContentGen(object):
    """Content generator with 'Loren ipsum' texts and random numbers"""

    def __init__(self, random_instance=None):
        if random_instance is not None:
            self._random = random_instance
        else:
            self._random = random.Random()

    def get_text(self, max_len):
        phrase = self.get_in_list(_phrases)

        if len(phrase) > max_len:
            return phrase[0:self.get_int(1, max_len)]

        return phrase

    def get_list_subset(self, list):
        options = []
        for i in range(self.get_int(1, len(list))):
            options.append(self.get_in_list(list))

        return set(options)

    def get_in_list(self, list):
        return list[self.get_int(0, len(list)-1)]

    def get_float(self, start, end):
        return self._random.uniform(float(start), float(end))

    def get_date(self, start=None, end=None):
        if start is None:
            start = self._get_default_start_date()

        end = end if end is not None else self._get_default_end_date()

        td_diff = end - start if start <= end else start - end
        return start + timedelta(self.get_int(0, td_diff.days))

    def _get_default_start_date(self):
        return date(2006, 1, 1)

    def _get_default_end_date(self):
        return date(2020, 1, 1)

    def get_datetime(self, start=None, end=None):
        if start is None:
            start = self._get_default_start_datetime()

        if end is None:
            end = self._get_default_end_datetime()

        td_diff = end - start if start <= end else start - end
        return start + timedelta(
            self.get_int(0, td_diff.days),
            self.get_int(0, td_diff.seconds)
        )

    def _get_default_start_datetime(self):
        return datetime(2006, 1, 1, 0, 0, 0)

    def _get_default_end_datetime(self):
        return datetime(2020, 1, 1, 0, 0, 0)

    def get_int(self, start, end):
        return self._random.randint(start, end)


class OptionsParser(object):
    """
    Parse a string of options separated with comma.
    Examples:
    p = OptionsParser()

    p.parse("'a','b'").options # Results: [ "a" , "b" ]

    p.parse("'a','b','c'''").options # Results: [ "a" , "b" , "c'" ]

    p.parse("'a','b'',','c'''").options # Results: [ "a" , "b'," , "c'" ]
    """

    # Grammar:
    #   OPTIONS = COMMA OPTION | OPTION
    #   OPTION = QUOTE OPTION_VALUE QUOTE
    #   OPTION_VALUE = PARTIAL_OPTION | QUOTE QUOTE | COMMA
    #   QUOTE = '''
    #   PARTIAL_VALUE = '[^',]'
    #   COMMA = ','
    tokens_regex = {
        "QUOTE": r"^(')",
        "COMMA": r"(\,)",
        "PARTIAL_OPTION": r"^([^'\,]+)",
    }

    def __init__(self):
        self.options = []
        self._result_tokens = []
        self._token_position = 0
        self._parsed_option = ""

    def parse(self, str_options):
        self._tokenize(str_options)
        self._parse()
        return self

    def _tokenize(self, str_options):
        self._result_tokens = []
        i = 0
        while (i < len(str_options)):
            increment = None
            for token, pattern in self.tokens_regex.iteritems():
                m = re.search(pattern, str_options[i:])
                if m is not None:
                    self._result_tokens.append((token, m.group(1), i+1))
                    increment = len(m.group(0))
                    break

            if increment is None:
                msg = "Unexpected value on parse enum options: \"{0}\""\
                    .format(str_options[i:])

                raise ValueError(msg)

            i = i + increment

    def _parse(self):
        "Starts the Top-down parser"
        self.options = []
        self._token_position = 0
        if not self._parse_options():
            msg = "Unexpected token '{0}', value '{1}', position: {2}".format(
                self._get_actual_token(),
                self._get_actual_token_value(),
                self._get_actual_token_str_position()
            )
            raise ValueError(msg)

    def _parse_options(self):
        "Parse grammar 'OPTIONS = COMMA OPTION | OPTION'"

        while self._get_actual_token() is not None:
            tp = self._token_position
            if self._parse_comma() and self._parse_option():
                continue

            self._token_position = tp
            if self._parse_option():
                continue

            self._token_position = tp
            break

        # It is OK If all Tokens was parsed
        if self._get_actual_token() is None:
            return True

        return False

    def _parse_option(self):
        "Parse grammar 'QUOTE OPTION_VALUE QUOTE'"
        tp = self._token_position
        if self._parse_quote() \
                and self._parse_option_value() \
                and self._parse_quote():
            return True

        self._token_position = tp
        return False

    def _parse_option_value(self):
        "Parse grammar 'OPTION_VALUE = PARTIAL_OPTION | QUOTE QUOTE | COMMA'"

        self._parsed_option = ""
        parsed = False  # Change to True if something was parsed
        while True:
            tp = self._token_position
            if self._parse_quote() and self._parse_quote(True):
                parsed = True
                continue

            self._token_position = tp
            if self._parse_partial_option(True):
                parsed = True
                continue

            self._token_position = tp
            if self._parse_comma(True):
                parsed = True
                continue

            self._token_position = tp
            break

        self.options.append(self._parsed_option)
        return parsed

    def _parse_partial_option(self, add_value=False):
        "Parse PARTIAL_OPTION token"

        if self._get_actual_token() == "PARTIAL_OPTION":
            if add_value:
                self._parsed_option += self._get_actual_token_value()

            self._token_position += 1
            return True

        return False

    def _parse_quote(self, add_value=False):
        "Parse QUOTE token"

        if self._get_actual_token() == "QUOTE":
            if add_value:
                self._parsed_option += self._get_actual_token_value()

            self._token_position += 1
            return True

        return False

    def _parse_comma(self, add_value=False):
        "Parse COMMA token"

        if self._get_actual_token() == "COMMA":
            if add_value:
                self._parsed_option += self._get_actual_token_value()

            self._token_position += 1
            return True

        return False

    def _get_actual_token(self):
        try:
            return self._result_tokens[self._token_position][0]
        except Exception, e:
            return None

    def _get_actual_token_value(self):
        try:
            return self._result_tokens[self._token_position][1]
        except Exception, e:
            return None

    def _get_actual_token_str_position(self):
        try:
            return self._result_tokens[self._token_position][2]
        except Exception, e:
            return None


class OutputProgress(object):
    """
    Show progress acording with a size (param progress_size)
    Ex:
    o = OutputProgress(100, sys.stdout.write) # All dots will be written in the screen.
    o() # This will print (using sys.stdout.write) a dots quantity related with 100.

    OBS: Raise an StandardError if number of calls exceed progress_size parameter.
    """

    line_size = 50
    lines = 10

    # Number of calls and actual dots, respectively.
    _calls_counter = 0
    _actual_dots = 0

    def __init__(self, progress_size, callback):
        self.progress_size = progress_size
        self._callback = callback

    def reset(self):
        self._calls_counter = 0
        self._actual_dots = 0

    def __call__(self):
        # The number of calls does'n exceed progres_size
        if self._calls_counter + 1 > self.progress_size:
            raise StandardError("Number of calls exhausted")

        self._calls_counter += 1
        self._print_dots()

    def _print_dots(self):
        total_dots = self.line_size * self.lines
        new_dots = int(self._calls_counter * total_dots / self.progress_size)
        
        self._call_callback(new_dots - self._actual_dots)

        self._actual_dots = new_dots


    def _call_callback(self, diff):
        old_line = int(self._actual_dots / self.line_size)

        for c in range(1, diff+1):
            self._callback(".")

            # Show percent
            act_line = int((self._actual_dots + c) / self.line_size)
            if act_line > old_line:
                self._show_percent(self._actual_dots + c)
                old_line = act_line

    def _show_percent(self, dots):
        self._callback(
            " %.0f%%" % (float(dots) / (self.line_size * self.lines) * 100)
        )

        self._callback(linesep)

