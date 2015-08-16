from dispersy.payload import Payload


class AskPayload(Payload):

    class Implementation(Payload.Implementation):

        def __init__(self, meta, text):
            assert isinstance(text, unicode)
            assert len(text.encode("UTF-8")) <= 255
            super(AskPayload.Implementation, self).__init__(meta)
            self._text = text

        @property
        def text(self):
            return self._text
