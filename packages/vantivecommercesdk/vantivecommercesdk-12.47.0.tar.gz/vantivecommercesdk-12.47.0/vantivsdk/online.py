# -*- coding: utf-8 -*-l
# Copyright (c) 2017 Vantiv eCommerce
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
from __future__ import absolute_import, print_function, unicode_literals

import re
from pathlib import Path

import requests
import xmltodict
import six

import xml.etree.ElementTree as ET
from vantivsdk import pgp_helper

from vantivsdk.commManager import commManager
from . import fields, utils, dict2obj


def request(transaction, conf, return_format='dict', timeout=30, sameDayFunding = False):
    """Send request to server.

    Args:
        transaction: An instance of transaction class
        conf: An instance of utils.Configuration
        return_format: Return format. The default is 'dict'. Could be one of 'dict', 'object' or 'xml'.
        timeout: timeout for the request in seconds. timeout is not a time limit on the entire response. It's the time that server has not issued a response.
        sameDayFunding (bool): Start v11.3. Used for Online Dynamic Payout Funding Instructions only. Set to True for same day funding.

    Returns:
        response XML in desired format.

    Raises:
        VantivExceptions.
    """
    if isinstance(transaction, dict):
        transaction = dict2obj.tofileds(transaction)

    if not (isinstance(transaction, fields.recurringTransactionType) or (transaction, fields.encryptionKeyRequest)
            or isinstance(transaction, fields.transactionType)):
        raise utils.VantivException(
            'transaction must be either cnp_xml_fields.recurringTransactionType or transactionType')

    if not isinstance(conf, utils.Configuration):
        raise utils.VantivException('conf must be an instance of utils.Configuration')

    if not isinstance(timeout, six.integer_types) or timeout < 0:
        raise utils.VantivException('timeout must be an positive int')

    request_xml = _create_request_xml(transaction, conf, sameDayFunding)
    response_xml = _http_post(request_xml, conf, timeout)

    response_dict = xmltodict.parse(response_xml)['cnpOnlineResponse']

    if response_dict['@response'] == '0':
        return_f_l = return_format.lower()
        if return_f_l == 'xml':
            return response_xml
        elif return_f_l == 'object':
            return fields.CreateFromDocument(response_xml)
        else:
            # if conf.print_xml:
            #     import json
            #     print('Response Dict:\n', json.dumps(response_dict, indent=4), '\n\n')
            return response_dict
    else:
        raise utils.VantivException(response_dict['@message'])


def _create_request_xml(transaction, conf, same_day_funding):
    """Create xml string from transaction object

    Args:
        transaction: an instance of object, could be either recurringTransaction or transaction
        conf: an instance of utils.Configuration

    Returns:
        XML string
    """
    request_obj = _create_request_obj(transaction, conf, same_day_funding)
    request_xml = utils.obj_to_xml(request_obj)

    if conf.oltpEncryptionPayload:
        request_xml = _create_encryption_request(request_xml, conf)

    if conf.print_xml:
        print_xml(request_xml.decode('utf-8'), conf.neuter_xml)

    return request_xml


def _create_encryption_request(request_xml, conf):
    # Parse the XML string
    ET.register_namespace('', 'http://www.vantivcnp.com/schema')
    root = ET.fromstring(request_xml)
    path = conf.oltpEncryptionKeyPath
    keyseq = conf.oltpEncryptionKeySequence
    namespace = {'ns': 'http://www.vantivcnp.com/schema'}

    # Find the second child element
    children = root.findall('./ns:*', namespace)

    if len(children) > 1:
        # Get the second child element
        child_element = children[1]
        str_element = ET.tostring(child_element, encoding='unicode')

        # Skip the encryption payload part for encryptionKeyRequest
        if str_element.__contains__('encryptionKeyRequest'):
            return ET.tostring(root)
        else:
            if path is None:
                raise utils.VantivException(
                    "Problem in reading the Encryption Key path. Provide the Encryption key path.")
            else:
                path = Path(path)
                if not path.exists() or not path.is_file():
                    raise utils.VantivException(
                        "The provided path is not a valid file path or the file does not exist.")
            # Send payload for encryption
            payload = pgp_helper.encryptPayload(str_element, path)

            new_element = ET.Element('payload')
            new_element.text = payload
            new_element0 = ET.Element('encryptionKeySequence')
            if keyseq is None or keyseq == '':
                raise utils.VantivException(
                    "Problem in reading the Encryption Key Sequence ...Provide the Encryption key Sequence ")
            else:
                new_element0.text = keyseq
            encrypted_element = ET.Element('encryptedPayload')

            # removing the child element which needs to be encrypted.
            root.remove(children[1])

            encrypted_element.append(new_element0)
            encrypted_element.append(new_element)

            # adding new element after encryption.
            root.append(encrypted_element)

    # Convert the modified XML back to a string
    return ET.tostring(root)


def _create_request_obj(transaction, conf, same_day_funding):
    """ Create <xs:element name="cnpOnlineRequest">

    <xs:complexType name="baseRequest">
        <xs:sequence>
            <xs:element ref="xp:authentication" />
            <xs:choice>
                <xs:element ref="xp:transaction" />
                <xs:element ref="xp:recurringTransaction" />
                <xs:element ref="xp:encryptionKeyRequest"/>
                <xs:element ref="xp:encryptedPayload" />
            </xs:choice>
        </xs:sequence>
        <xs:attribute name="version" type="xp:versionType" use="required" />
    </xs:complexType>

    <xs:element name="cnpOnlineRequest">
        <xs:complexType>
            <xs:complexContent>
                <xs:extension base="xp:baseRequest">
                    <xs:attribute name="merchantId" type="xp:merchantIdentificationType" use="required" />
                    <xs:attribute name="merchantSdk" type="xs:string" use="optional" />
                    <xs:attribute name="loggedInUser" type="xs:string" use="optional"/>
                </xs:extension>
            </xs:complexContent>
        </xs:complexType>
    </xs:element>

    Args:
        transaction: an instance of object, could be either recurringTransaction or transaction
        conf: an instance of utils.Configuration

    Returns:
        an instance of cnpOnlineRequest object
    """
    request_obj = fields.cnpOnlineRequest()
    request_obj.merchantId = conf.merchantId
    request_obj.version = conf.VERSION
    request_obj.merchantSdk = conf.MERCHANTSDK

    if hasattr(request_obj, 'sameDayFunding') and same_day_funding:
        request_obj.sameDayFunding = same_day_funding

    authentication = fields.authentication()
    authentication.user = conf.user
    authentication.password = conf.password
    request_obj.authentication = authentication
    if hasattr(transaction, 'reportGroup') and not transaction.reportGroup:
        transaction.reportGroup = conf.reportGroup
    # determine option for choice.
    # <xs:choice>
    #     <xs:element ref="xp:transaction" />
    #     <xs:element ref="xp:recurringTransaction" />
    #     <xs:element ref="xp:encryptionKeyRequest"/>
    # </xs:choice>
    if isinstance(transaction, fields.recurringTransactionType):
        request_obj.recurringTransaction = transaction
    # add elif condition for encryptionKeyRequest
    elif hasattr(transaction, 'encryptionKeyRequest'):
        request_obj.encryptionKeyRequest = transaction.encryptionKeyRequest
    else:
        request_obj.transaction = transaction
    return request_obj


def _http_post(post_data, conf, timeout):
    ECOM_API = ''
    """Post xml to server via https using requests

    Args:
        timeout:
        post_data: Request XML String
        conf: Instances of Configuration

    Returns:
        XML string for server response.

    Raise:
        VantivException
    """
    REQUEST_RESULT_RESPONSE_RECEIVED = 1
    REQUEST_RESULT_CONNECTION_FAILED = 2
    REQUEST_RESULT_RESPONSE_TIMEOUT = 3

    headers = {'Content-type': 'text/xml; charset=UTF-8'}
    if conf.sendEcomHeader:
        headerValue = ""
        if conf.ecomHeaderValue and conf.ecomHeaderValue.strip():
            headerValue = conf.ecomHeaderValue
        else:
            headerValue = ECOM_API

        headers["X-Ecom-Api"] = headerValue

    proxies = {'https': conf.proxy} if (conf.proxy is not None and conf.proxy != '') else None
    try:
        commManagerTemp = commManager(conf).manager
        requTarget = commManagerTemp.findUrl()
        response = requests.post(requTarget["targetUrl"], data=post_data, headers=headers, proxies=proxies, timeout=timeout)
        commManagerTemp.reportResult(requTarget, REQUEST_RESULT_RESPONSE_RECEIVED, response.status_code)
    except requests.RequestException:
        commManagerTemp.reportResult(requTarget, REQUEST_RESULT_CONNECTION_FAILED, 0)
        raise utils.VantivException("Error with Https Request, Please Check Proxy and Url configuration")

    if response.status_code != 200:
        raise utils.VantivException("Error with Https Response, Status code: ", response.status_code)

    # Check empty response
    if not response:
        commManagerTemp.reportResult(requTarget, REQUEST_RESULT_RESPONSE_TIMEOUT, 0)
        raise utils.VantivException("The response is empty, Please call Vantiv eCommerce")

    if conf.print_xml:
        print('Response XML:\n', response.text, '\n')

    return response.text


def neuter_xml(xml):
    neuter_str = "NEUTERED"
    if xml is None:
        return xml
    xml = re.sub(r"<accNum>.*?</accNum>", f"<accNum>{neuter_str}</accNum>", xml)
    xml = re.sub(r"<user>.*?</user>", f"<user>{neuter_str}</user>", xml)
    xml = re.sub(r"<password>.*?</password>", f"<password>{neuter_str}</password>", xml)
    xml = re.sub(r"<track>.*?</track>", f"<track>{neuter_str}</track>", xml)
    xml = re.sub(r"<number>.*?</number>", f"<number>{neuter_str}</number>", xml)
    xml = re.sub(r"<cardValidationNum>.*?</cardValidationNum>", f"<cardValidationNum>{neuter_str}</cardValidationNum>",
                 xml)

    return xml


def print_xml(xml_request, neuter_xml_flag):
    xml_to_log = xml_request
    if neuter_xml_flag:
        xml_to_log = neuter_xml(xml_to_log)
    print(f"Request XML: {xml_to_log}")

    return xml_request
