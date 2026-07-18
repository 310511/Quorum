import uuid

import pytest

from dirty_equals import FunctionCheck, IsEmail, IsJson, IsUUID


@pytest.mark.parametrize(
    'other,dirty',
    [
        (uuid.uuid4(), IsUUID()),
        (uuid.uuid4(), IsUUID),
        (uuid.uuid4(), IsUUID(4)),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID(4)),
        ('edf9f29e45c7431c99db28ea44df9785', IsUUID(4)),
        (uuid.uuid3(uuid.UUID('edf9f29e-45c7-431c-99db-28ea44df9785'), 'abc'), IsUUID),
        (uuid.uuid3(uuid.UUID('edf9f29e-45c7-431c-99db-28ea44df9785'), 'abc'), IsUUID(3)),
        (uuid.uuid1(), IsUUID(1)),
        (str(uuid.uuid1()), IsUUID(1)),
        ('ea9e828d-fd18-3898-99f3-5a46dbcee036', IsUUID(3)),
    ],
)
def test_is_uuid_true(other, dirty):
    assert other == dirty


@pytest.mark.parametrize(
    'other,dirty',
    [
        ('foobar', IsUUID()),
        ([1, 2, 3], IsUUID()),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID(5)),
        (uuid.uuid3(uuid.UUID('edf9f29e-45c7-431c-99db-28ea44df9785'), 'abc'), IsUUID(4)),
        (uuid.uuid1(), IsUUID(4)),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID(1)),
        ('ea9e828d-fd18-3898-99f3-5a46dbcee036', IsUUID(4)),
    ],
)
def test_is_uuid_false(other, dirty):
    assert other != dirty


def test_is_uuid_false_repr():
    is_uuid = IsUUID()
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(*)'


def test_is_uuid4_false_repr():
    is_uuid = IsUUID(4)
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(4)'


@pytest.mark.parametrize('json_value', ['null', '"xyz"', '[1, 2, 3]', '{"a": 1}'])
def test_is_json_any_true(json_value):
    assert json_value == IsJson()
    assert json_value == IsJson


def test_is_json_any_false():
    is_json = IsJson()
    with pytest.raises(AssertionError):
        assert 'foobar' == is_json
    assert str(is_json) == 'IsJson(*)'


@pytest.mark.parametrize(
    'json_value,expected_value',
    [
        ('null', None),
        ('"xyz"', 'xyz'),
        ('[1, 2, 3]', [1, 2, 3]),
        ('{"a": 1}', {'a': 1}),
    ],
)
def test_is_json_specific_true(json_value, expected_value):
    assert json_value == IsJson(expected_value)
    assert json_value == IsJson[expected_value]


def test_is_json_invalid():
    assert 'invalid json' != IsJson
    assert 123 != IsJson
    assert [1, 2] != IsJson


def test_is_json_kwargs():
    assert '{"a": 1, "b": 2}' == IsJson(a=1, b=2)
    assert '{"a": 1, "b": 3}' != IsJson(a=1, b=2)


def test_is_json_specific_false():
    is_json = IsJson([1, 2, 3])
    with pytest.raises(AssertionError):
        assert '{"a": 1}' == is_json
    assert str(is_json) == 'IsJson([1, 2, 3])'


def test_equals_function():
    func_argument = None

    def foo(v):
        nonlocal func_argument
        func_argument = v
        return v % 2 == 0

    assert 4 == FunctionCheck(foo)
    assert func_argument == 4
    assert 5 != FunctionCheck(foo)


def test_equals_function_fail():
    def foobar(v):
        return False

    c = FunctionCheck(foobar)

    with pytest.raises(AssertionError):
        assert 4 == c

    assert str(c) == 'FunctionCheck(foobar)'


def test_json_both():
    with pytest.raises(TypeError, match='IsJson requires either an argument or kwargs, not both'):
        IsJson(1, a=2)


# IsEmail tests
@pytest.mark.parametrize(
    'email,dirty',
    [
        ('user@example.com', IsEmail()),
        ('user@example.com', IsEmail),
        ('test.email+tag@domain.co.uk', IsEmail()),
        ('user123@test-domain.org', IsEmail()),
        ('a@b.co', IsEmail()),
        ('user_name@domain.info', IsEmail()),
        ('user.name@example.com', IsEmail(domain='example.com')),
        ('test@domain.org', IsEmail(domain='domain.org')),
    ],
)
def test_is_email_true(email, dirty):
    assert email == dirty


@pytest.mark.parametrize(
    'email,dirty',
    [
        ('invalid-email', IsEmail()),
        ('user@', IsEmail()),
        ('@domain.com', IsEmail()),
        ('user@domain', IsEmail()),
        ('user.domain.com', IsEmail()),
        ('user@domain.c', IsEmail()),
        ('user@.com', IsEmail()),
        ('user@domain.', IsEmail()),
        (123, IsEmail()),
        (None, IsEmail()),
        ([], IsEmail()),
        ('user@example.com', IsEmail(domain='other.com')),
        ('user@domain.org', IsEmail(domain='example.com')),
    ],
)
def test_is_email_false(email, dirty):
    assert email != dirty


def test_is_email_repr():
    is_email = IsEmail()
    with pytest.raises(AssertionError):
        assert 'invalid-email' == is_email
    assert str(is_email) == 'IsEmail(*)'


def test_is_email_domain_repr():
    is_email = IsEmail(domain='example.com')
    with pytest.raises(AssertionError):
        assert 'user@other.com' == is_email
    assert str(is_email) == "IsEmail('example.com')"


def test_is_email_edge_cases():
    # Test empty string
    assert '' != IsEmail()
 
    # Test very long email
    long_email = 'a' * 50 + '@' + 'b' * 50 + '.com'
    assert long_email == IsEmail()
 
    # Test email with numbers and special chars
    assert 'user123+tag@domain-name.co.uk' == IsEmail()
 
    # Test case sensitivity in domain matching
    assert 'user@Example.Com' != IsEmail(domain='example.com')
    assert 'user@example.com' == IsEmail(domain='example.com')


def test_is_email_domain_filtering():
    # Test exact domain matching
    assert 'user@example.com' == IsEmail(domain='example.com')
    assert 'user@example.org' != IsEmail(domain='example.com')
 
    # Test subdomain handling
    assert 'user@sub.example.com' != IsEmail(domain='example.com')
    assert 'user@sub.example.com' == IsEmail(domain='sub.example.com')
