# pushover-open-client-python

Implementation of [Pushover](https://play.google.com/store/apps/details?id=net.superblock.pushover)'s Open Client API specification for **receiving**
push notifications using pushover, using Python 3.

The Pushover Open Client API specification can be found at:

https://pushover.net/api/client

## How to test it for now

The expects a file at the home directory named `/.pushover-open-client-creds.json`.
The file should be a JSON file with account's `email` and `password`, this way:

### file: `~/.pushover-open-client-creds.json`

```json
{
  "email": "USERS@EMAIL.ETC",
  "password": "M4HSUP3RBPASS"
}
```

Given the above, by logging and getting an auth `secret`, a new device will be
created, and that file will be updated containing all these four values.

## Contributing

Please open an issue if you want to contribute with code.
