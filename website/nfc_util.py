from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from smartcard.Exceptions import CardConnectionException
#from controlvault2_nfc_enable import nfc

# APDU for getting UID of MIFARE card
GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]


class MyObserver(CardObserver):
    """A simple card observer that gets the UID of inserted cards"""

    def __init__(self):
        self.uid = None

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("Card inserted: ", toHexString(card.atr))
            try:
                connection = card.createConnection()
                connection.connect()
                response, sw1, sw2 = connection.transmit(GET_UID_APDU)
                self.uid = toHexString(response)
                print("Card UID: ", self.uid)
            except CardConnectionException:
                print("Failed to connect to card")
                pass

    def get_uid(self):
        return self.uid


def get_nfc_uid_from_reader():
    nfc.turn_nfc_on()

    cardmonitor = CardMonitor()
    cardobserver = MyObserver()
    cardmonitor.addObserver(cardobserver)

    # Continuously loop until a card is detected.
    while cardobserver.get_uid() is None:
        pass

    uid = cardobserver.get_uid()

    cardmonitor.deleteObserver(cardobserver)
    return uid
