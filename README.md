# THIS REPOSITORY IS *DEPRECATED*, THIS PROJECT IS NOW HOSTED AT https://github.com/iacchus/python-pushover-open-client

New repository:
https://github.com/iacchus/python-pushover-open-client

# pushover-open-client-python

This is a client and framework implementation of 
[*Pushover*](https://play.google.com/store/apps/details?id=net.superblock.pushover)'s
[**Open Client API**](https://pushover.net/api/client) specification for
**receiving** push notifications using pushover, using Python 3.

The Pushover Open Client API specification can be found at:

https://pushover.net/api/client

## How to test it for now

The script expects a file at the home directory named `~/.pushover-open-client-creds.json`.
The file should be a JSON file with account's `email` and `password`, this way:

### file: `~/.pushover-open-client-creds.json`

```json
{
  "email": "USERS@EMAIL.ETC",
  "password": "M4HSUP3RBPASS"
}
```

Given the above, by logging and getting an auth `secret`, a new device will be
created wielding it's `device_id`, and that file will be updated containing all
these four values.

## Contributing

Please open an issue if you want to contribute with code.

## Support

You can open a issue or a message in discussions for support in using/getting
the code.

## Is it ready already?

No, not really, but will be soon. All steps of the app are already implemented,
almost all is done.
