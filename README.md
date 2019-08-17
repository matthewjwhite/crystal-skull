# crystal-skull

## Build

1. `docker build -t crystal-skull .`

## Run

1. `docker-compose up -d`
1. `telnet localhost 5555`
1. Follow steps to create a user.

The connection will die after the user is created.

Upon reconnecting, you will need to decrypt the challenge to authenticate.

To decrypt (assuming priv. key at `mykey.pem`):
```
echo <encryptedEncodedChallenge> | base64 -d > challenge && \
    openssl rsautl -decrypt -in challenge -inkey mykey.pem -out challenge-dec && \
    cat challenge-dec && \
    rm -f challenge-dec
```

## Features

### Implemented
* Server
* Basic user creation
* Authentication

### To Be Implemented
* NPCs
* Combat
