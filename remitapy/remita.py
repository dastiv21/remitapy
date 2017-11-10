from .apibase import RemitaApiBase


class Remita(RemitaApiBase):
    def encrypt(self, value):
        return self._encrypt(value)

    def get_bulk_transaction_status(self, *transRef):
        """
        This get one or more transaction status
        :param transRef: supply n transaction reference to fetch. format: ref1,ref2,ref3,...,refn
        :return: list of dicts for each transaction status in the order of how the transaction references are supplied
        """
        responses = []
        for trans_ref in transRef:
            responses.append(self._get_transaction_status(trans_ref))
        return responses

    def get_transaction_status(self, transRef):
        """
        This get a single transaction status
        :param transRef: 
        :return: dict of transaction status
        """
        return self._get_transaction_status(transRef)

    def get_all_banks(self):
        """
        Get all banks information like bankCode,bankName etc
        :return: list if successful and None if not
        """
        response = self._get_banks_data()
        if response['status'] == 'serverError':
            return None
        else:
            return response['data']['banks']

    def verify_account(self, account_number, bank_code):
        return self._account_lookup(account_number, bank_code)

    def is_account_number_valid(self, account_number, bank_code):
        """
        Verify if an account number is valid with a given bank
        :param account_number: account number to check 
        :param bank_code: corresponding bank code of the account number
        :return: either TRUE, if successful, False if account number is not, NONE, if the request could not be processed
        """
        response = self.verify_account(account_number, bank_code)
        if response['status'] == 'serverError':
            return None  # could not be processed. probably connection error or API server is down
        elif response['success']:
            if response['data']['responseCode'] == '00':
                return True  # success. account validated
            else:
                return False  # account is not valid
        else:
            return None  # Another massive error occur

    def process_single_payment(self, payload, verify=True, is_plaintext_payload=True):
        response = self._process_single_payment(payload,is_plaintext_payload)
        if verify: #verify the transaction after processing
            trans_refs = self._get_transRefs(payload)
            response = self._verify_payments(trans_refs)[0]
        return response

    def process_bulk_payment(self, payload, verify=True, is_plaintext_payload=True):
        response = self._process_bulk_payment(payload, is_plaintext_payload)
        if verify: #verify the transaction after processing
            trans_refs = self._get_transRefs(payload)
            response = self._verify_payments(trans_refs)
        return response



