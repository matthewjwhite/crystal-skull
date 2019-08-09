''' Game entrypoint '''

import game.telnet as telnet

if __name__ == '__main__':
    telnet.TelnetServer().run()
