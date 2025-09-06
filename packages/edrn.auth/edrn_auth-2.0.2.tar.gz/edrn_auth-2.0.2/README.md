# 🔑 EDRN Auth

This is a [Django](https://www.djangoproject.com) app (that is, [Python](https://www.python.org/) package) that provides authentication and authorization for the [portal for the Early Detection Research Network](https://edrn.nci.nih.gov/) and other applications. You use it with the [Wagtail CMS](https://www.wagtail.org/).

It currently works with:

- Wagtail versions less than 7 but greater than 5
- [Django](https://www.djangoproject.com) versions less than 6 but greater than 4
- [Python](https://www.python.org/) versions 3.11 or greater (but probably less than 4)


## 💁 How to Use It

Simply add `edrn.auth` to your list of dependencies and install it (such as in `requirements.txt` or `pyproject.toml`'s `dependencies)`), then add it your site's `INSTALLED_APPS`. Next you'll want to import `edrn.auth`'s URL patterns with something like this in your own `urls.py`:
```python
from edrn.auth.urls import urlpatterns as edrn_auth_urlpatterns
…
urlpatterns = edrn_auth_urlpatterns + [
    # your own URL patterns
]
```

This will give you several URL paths:

- `_util/login/` for logging in, overriding the Wagtail frontend login template, with the full U.S. government boilerplate and the three login alternatives (portal, LabCAS, DMCC "secure" site)
- `_util/portal-login` (named `portal_login`), for logging in, with the full U.S. government boilerplate but only portal login (LabCAS and DMCC "secure" site are not mentioend)
- `logout/` (named `logout`), for logging out
- `authentication-test` (named `authentication-test`), for testing if credentials are valid, using HTTP Basic

This gives a template tag library which you can use by first doing `{% load edrn_auth_tags %}`; it provides a single inclusion tag, `edrn_personal_links`, which generates the "personal links":

- A "Hello, {{name}}" if you're logged in (or just "You're logged in" if your name's unknown), plus a "Log out" link
- A "Log in" link if you're not logged in.

There are several utilities you can import from `edrn.auth.views`, which are described below.

### 🔐 `view_or_basicauth`

`view_or_basicauth` is used as a decorator on a view along with a test function, `test_func`. The `test_func` is expected to receive a single argument, the Django `HTTPRequest.user`.

If the test function succeeds, the decorated view is returned. Otherwise, if HTTP Basic authentication is present and succeeds, the decorated view is returned.

Otherwise, the HTTP "unauthorized" status is returned with an HTTP Basic challenge.


### 🔒 `logged_in_or_basicauth`

The decorator `logged_in_or_basicauth` just uses the above view with the `test_func` set to `user.is_authenticated`.


### 🔏`authentication_context`

The function `authentication_context` takes a Django `HTTPRequest` and based on its state, returns a dictionary with the following values:

- `authenticated`: `True` if there's an authenticated user present, `False` otherwise
- `logout`: The URL to visit to have the current user logout, if applicable
- `login`: The URL to visit to present a full login page (with the three alternative destinations, portal, LabCAS, and DMCC "secure" site)
- `portal_login`: The URL to visit to present the portal-only login page

This is intended to be used in `get_context` methods or views to provide handy links.


## 🪙 Changes

- 2.0.2 increased Wagtail support from `< 6` to `< 7`
- 2.0.1 increased Django support from `< 5` to `< 6`


## 🥖 Translations

This package hasn't be translated into any other languages aside from US English.


## 👏 Contributing

All of the developers of this package are expected to abide by our [Code of Conduct](https://github.com/EDRN/.github/blob/main/CODE_OF_CONDUCT.md). Do check it out! We don't take this lightly and we have high standards of our community. For information on how to contribute software to the Early Detection Research Network, check out our [contributor guidelines](https://github.com/EDRN/.github/blob/main/CONTRIBUTING.md).


## 🎈 Support

If you're experiencing issues, view to see if an issue's been filed (or file a fresh one) at our [issue tracker](https://github.com/EDRN/edrn.auth/issues). Or you can reach us [by email](mailto:edrn-ic@jpl.nasa.gov).


## 🪪 License

This package is licensed under the Apache License, version 2. See the `LICENSE.md` file for details.
