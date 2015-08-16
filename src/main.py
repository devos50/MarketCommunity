import logging, signal, threading
from twisted.internet import reactor
from twisted.python.log import addObserver
from dispersy.dispersy import Dispersy
from dispersy.endpoint import StandaloneEndpoint
from marketcommunity.community import MarketCommunity

logging.basicConfig(format="%(asctime)-15s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DispersyMarket(Dispersy):

    def signal_handler(self, sig, frame):
        print '' # empty line to make info logging cleaner
        key = ''
        for i in signal.__dict__.keys():
            if i.startswith("SIG") and getattr(signal, i) == sig:
                key = i
                break
        logger.info("Received signal '%s', shutting down.", key)
        self.stop()
        reactor.stop()

    def bind_signals(self):
        "Binds to terminating signals"
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGQUIT, self.signal_handler)

    def setup_communities(self):
        master_key = "3081a7301006072a8648ce3d020106052b810400270381920004076bb2b34a80bc0ff658016c4ee964efd3006c66cbe1f8b4cb75b531e6d9cbc62531156007855cd2ad4985d1f1f9336fd0a2dc0b76ce35351115f20a6637aa76b0bf090ea47df88d029a844f26d0d689463cff7052f0d3b3288113a025164394e8eaed37fb2e9d8afd2275e0fb0ad7c503d9595eb3c1a8c6c8c2f4c5ee6044f2834854a753c8b0317c8a8c37bd2c6d08".decode("HEX")
        master = self.get_member(public_key=master_key)

        # Create an instance of the market community
        self.market_community = MarketCommunity.init_community(self, master, self.me)
        self.attach_community(self.market_community)

    def start_reactor(self):
        logger.info('Starting Twisted Reactor')
        reactor.exitCode = 0
        reactor.callWhenRunning(self.init)
        reactor.run(installSignalHandlers=0)

    def init(self):
        self.start(autoload_discovery=True)
        logger.info('Started Dispersy market instance')
        self.me = self.get_new_member()

        self.setup_communities()

    def __init__(self):
        super(DispersyMarket, self).__init__(StandaloneEndpoint(1234, '0.0.0.0'), u'../data', u'dispersy.db')
        self.statistics.enable_debug_statistics(True)

        self.bind_signals()

        from dispersy.util import unhandled_error_observer
        addObserver(unhandled_error_observer)

        threading.Thread(target=self.start_reactor, args=()).start()

if __name__ == "__main__":
    DispersyMarket()

    while True:
        inp = raw_input()
        if inp == "print":
            print "TODO: Print all orders"

    exit(reactor.exitCode)