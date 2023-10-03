from pn7150 import PN7150

pn7150 = PN7150()

def get_nfc_uid_from_reader():
    NFC_ID = pn7150.read_once()
    return NFC_ID