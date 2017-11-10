import os
import base64
import hashlib
import json
import uuid
import requests
import datetime
from time import time
from Crypto.Cipher import AES
from __builtin__ import unicode
import sys
from . import exceptions as ex


class RemitaApiBase(object):
    REMITA_BASE_URL_DEMO = 'http://remitademo.net/remita/exapp/api/v2/pg'
    REMITA_BASE_URL_LIVE = 'http://remitademo.net'
    PAYLOAD_TRANSREFS = []

    def __init__(self, api_key=None, token=None, merchant_id=None, encryption_key=None, encryption_vector=None):
        if api_key:
            self.REMITA_API_KEY = api_key
        else:
            self.REMITA_API_KEY = os.getenv('REMITA_API_KEY', None)

        if not self.REMITA_API_KEY:
            raise ex.MissingAPIKeyError(
                'Remita API KEY could not be found. You can either add it to your settings file using the name REMITA_API_KEY or supply it while initiating this class')

        if token:
            self.REMITA_API_TOKEN = token
        else:
            self.REMITA_API_TOKEN = os.getenv('REMITA_API_TOKEN', None)

        if not self.REMITA_API_TOKEN:
            raise ex.MissingTokenKeyError('Remita Token KEY could not be loaded.')

        if merchant_id:
            self.REMITA_MERCHANT_ID = merchant_id
        else:
            self.REMITA_MERCHANT_ID = os.getenv('REMITA_MERCHANT_ID', None)

        if not self.REMITA_MERCHANT_ID:
            raise ex.MissingMerchantIDError('Remita Merchant ID  could not be loaded.')

        if encryption_key:
            self.REMITA_ENC_KEY = encryption_key
        else:
            self.REMITA_ENC_KEY = os.getenv('REMITA_ENC_KEY', None)

        if not self.REMITA_ENC_KEY:
            raise ex.MissingEncryptionKeyError('Remita Encryption Key could not be loaded.')

        if encryption_vector:
            self.REMITA_ENC_VECTOR = encryption_vector
        else:
            self.REMITA_ENC_VECTOR = os.getenv('REMITA_ENC_VECTOR', None)

        if not self.REMITA_ENC_VECTOR:
            raise ex.MissingEncryptionVectorError('Remita Encryption Vector could not be loaded.')

        """ setting environment"""
        if os.getenv('REMITA_IS_LIVE'):
            self.REMITA_BASE_URL = self.REMITA_BASE_URL_LIVE
            self.REMITA_IS_LIVE = True
        else:
            self.REMITA_BASE_URL = self.REMITA_BASE_URL_DEMO
            self.REMITA_IS_LIVE = False

        self.REMITA_ACCOUNT_LOOKUP = self.REMITA_BASE_URL + "/merc/fi/account/lookup"
        self.REMITA_BANKS_ENQUIRY = self.REMITA_BASE_URL + "/fi/banks"
        self.REMITA_BULK_PAYMENT_URL = self.REMITA_BASE_URL + "/merc/bulk/payment/send"
        self.REMITA_SINGLE_PAYMENT_URL = self.REMITA_BASE_URL + "/merc/payment/singlePayment.json"
        self.REMITA_TRANSACTION_STATUS_URL = self.REMITA_BASE_URL + "/merc/payment/status"

    def _encrypt(self, value):
        BS = 16
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        aes = AES.new(self.REMITA_ENC_KEY, AES.MODE_CBC, self.REMITA_ENC_VECTOR)
        return str(base64.b64encode(aes.encrypt(pad(value))).decode('utf-8'))

    def _header(self):
        request_id = "%s%s" % (str(uuid.uuid4()), str(time()).replace('.', ''))
        request_ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+000000')
        key = "%s%s%s" % (self.REMITA_API_KEY, request_id, self.REMITA_API_TOKEN)
        hash = hashlib.sha512(key.encode('utf8')).hexdigest()

        header = {
            'API_KEY': self.REMITA_API_KEY,
            'REQUEST_ID': request_id,
            'MERCHANT_ID': self.REMITA_MERCHANT_ID,
            'REQUEST_TS': request_ts,
            'API_DETAILS_HASH': hash
        }
        return header

    def _encrypt_bulk_details(self, dt):
        if isinstance(dt, dict):
            for key, value in dt.items():
                if isinstance(value, str) or isinstance(value, unicode):
                    dt[key] = self._encrypt(value)
                else:
                    self._encrypt_bulk_details(value)
            return dt
        else:  # elif isinstance(dt, list)
            for value in dt:
                if isinstance(value, str) or isinstance(value, unicode):
                    value = self._encrypt(value)
                else:
                    self._encrypt_bulk_details(value)
            return dt

    def _encrypt_bulk_details3(self, dt):
        if isinstance(dt, dict):
            for key, value in dt.items():
                if isinstance(value, str):
                    dt[key] = self._encrypt(value)
                else:
                    self._encrypt_bulk_details3(value)
            return dt
        else:  # elif isinstance(dt, list)
            for value in dt:
                if isinstance(value, str):
                    value = self._encrypt(value)
                else:
                    self._encrypt_bulk_details3(value)
            return dt

    def _encrypt_bulk_single_payment_details(self, transRef, paymentReference, naration, benficiaryName, benficiaryEmail,
                                        beneficiaryPhone, amount, benficiaryLocation, benficiaryBankCode,
                                        benficiaryAccountNumber,
                                        originalAccountNumber, currencyCode="NGN"):
        res = {
            "transRef": self._encrypt(str(transRef)),
            "paymentReference": self._encrypt(str(paymentReference)),
            "narration": self._encrypt(naration),
            "benficiaryName": self._encrypt(benficiaryName),
            "benficiaryEmail": self._encrypt(benficiaryEmail),
            "beneficiaryPhone": self._encrypt(beneficiaryPhone),
            "benficiaryLocation": self._encrypt(str(benficiaryLocation)),
            "benficiaryBankCode": self._encrypt(benficiaryBankCode),
            "benficiaryAccountNumber": self._encrypt_account_number_for_env(benficiaryAccountNumber,
                                                                            benficiaryBankCode),
            "amount": self._encrypt(str(amount)),
            "currencyCode": self._encrypt(currencyCode),
            "originalAccountNumber": self._encrypt(originalAccountNumber)
        }
        return res

    def _encrypt_single_payload(self, credit_bank_code, credit_account, narrarion, amount, trans_ref, debit_bank_code,
                                debit_account_no, beneficiary_email):
        res = {
            "toBank": self._encrypt(credit_bank_code),
            "creditAccount":self._encrypt_account_number_for_env(credit_account,credit_bank_code),
            "narration": self._encrypt(narrarion),
            "amount": self._encrypt(amount),
            "transRef": self._encrypt(trans_ref),
            "fromBank": self._encrypt(debit_bank_code),
            "debitAccount": self._encrypt_account_number_for_env(debit_account_no,debit_bank_code),
            "beneficiaryEmail": self._encrypt(beneficiary_email)
        }
        return res

    def _get_transaction_status(self, transRef, is_plantext=True):
        if is_plantext:
            transRef =self._encrypt(transRef)
        data = {
            'transRef': transRef
        }
        return self._process(self.REMITA_TRANSACTION_STATUS_URL, data)

    def _get_banks_data(self):
        return self._process(self.REMITA_BANKS_ENQUIRY)

    def _encrypt_account_number_for_env(self, account_number, bank_code):
        if self.REMITA_IS_LIVE:
            return self._encrypt(account_number)
        else:
            return self._encrypt("%s%s" % (bank_code, account_number))

    def _account_lookup(self, account_number, bank_code):
        data = {
            'accountNo': self._encrypt_account_number_for_env(account_number, bank_code),
            'bankCode': self._encrypt(bank_code),
        }
        return self._process(self.REMITA_ACCOUNT_LOOKUP, data)

    def _process(self, url, data=None):
        try:
            response = requests.post(url, json=data, headers=self._header())
        except:
            k = json.dumps({'status': 'serverError', 'message': 'Connection or server error. Please try again later'})
            return json.loads(k)
        r = response.text
        return json.loads(r)

    def verify_payload(self, payload, is_plain_text=False):
        pass

    def _get_python_version(self):
        return sys.version_info.major

    def _encrypt_plain_payload(self, text_payload):
        python_version = self._get_python_version()
        if python_version == 3:
            return self._encrypt_bulk_details3(text_payload)
        elif python_version == 2:
            return self._encrypt_bulk_details(text_payload)
        else:
            return ''

    def _get_transRefs(self, payload):
        self.PAYLOAD_TRANSREFS = []
        d = self._get_transRefs_loop(payload)
        return d

    def _get_transRefs_loop(self,payload):
        if isinstance(payload, dict):
            for key, value in payload.items():
                if isinstance(value, str):
                    if key == 'transRef':
                        self.PAYLOAD_TRANSREFS.append(value)
                else:
                    self._get_transRefs_loop(value)

            return self.PAYLOAD_TRANSREFS
        else:
            for value in payload:
                if isinstance(value, str):
                    pass
                else:
                    self._get_transRefs_loop(value)
            return self.PAYLOAD_TRANSREFS

    def _process_bulk_payment(self,payload,is_plaintext_payload=True):
        if is_plaintext_payload:
            data = self._encrypt_plain_payload(payload)
        else:
            data = payload
        return self._process(self.REMITA_BULK_PAYMENT_URL, data)

    def _process_single_payment(self,payload,is_plain_payload=True):
        if is_plain_payload:
            payload = self._encrypt_plain_payload(payload)
        return self._process(self.REMITA_SINGLE_PAYMENT_URL,payload)

    def _verify_payments(self,trans_refs):
        final_result = []
        for j in trans_refs:
            final_result.append(self._get_transaction_status(j, False))
        return final_result