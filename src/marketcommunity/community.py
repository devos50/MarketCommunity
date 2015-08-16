import logging
import json
from dispersy.community import Community
from dispersy.conversion import DefaultConversion
from dispersy.message import Message
from dispersy.authentication import MemberAuthentication
from dispersy.resolution import PublicResolution
from dispersy.distribution import FullSyncDistribution
from dispersy.destination import CommunityDestination
from payload import AskPayload
from conversion import MarketConversion
from orders.orderbook import Orderbook

logging.basicConfig(format="%(asctime)-15s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MarketCommunity(Community):

    order_book = Orderbook()

    def initialize(self):
        super(MarketCommunity, self).initialize()
        logger.info("Market community initialized")

    def initiate_meta_messages(self):
        return super(MarketCommunity, self).initiate_meta_messages() + [
            Message(self, u"create-ask",
                    MemberAuthentication(encoding="sha1"),
                    PublicResolution(),
                    FullSyncDistribution(enable_sequence_number=False, synchronization_direction=u"ASC", priority=128),
                    CommunityDestination(node_count=0),
                    AskPayload(),
                    self.check_message,
                    self.on_ask)
        ]

    def initiate_conversions(self):
        return [DefaultConversion(self), MarketConversion(self)]

    def check_message(self, messages):
        for message in messages:
            yield message

    def on_ask(self, messages):
        for message in messages:
            logger.info("received ask message: " + message.payload.text)
            msg_json = json.loads(message.payload.text)
            self.order_book.add_order('ask', msg_json)

    def send_ask(self, price, quantity):
        message_dict = { "price" : price, "quantity" : quantity }
        logger.debug("sending ask")
        meta = self.get_meta_message(u"create-ask")
        message = meta.impl(authentication=(self.my_member,),
                          distribution=(self.claim_global_time(),),
                          payload=(unicode(json.dumps(message_dict)),))
        self.dispersy.store_update_forward([message], True, True, True)