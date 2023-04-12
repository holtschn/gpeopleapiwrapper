# Google People API Wrapper

This python package provides a wrapper around the Google People API which allows you to programmatically access and
manage persons and groups in Google contacts.

## Usage

### Preconditions

Of course, you need to have a Google account to access and manage its contacts.

You will also need to set up a Google Cloud project and enable the People API. Please follow the instructions in the
documentation: https://developers.google.com/people/v1/getting-started.

You need to have Python >=3.9 installed. Pip can be used to install the package:

```shell
pip install gpeopleapiwrapper
```

### Authentication

Accessing the Google People API requires authentication using OAuth 2.0 and a manual consent to access the contacts
of your Google account.

For the authentication you need to obtain an OAuth client ID from the Google Cloud console:

1. Go to the Google Cloud console and select your project.
2. Open the "APIs & Services" menu and select "Credentials".
3. Click on the "Create credentials" button and select "OAuth client ID".
4. Choose "Desktop app" as the application type and enter a name for your OAuth client ID.
5. Click "Create" and you will be presented with a client ID and client secret.
6. Download the client secret as a JSON file and save it in your project directory.

The credentials file is used to initialize the Google People API Wrapper client:

```python
import json
from gpeopleapiwrapper import client as gp_client

with open("${client secret json file}", "r") as json_file:
    api_client_secret = json.load(json_file)

pc_client = gp_client.Client(api_client_secret)
```

On initialization, the client will open a browser window and ask you to log in to your Google account. As long as
your app is not verified by Google, you will have to manually consent to access your contacts and additionally confirm
that you "know the developer that invited you".

For further details on the authentication process, please refer to Google's documentation:
https://developers.google.com/workspace/guides/auth-overview

#### Refreshing the authentication

By default, the client runs through the same manual authentication flow each time it is initialised. You can get rid
of this manual process by storing the obtained credentials. This way, the client will be able to refresh the
authentication automatically.

To store the credentials, you need to pass a persistent implementation of a `CredentialsStore` on initialisation of
the client:

```python
import json

from gpeopleapiwrapper import auth as gp_auth
from gpeopleapiwrapper import client as gp_client

with open("${client secret json file}", "r") as json_file:
    api_client_secret = json.load(json_file)

pc_client = gp_client.Client(
    api_client_secret=api_client_secret,
    credentials_store=gp_auth.PickleFileCredentialsStore("${credentials pickle file}"))
```

The auth module provides a simple implementation of a credentials store using pickle files. You can also have your own 
credentials store by implementing the `CredentialsStore` interface.

### Retrieving contacts

Once you have authenticated, you can use the client to retrieve contacts from your selected Google account:

```python
import json
from gpeopleapiwrapper import client as gp_client

with open("${client secret json file}", "r") as json_file:
    credentials = json.load(json_file)
pc_client = gp_client.Client(credentials)

all_contacts = pc_client.get_all_persons([gp_client.PersonField.names, gp_client.PersonField.email_addresses])
```

The `get_all_persons` method returns a list of `PersonWrapper` objects. The `PersonWrapper` provides accessors to the
many fields of the person model from the Google People API. Each `PersonWrapper` object only contains the requested
fields of the contact. In the above example we requested the `names` and `email_addresses` only.

For a detailed explanation of the `field_mask` parameter, the available fields, and the underlying model of a `Person`,
please refer to the documentation of the Google People API:

* see https://developers.google.com/people/api/rest/v1/people/get#query-parameters for available fields
* see https://developers.google.com/people/api/rest/v1/people#Person for the underlying model

Please note that this libray remains incomplete, i.e. not all fields of the person model are supported yet.

### Creating contacts

To create a new contact you can use the `create_person` method:

```python
import json
from gpeopleapiwrapper import client as gp_client

with open("${client secret json file}", "r") as json_file:
    credentials = json.load(json_file)
pc_client = gp_client.Client(credentials)

created_contact = pc_client.create_person("Peter Tester", [gp_client.PersonField.names])
```

The `create_person` method returns a `PersonWrapper` object representing the newly created contact containing the
requested fields according to the given field mask.

Limiting the capabilities of the API itself this library creates new contacts with the unstructured name as the only
parameter. Populating the other fields of the contact requires subsequent updates of the contact.

### Updating contacts

To update an existing contact you first need to retrieve or create one. You can modify the `PersonWrapper` object
by the provided accessors and then update the contact using the `update_person` method:

```python
import json
from gpeopleapiwrapper import client as gp_client

with open("${client secret json file}", "r") as json_file:
    credentials = json.load(json_file)
pc_client = gp_client.Client(credentials)

created_contact = pc_client.create_person("Peter Tester", [gp_client.PersonField.email_addresses])
created_contact.email_addresses.append_email_address("Home", "peter.tester@gmail.com")
updated_contact = pc_client.update_person(created_contact, [gp_client.PersonField.names])
```

Please be aware that the library only allows you to update the fields you requested from the api by specifying a
field_mask.

### Managing contact groups

The library allows you to conveniently add and remove contacts from contact groups with the help of the
`add_member_to_group` and `remove_member_from_group` methods:

```python
import json
from gpeopleapiwrapper import client as gp_client

with open("${client secret json file}", "r") as json_file:
    credentials = json.load(json_file)
pc_client = gp_client.Client(credentials)

created_contact = pc_client.create_person("Peter Tester", [gp_client.PersonField.email_addresses])
pc_client.add_member_to_group("test", created_contact)
pc_client.remove_member_from_group("test", created_contact)
```

## Contribution

First of all: If you find any issues or would like to contribute to the project, do not hesitate to create a new issue
or a pull request on the GitHub repository.

### Project Setup for Development

There are multiple ways to set up the project for development and the following steps are just one of them.

1. initialize python virtual environment, i.e. change to project directory and create virtual environment
   ```shell
   python -m venv .venv
   ```
2. activate the virtual environment
   ```shell
   source .venv/bin/activate
   ```
3. install project dependencies
   ```shell
   pip install .
   ```
4. install test dependencies
   ```shell
   pip install ".[test,publish]"
   ```

### Running Code Checks and Tests

1. We use the `unittest` module for testing:
   ```shell
   python -m unittest
   ```

2. Sometimes we check the coverage of the unittests:
   ```shell
   coverage run -m unittest
   coverage html --include="gpeopleapiwrapper/*"
   ```

3. We use `pylama` for code checks:
   ```shell
   pylama --max-line-length 120 gpeopleapiwrapper
   ```

### Publishing

1. We use `build` to create the distribution packages:
   ```shell
   python -m build .
   ```

2. We use `twine` to upload the distribution packages to PyPI:
   ```shell
     python -m twine upload --repository pypi dist/*
   ```

## Remarks

This library is not affiliated with Google in any way. It is not an official library nor has any 
endorsement of Google. It is just a personal project.

This library is overengineered. As a side effect, it allowed me to try out generics and mixins.

This library might violate common python conventions. I am not a python expert or even a professional developer. I am 
open to suggestions and improvements.

This library is not complete. It only implements the features I needed for my personal use case.

### Backlog

* implement remaining fields of the person model
* improve error handling
* implement remaining methods of the API, e.g. deletion, search, batch requests etc.
* implement syncing after paged retrieval

### Release notes

TBD.
