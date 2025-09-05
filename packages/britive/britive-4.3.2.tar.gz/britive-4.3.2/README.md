# Britive Python SDK

Pure Python implementation for interacting with the [Britive API](https://docs.britive.com/v1/docs/en/overview-britive-apis).

This package aims to wrap the Britive API for usage in Python development. For the most part it is a simple wrapper
(sending potentially bad parameters to the API) but there are a couple of places where liberties were taken to enhance
the developer/end user experience. Some APIs may also be combined into one Python method with a parameter if and where
it makes more sense to present the API that way.

This package supports Python versions `>= 3.9`.

## Installation

```sh
pip install britive
```

Or execute one of the following commands if you wish to pull directly from the Github repo instead of PyPi. Or navigate
to Releases and use the URL of the tarball release that is needed, if not the lastest.

```sh
pip install $(curl -s https://api.github.com/repos/britive/python-sdk/releases/latest \
    | jq -r '.assets[] | select(.content_type == "application/x-gzip") | .browser_download_url')

OR

pip install $(curl -s https://api.github.com/repos/britive/python-sdk/releases/latest \
    | grep "browser_download_url.*.tar.gz" | cut -d : -f 2,3 | tr -d \")
```

## Documentation

Each public method is documented with a docstring which provides details on what the method does, the parameters the
method accepts, and details about what is returned from the method.

Official API documentation can be found here: [Overview of Britive APIs](https://docs.britive.com/v1/docs/en/overview-britive-apis).

## Authentication

Authentication is handled solely via API tokens. The token must be provided in one of two methods.

1. Passed directly into the class constructor.
2. Injected as an environment variable into the execution context where this package is being run.
    1. The environment variable name must be `BRITIVE_API_TOKEN`.

> _As of `v2.5.0` a `Bearer` token can be provided as well._
> _A `Bearer` token is generated as part of an interactive login process and is temporary in nature._
> _This is to support the [Britive Python CLI](https://github.com/britive/python-cli/)._

All Britive API tokens are authenticated against a specific Britive tenant. The name of the tenant must be presented in
one of two methods.

1. Passed directly into the `Britive` class constructor.
2. Injected as an environment variable into the execution context where this package is being run.
    1. The environment variable name must be `BRITIVE_TENANT`.

> _In order to obtain the tenant name, reference the Britive URL used to log into the UI._
> _If the URL is `https://example.britive-app.com` then the tenant name will be `example`._

## Pagination

All pagination is handled by the package. The caller will never have to deal with paginated responses.

## Assumptions

* The caller has access to an active Britive tenant.
* The caller has been granted an API token and/or has the ability to generate an API token.
  * This can be either for a _User_ or _Service Identity_.
* No assumptions are made about the operating system or file system.
  * Nothing is persisted to disk.
    * The end user must persist responses to disk if and when that is required.

## Resource Coverage

The following Britive resources are supported with full CRUDL operations where appropriate, and additional actions where
they exist.

* Access Broker
* Access Builder
* Accounts
* Accounts (associated with an application/environment)
* API Tokens (for Users)
* Applications
* Audit Logs
* Environment
* Environment Groups
* Groups (associated with an application/environment)
* Identity Attributes
* Identity Providers
* My Access (access granted to the given identity (user or service))
* My Approvals
* My Requests
* My Resources (access granted to the given identity (user or service))
* My Secrets (access granted to the given identity (user or service))
* Notifications
* Permissions (associated with an application/environment)
* Profiles
* Reports
* SAML Settings
* Scans
* Security Policies
* Service Identities
* Service Identity Tokens
* System Announcement (aka banner)
* Tags (aka User Tags)
* Task Services
* Tasks
* Users

## Proxies

Under the covers, python [`requests`](https://github.com/psf/requests) is being used to communicate with the Britive API.
As such, any functionality of `requests` can be used, including setting an HTTP proxy.

* HTTP proxies will be set via environment variables.
  * `HTTP_PROXY`
  * `HTTPS_PROXY`
  * `NO_PROXY`
  * `http_proxy`
  * `https_proxy`
  * `no_proxy`

> _Standard HTTP proxy URLs should be utilized._
>
> _Examples:_
>
> * _Unauthenticated Proxy: `http://internalproxy.domain.com:8080`_
> * _Authenticated Proxy: `http://user:pass@internalproxy.domain.com:8080`_

## Custom TLS Certificates

Setting custom TLS certificates functionality of `requests` can also be used.

* Certificate bundles can be set via environment variables.
  * `REQUESTS_CA_BUNDLE`
  * `CURL_CA_BUNDLE` _(used as a fallback)_
  * `PYBRITIVE_CA_BUNDLE` _(specific to the Britive Python SDK)_

> _The values of these environment variables must be a path to a directory of certificates or a specific certificate._
>
> _Example:_
> _`/path/to/certfile`_

### Platform Examples

#### linux/macos

```sh
export REQUESTS_CA_BUNDLE="/usr/local/corp-proxy/cacert.pem"
```

#### windows

__powershell:__

```pwsh
$env:REQUESTS_CA_BUNDLE = "C:\Users\User\AppData\Local\corp-proxy\cacert.pem"
```

__cmd:__

```bat
set REQUESTS_CA_BUNDLE="C:\Users\User\AppData\Local\corp-proxy\cacert.pem"
```

## Examples

### Importing

This should be the only class that is required for import.

```python
from britive.britive import Britive
```

Optionally, the various exceptions that this package raises can be imported as well, e.g.

```python
from britive import exceptions
```

Then specific exception(s) could be referenced as demonstrated below:

```python
try:
    something()
except exceptions.TokenMissingError():
    handle()
```

### List All Users

```python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.identity_management.users.list(), indent=2, default=str))
```

### Provide Needed Authentication Information in the Script

```python
from britive.britive import Britive
import json

britive = Britive(tenant='example', token='...') # source token and tenant locally (not from environment variables)

print(json.dumps(britive.identity_management.users.list(), indent=2, default=str))
```

### Create API Token for a Service Identity

```python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.identity_management.service_identity_tokens.create(service_identity_id='abc123'), indent=2, default=str))
```

### Run a Report (JSON and CSV output)

```python
from britive.britive import Britive
import json

britive = Britive()  # source needed data from environment variables

print(json.dumps(britive.reports.run(report_id='abc123'), indent=2, default=str))

with open('file.csv', 'w') as f:
    f.write(britive.reports.run(report_id='abc123', csv=True))
```

### Create a Profile Policy (profiles v2/enhanced profiles)

The commands below will create a policy on a profile that allows `user@domain.com` to check out the profile but only if
`approver@domain.com` approves that request within 10 minutes.

```python
from britive.britive import Britive

b = Britive()

policy = b.application_management.profiles.policies.build(
    name='example',
    users=['user@domain.com'],
    approval_notification_medium='Email',
    approver_users=['approver@domain.com'],
    time_to_approve=10
)

b.application_management.profiles.policies.create(profile_id='...', policy=policy)
```
