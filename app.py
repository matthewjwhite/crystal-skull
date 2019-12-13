''' Game entrypoint '''

from gevent import monkey
monkey.patch_all()

import game.telnet as telnet

if __name__ == '__main__':
    telnet.TelnetServer().run()
