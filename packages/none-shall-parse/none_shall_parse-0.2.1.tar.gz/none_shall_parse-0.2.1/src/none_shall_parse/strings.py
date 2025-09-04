import base64
import hashlib
import itertools
import random
import re
import secrets
import string
import unicodedata

_control_chars = "".join(
    map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0))))
_re_control_char = re.compile("[%s]" % re.escape(_control_chars))
_re_combine_whitespace = re.compile(r"\s+")


def slugify(value, allow_unicode=False):
    """
    Maps directly to Django's slugify function.
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def random_16():
    return "".join(random.choices(string.ascii_letters + string.digits, k=16))


def to_human_string(s):
    """
    This replaces all tabs and newlines with spaces and removes all non-printing
    control characters.
    """
    if not isinstance(s, str):
        return s, False

    c = _re_combine_whitespace.sub(" ", s).strip()
    clean_string = _re_control_char.sub("", c)
    if clean_string == s:
        return s, False
    return clean_string, True


def is_quoted_string(s, strip=False):
    is_quoted = False
    result = s
    if not isinstance(s, str):
        return is_quoted, result

    if s[0] == s[-1]:
        if s[0] in ['"', "'"]:
            is_quoted = True
            if strip:
                if s[0] == "'":
                    result = s.strip("'")
                elif s[0] == '"':
                    result = s.strip('"')
    return is_quoted, result


def is_numeric_string(s, convert=False):
    is_numeric = False
    result = s
    f = None
    if not isinstance(s, str):
        return is_numeric, result
    try:
        f = float(s)
        is_numeric = True
    except ValueError:
        is_numeric = False

    if is_numeric and convert:
        result = int(f) if f.is_integer() else f

    return is_numeric, result


def custom_slug(s):
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", "", s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", "_", s)

    return s


def b64_encode(s):
    return base64.b64encode(s).decode("utf-8").strip("=")


def b64_decode(s):
    pad = "=" * (-len(s) % 4)
    return base64.b64decode(s + pad)


def calc_hash(*args):
    """
    Calculate a hash over the set of arguments.
    This is useful to compare models against each other for equality
    if the assumption is that if some combination of fields are equal, then
    the models represent equal ideas.
    """
    s = '_'.join(map(str, args))
    return hashlib.sha1(s.encode("utf-16")).hexdigest()


def generate_random_password(n=10):
    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(n))
        if (
                any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3
        ):
            break
    return password
