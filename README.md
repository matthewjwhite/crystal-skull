# crystal-skull

A highly-configurable, `telnet`-compatible, text-based RPG.

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

## Goals

* Keep the client-server communication as primitive as possible, using `telnet`,
  to maintain a retro feel.
* Make most aspects of the game configurable via simple file edits.
  * Rather than incorporating complex binaries burying aspects of maps, the goal
    is to use a simple format, such as YAML, to define monsters, maps, etc.
  * A server administrator could quickly customize the genre of the game, using
    this as an engine of sorts for their own game.

## Features

### Implemented
* Server
* Basic user creation
* Authentication

### To Be Implemented
* NPCs
* Combat
