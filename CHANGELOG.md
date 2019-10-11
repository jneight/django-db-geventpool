# Changelog

## 3.2.0

- Removed support for django < 1.11
- Updated previous deprecation warnings

## 3.1.0

- Correct connection cleanup after disabling autocommit with `transaction.setautocommit(False)`

## 3.0.1

- Fix setup.py UnicodeDecodeError when installing with python 3.6

## 3.0.0

- psycopg2 is not installed by default, @mattbriancon


## 2

- Testing: Add support for Python 3 and Django 2, @stefankoegl
- Fixed error with undefined attribute "closed_in_transaction", @bmunoz89
- Working with django 1.11 LTS and 2.0

## Previous versions:

- Proper error handling for integer types, @gxx
- Ensure that close_connection property closes, even in the case of an error, @gxx
- Compatible with Python 3, @sumitalp
- Fixed self.pool must exist, @rajivm
- Fixed Postgis pool connection, @rajivm
