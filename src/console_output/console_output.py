from src.logic.CryptoParamsEnum import CryptoParamsEnum as CPEnum
from src.logic.CryptoParams import CryptoParams


def get_string_rating(rating: int):
    ratings = {
        0: 'nezistené/chyba',
        1: 'bezpečné',
        2: 'nedoporúčané',
        3: 'legacy use/slabé',
        4: 'zakázané'
    }
    return ratings[rating]


def console_output(params: CryptoParams):
    print('Kryptografická sada: \n\t{}'.format(params.cipher_suite))
    print('Kryptografické parametre:')
    for enum in CPEnum:
        print('\t{}: {}->{}({})'.format(
            enum.string_alias,
            params.params[enum][0],
            get_string_rating(params.params[enum][1]),
            params.params[enum][1])
        )
    print('Ostatné informácie o certifikáte:')
    print('\tCelková bezpečnosť kryptografickej sady: {}({})'.format(get_string_rating(params.rating), params.rating))
    print('\tVerzia certifikátu: {}'.format(params.cert_version))
    print('\tSériové číslo: {}'.format(params.cert_serial_number))
    print('\tInterval platnosti: {} do {}'.format(params.cert_not_valid_before, params.cert_not_valid_after))
    print('\tpredmet: ')
    for attribute in params.cert_subject:
        print('\t\t' + attribute.oid._name + ' = ' + attribute.value)
    print('\tvydavateľ:')
    for attribute in params.cert_issuer:
        print('\t\t' + attribute.oid._name + ' = ' + attribute.value)
