import json
import logging
import re
import os
import time

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, ed448
from .exceptions.NoIanaPairFound import NoIanaPairFound
from .ratable.PType import PType
from ..utils import read_json


def convert_openssh_to_iana(search_term: str):
    """
    Convert openssh format of a cipher suite to IANA format.

    Raises IndexError if not conversion is found
    :param search_term: cipher suite
    :return: converted cipher suite
    """
    json_data = read_json('iana_openssl_cipher_mapping.json')
    for row in json_data:
        if json_data[row] == search_term:
            return row
    raise NoIanaPairFound()


def rate_key_length_parameter(algorithm_type: PType, key_len: str, key_len_type: PType):
    """
    Get the rating of an algorithm key length.

    :param key_len_type: type of the key length parameter
    :param algorithm_type: algorithm of the key length
    :param key_len: key length of the algorithm
    :return: rating of a parameter pair or 0 if a rating isn't defined or found
    """
    functions = {
        ">=": lambda a, b: a >= b,
        ">>": lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        "<<": lambda a, b: a < b,
        "==": lambda a, b: a == b
    }
    # TODO: All of the algorithms are not yet added to the security_levels.json
    levels_str = read_json('security_levels.json')[key_len_type.name]
    if key_len == 'N/A':
        return '0'
    for idx in range(1, 5):
        levels = levels_str[str(idx)].split(',')
        if algorithm_type in levels:
            # gets the operation assigned to the algorithm key length
            operation = levels[levels.index(algorithm_type) + 1]
            function = functions[operation[:2]]
            if function(int(key_len), int(operation[2:])):
                return str(idx)
    return '0'


def rate_parameter(p_type: PType, parameter: str):
    """
    Rate a parameter using a defined json file.

    :param parameter: parameter that is going to be rated
    :param p_type: specifies which parameter category should be used for rating
    :return: if a rating is found for a parameter returns that rating,
    if not 0 is returned (default value)
    """
    # TODO: All of the algorithms are not yet added to the security_levels.json
    security_levels_json = read_json('security_levels.json')
    if parameter == 'N/A':
        return '0'
    for idx in range(1, 5):
        if parameter in security_levels_json[p_type.name][str(idx)].split(','):
            return str(idx)
    return '0'


def pub_key_alg_from_cert(public_key):
    """
    Get the public key algorithm from a certificate.

    :param public_key: instance of a public key
    :return: string representation of a parameter
    """
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        return 'EC'
    elif isinstance(public_key, rsa.RSAPublicKey):
        return 'RSA'
    elif isinstance(public_key, dsa.DSAPublicKey):
        return 'DSA'
    elif isinstance(public_key, ed25519.Ed25519PublicKey) or isinstance(public_key, ed448.Ed448PublicKey):
        return 'ECDSA'
    else:
        return 'N/A'


def get_sig_alg_from_oid(oid: x509.ObjectIdentifier):
    """
    Get a signature algorithm from an oid of a certificate

    :param oid: object identifier
    :return: signature algorithm in string representation
    """
    values = list(x509.SignatureAlgorithmOID.__dict__.values())
    keys = list(x509.SignatureAlgorithmOID.__dict__.keys())
    return keys[values.index(oid)].split('_')[0]


def fix_url(url: str):
    """
    Extract the root domain name.

    :param url: hostname address to be checked
    :return: fixed hostname address
    """
    logging.info('Correcting url...')
    if url[:4] == 'http':
        # Removes http(s):// and anything after TLD (*.com)
        url = re.search('[/]{2}([^/]+)', url).group(1)
    else:
        # Removes anything after TLD (*.com)
        url = re.search('^([^/]+)', url).group(0)
    logging.info('Corrected url: {}'.format(url))
    return url


def incremental_sleep(sleep_dur, exception, max_timeout_dur):
    if sleep_dur >= max_timeout_dur:
        logging.debug('raise unknown connection error')
        raise exception
    logging.debug('increasing sleep duration')
    sleep_dur += 1
    logging.debug(f'sleeping for {sleep_dur}')
    time.sleep(sleep_dur)
    return sleep_dur
