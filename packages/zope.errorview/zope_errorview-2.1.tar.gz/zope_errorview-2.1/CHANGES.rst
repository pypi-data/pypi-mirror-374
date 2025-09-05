=========
 CHANGES
=========

2.1 (2025-09-04)
================

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


2.0 (2023-02-09)
================

- Drop support for Python 2.7, 3.4, 3.5, 3.6.

- Add support for Python 3.7, 3.8, 3.9, 3.10, 3.11.


1.2.0 (2018-01-15)
==================

- Remove the whitespace between the content-type and charset of the default
  error views. This is because in certain cases zope.publisher.http will parse
  the content type parameters and combine them back again without the
  whitespace. This fix makes things more predictable esp. in tests.

1.1 (2018-01-10)
================

- Additional fixes for Python 3 compatibility.

  NOTE: The error view base classes now set a Content-Type response header to
  "text/plain". If your error view subclassing from the zope.errorview classes
  return a response body other than "text/plain" you need to explicitly set
  the Content-Type in your views.

1.0.0 (2017-05-10)
==================

- Add support for Python 3.4, 3.5, 3.6 and PyPy.

- Fix typo in Dutch translation

0.11 (2011-06-28)
=================

- Added nl translations.

0.10 (2011-02-08)
=================

- Exception views do not by default provide ISystemErrorView anymore as it
  would result in duplicate log output. The mixin class still exists for
  writing custom error views that do provide ISystemErrorView.

0.9 (2011-01-20)
================

- Initial release.
