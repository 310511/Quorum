import re

import pytest
from pydantic import BaseModel

from outlines import types
from outlines.types.dsl import to_regex


@pytest.mark.parametrize(
    "custom_type,test_string,should_match",
    [
        (types.locale.us.phone_number, "12", False),
        (types.locale.us.phone_number, "(123) 123-1234", True),
        (types.locale.us.phone_number, "123-123-1234", True),
        (types.locale.us.zip_code, "12", False),
        (types.locale.us.zip_code, "12345", True),
        (types.locale.us.zip_code, "12345-1234", True),
        (types.isbn, "ISBN 0-1-2-3-4-5", False),
        (types.isbn, "ISBN 978-0-596-52068-7", True),
        (types.isbn, "ISBN-13: 978-0-596-52068-7", True),
        (types.isbn, "978 0 596 52068 7", True),
        (types.isbn, "9780596520687", True),
        (types.isbn, "ISBN-10: 0-596-52068-9", True),
        (types.isbn, "0-596-52068-9", True),
        (types.email, "eitan@gmail.com", True),
        (types.email, "99@yahoo.com", True),
        (types.email, "eitan@.gmail.com", False),
        (types.email, "myemail", False),
        (types.email, "eitan@gmail", False),
        (types.email, "eitan@my.custom.domain", True),
        (types.integer, "-19", True),
        (types.integer, "19", True),
        (types.integer, "019", False),
        (types.integer, "1.9", False),
        (types.integer, "a", False),
        (types.boolean, "True", True),
        (types.boolean, "False", True),
        (types.boolean, "true", False),
        (types.number, "10", True),
        (types.number, "10.9", True),
        (types.number, "10.9e+3", True),
        (types.number, "10.9e-3", True),
        (types.number, "a", False),
        (types.date, "2022-03-23", True),
        (types.date, "2022-03-32", False),
        (types.date, "2022-13-23", False),
        (types.date, "32-03-2022", False),
        (types.time, "01:23:59", True),
        (types.time, "01:23:61", False),
        (types.time, "01:61:59", False),
        (types.time, "24:23:59", False),
        (types.sentence, "The temperature is 23.5 degrees !", True),
        (types.sentence, "Did you earn $1,234.56 last month  ?", True),
        (types.sentence, "The #1 player scored 100 points .", True),
        (types.sentence, "Hello @world, this is a test!", True),
        (types.sentence, "invalid sentence.", False),
        (types.sentence, "Invalid sentence", False),
        (types.paragraph, "This is a paragraph!\n", True),
        (types.paragraph, "Line1\nLine2", False),
        (types.paragraph, "One sentence. Two sentences.\n\n", True),
        (types.paragraph, "One sentence. invalid sentence.", False),
        (types.paragraph, "One sentence. Invalid sentence\n", False),
        # SHA-256 hash tests
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", True),  # Empty string SHA-256
        (types.hash_sha256, "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae", True),  # "foo" SHA-256
        (types.hash_sha256, "A665A45920422F9D417E4867EFDC4FB8A04A1F3FFF1FA07E998E86F7F7A27AE3", True),  # Uppercase
        (types.hash_sha256, "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3", True),  # Lowercase
        (types.hash_sha256, "AbCdEf1234567890AbCdEf1234567890AbCdEf1234567890AbCdEf1234567890", True),  # Mixed case
        (types.hash_sha256, "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", True),  # All valid hex chars
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85", False),  # 63 chars (too short)
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555", False),  # 65 chars (too long)
        (types.hash_sha256, "", False),  # Empty string
        (types.hash_sha256, "g3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", False),  # Invalid char 'g'
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85z", False),  # Invalid char 'z'
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85@", False),  # Special char
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85 ", False),  # With space
        (types.hash_sha256, " e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", False),  # Leading space
        (types.hash_sha256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 ", False),  # Trailing space
        (types.hash_sha256, "123", False),  # Too short
        (types.hash_sha256, "abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz12", False),  # Invalid chars
    ],
)
def test_type_regex(custom_type, test_string, should_match):
    class Model(BaseModel):
        attr: custom_type

    schema = Model.model_json_schema()
    assert schema["properties"]["attr"]["type"] == "string"
    regex_str = schema["properties"]["attr"]["pattern"]
    does_match = re.fullmatch(regex_str, test_string) is not None
    assert does_match is should_match

    regex_str = to_regex(custom_type)
    does_match = re.fullmatch(regex_str, test_string) is not None
    assert does_match is should_match


@pytest.mark.parametrize(
    "custom_type,test_string,should_match",
    [
        (types.airports.IATA, "CDG", True),
        (types.airports.IATA, "XXX", False),
        (types.countries.Alpha2, "FR", True),
        (types.countries.Alpha2, "XX", False),
        (types.countries.Alpha3, "UKR", True),
        (types.countries.Alpha3, "XXX", False),
        (types.countries.Numeric, "004", True),
        (types.countries.Numeric, "900", False),
        (types.countries.Name, "Ukraine", True),
        (types.countries.Name, "Wonderland", False),
        (types.countries.Flag, "🇿🇼", True),
        (types.countries.Flag, "🤗", False),
    ],
)
def test_type_enum(custom_type, test_string, should_match):
    type_name = custom_type.__name__

    class Model(BaseModel):
        attr: custom_type

    schema = Model.model_json_schema()
    assert isinstance(schema["$defs"][type_name]["enum"], list)
    does_match = test_string in schema["$defs"][type_name]["enum"]
    assert does_match is should_match

    does_match = test_string in custom_type.__members__
    assert does_match is should_match
