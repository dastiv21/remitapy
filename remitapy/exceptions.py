

class RemitaPyError(Exception):
    '''
    Remita API Error
    '''
    pass


class MissingAPIKeyError(RemitaPyError):
    ''' 
    API Key cannot be found
    '''
    pass


class MissingTokenKeyError(RemitaPyError):
    ''' 
    API Token Key cannot be found
    '''
    pass


class MissingMerchantIDError(RemitaPyError):
    ''' 
    API Merchant ID Key could not be found
    '''
    pass


class MissingEncryptionKeyError(RemitaPyError):
    ''' 
    AES Encryption Key Could not be loaded
    '''
    pass


class MissingEncryptionVectorError(RemitaPyError):
    ''' 
    AES Encryption Vector Key Could not be loaded
    '''
    pass

