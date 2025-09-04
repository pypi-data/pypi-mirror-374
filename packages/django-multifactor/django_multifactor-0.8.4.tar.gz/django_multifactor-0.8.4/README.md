# ![django-multifactor - Easy multi-factor authentication for Django](https://raw.githubusercontent.com/oliwarner/django-multifactor/master/logo3.png)

Probably the easiest multi-factor for Django. Ships with standalone views, opinionated defaults 
and a very simple integration pathway to retrofit onto mature sites. Supports [FIDO2/WebAuthn](https://en.wikipedia.org/wiki/WebAuthn) and [TOTP authenticators](https://en.wikipedia.org/wiki/Time-based_One-time_Password_algorithm), with removable fallback options for email, SMS, carrier pigeon, or whatever other token exchange you can think of. U2F has been removed in 0.6.

This is ***not*** a passwordless authentication system. django-multifactor is a second layer of defence.

[![PyPI version](https://badge.fury.io/py/django-multifactor.svg)](https://badge.fury.io/py/django-multifactor)

FIDO2/WebAuthn is the big-ticket item for MFA. It allows the browser to interface with a myriad of biometric and secondary authentication factors.

 * **Security keys** (Firefox 60+, Chrome 67+, Edge 18+),
 * **Windows Hello** (Firefox 67+, Chrome 72+ , Edge) ,
 * **Apple's Touch ID** (Chrome 70+ on Mac OS X ),
 * **android-safetynet** (Chrome 70+)
 * **NFC devices using PCSC** (Not Tested, but as supported in fido2)

# Python and Django Support
This project targets modern stacks, officially supporting Python 3.8+ and Django 3.2+. Please refer to the [Django documentation](https://docs.djangoproject.com/en/dev/faq/install/) for more

| **Python/Django** | **2.2** |**3.2** | **4.0** | **4.1** | **4.2** | **5.0** | **5.1** | **5.2** |
|-------------------|---------|--------|---------|---------|---------|---------|---------|---------|
| 3.8               | Y       | Y      | Y       | Y       | N/A     | N/A     | N/A     | N/A     |
| 3.9               | Y       | Y      | Y       | Y       | N/A     | N/A     | N/A     | N/A     |
| 3.10              | N       | Y      | Y       | Y       | N/A     | Y       | Y       | Y       |
| 3.11              | N       | N      | N       | Y       | Y       | Y       | Y       | Y       |
| 3.12              | N       | N      | N       | N       | Y       | Y       | Y       | Y       |
| 3.13              | N       | N      | N       | N       | N       | N       | Y       | Y       |

## Installation:

Install the package:

    pip install django-multifactor

Add `multifactor` to `settings.INSTALLED_APPS` and override whichever setting you need.

    MULTIFACTOR = {
        'LOGIN_CALLBACK': False,             # False, or dotted import path to function to process after successful authentication
        'RECHECK': True,                     # Invalidate previous authorisations at random intervals
        'RECHECK_MIN': 60 * 60 * 3,          # No rechecks before 3 hours
        'RECHECK_MAX': 60 * 60 * 6,          # But within 6 hours
    
        'FIDO_SERVER_ID': 'example.com',     # Server ID for FIDO request
        'FIDO_SERVER_NAME': 'Django App',    # Human-readable name for FIDO request
        'TOKEN_ISSUER_NAME': 'Django App',   # TOTP token issuing name (to be shown in authenticator)
        
        # Optional Keys - Only include these keys if you wish to deviate from the default actions
        'LOGIN_MESSAGE': '<a href="{}">Manage multifactor settings</a>.',  # {OPTIONAL} When set overloads the default post-login message.
        'SHOW_LOGIN_MESSAGE': False,  # {OPTIONAL} <bool> Set to False to not create a post-login message
    }

Ensure that [`django.contrib.messages`](https://docs.djangoproject.com/en/2.2/ref/contrib/messages/) is installed.

Include `multifactor.urls` in your URLs. You can do this anywhere but I suggest somewhere similar to your login URLs, or underneath them, eg:

    urlpatterns = [
        path('admin/multifactor/', include('multifactor.urls')),
        path('admin/', admin.site.urls),
        ...
    ]


And don't forget to run a `./manage.py collectstatic` before restarting Django.


## Usage

At this stage any authenticated user can add a secondary factor to their account by visiting (eg) `/admin/multifactor/`, but no view will *require* secondary authentication. django-multifactor gives you granular control to conditionally require certain users need a secondary factor on certain views. This is accomplished through the `multifactor.decorators.multifactor_protected` decorator.

    from multifactor.decorators import multifactor_protected

    @multifactor_protected(factors=0, user_filter=None, max_age=0, advertise=False)
    def my_view(request):
        ...

 - `factors` is the minimum number of active, authenticated secondary factors. 0 will mean users will only be prompted if they have keys. It can also accept a lambda/function with one request argument that returns a number. This allows you to tune whether factors are required based on custom logic (eg if local IP return 0 else return 1)
 - `user_filter` can be a dictionary to be passed to `User.objects.filter()` to see if the current user matches these conditions. If empty or None, it will match all users.
 - `max_age=600` will ensure the the user has authenticated with their secondary factor within 10 minutes. You can tweak this for higher security at the cost of inconvenience.
 - `advertise=True` will send an info-level message via django.contrib.messages with a link to the main django-multifactor page that allows them to add factors for future use. This is useful to increase optional uptake when introducing multifactor to an organisation.


 You can also wrap entire branches of your URLs using [`django-decorator-include`](https://pypi.org/project/django-decorator-include/):

    from decorator_include import decorator_include
    from multifactor.decorators import multifactor_protected

    urlpatterns = [
        path('admin/multifactor/', include('multifactor.urls')),
        path('admin/', decorator_include(multifactor_protected(factors=1), admin.site.urls)),
        ...
    ]


## Don't want to allow TOTP? Turn them off.

You can control the factors users can pick from in `settings.MULTIFACTOR`:

    MULTIFACTOR = {
        # ...
        'FACTORS': ['FIDO2', 'TOTP'],  # <- this is the default
    }


## Extending OTP fallback with custom transports

`django-multifactor` has a fallback system that allows the user to be contacted via a number of sub-secure methods **simultaneously**. The rationale is that if somebody hacks their email account, they'll still know something is going on when they get an SMS. Providing sane options for your users is critical to security here. A poor fallback can undermine otherwise solid factors.

The included fallback uses `user.email` to send an email. This now sends as plain+HTML. You can send just plain by setting `settings.MULTIFACTOR.HTML_EMAIL` to `False`.

You can plumb in additional functions to carry the OTP message over any
other system you like. The function should look something like:

    def send_carrier_pigeon(user, message):
        bird = find_bird()
        bird.attach(message)
        bird.send(user.address)
        return True  # to indicate it sent

Then hook that into `settings.MULTIFACTOR`:

    MULTIFACTOR = {
        # ...
        'FALLBACKS': {
            'email': (lambda user: user, 'multifactor.factors.fallback.send_email'),
            'pigeon': (lambda user: user.address, 'path.to.send_carrier_pigeon'),
        }
    }

Now if the user selects the fallback option, they will receive an email *and* a pigeon. You can remove email by omitting that line. You can disable fallback entirely by setting FALLBACKS to an empty dict.


## Conditional bypass

It's sometimes useful to be able to be able to conditionally bypass multifactor requirements. You might be in local testing, you might be in automated testing or impersonating other users. Deactivating a security layer has obvious risks but that's between you and your gods.

`settings.MULTIFACTOR.BYPASS` accepts a single path to a function accepting a request. If that returns True, multifactor will bypass its normal checks on a page.

    MULTIFACTOR = {
        # ...
        'BYPASS': 'path.to.bypass_when_impersonating'
    }

These are relatively easy to implement:

    def bypass_when_impersonating(request):
        from loginas.utils import is_impersonated_session
        if is_impersonated_session(request):
            return True

    def bypass_when_debug(request):
        from django.config import settings
        return settings.DEBUG


## UserAdmin integration

It's often useful to monitor which of your users is using django-multifactor and, in emergencies, critical to be able to turn their secondary factors off. We ship a opinionated mixin class that you can add to your existing UserAdmin definition.

    from multifactor.admin import MultifactorUserAdmin

    @admin.register(User)
    class StaffAdmin(UserAdmin, MultifactorUserAdmin):
        ...

It adds a column to show if that user has active factors, a filter to just show those with or without, and an inline to allow admins to turn certain keys off for their users.


## Branding

If you want to use the styles and form that django-multifactor supplies, your users may think they're on another site. To help there is an empty placeholder template `multifactor/brand.html` that you can override in your project. This slots in just before the h1 title tag and has `text-align: centre` as standard.

If you use HTML emails for your email fallback, you can create a `multifactor/email.html` template (accepting user, message context variables).

You can use this to include your product logo, or an explanation.
