def get_transRefs(payload):
    f_out = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            print(key)
            if isinstance(value, str):
                if key == 'transRef':
                    f_out.append(value)
            else:
                get_transRefs(value)

        return f_out
    else:
        for value in payload:
            if isinstance(value, str):
                pass
            else:
                get_transRefs(value)

        return f_out



bk = {
    "bulkPaymentInfo": {
        "totalAmount": "5000.00",
        "batchRef": "btc-0001",
        "debitAccount": "12345467890",
        "narration": "Bulk payment",
        "bankCode": "011"
    },
    "paymentDetails": [
        {
            "transRef": "trans-01", "paymentReference":
            "pmnt9273", "narration": "Payment one",
            "benficiaryName": "John Doe",
            "benficiaryEmail": "johndoe@test.com",
            "benficiaryPhone": "08083372818",
            "benficiaryLocation": "Lagos",
            "benficiaryBankCode": "044",
            "benficiaryAccountNumber": "8913323482",
            "amount": "2500.00",
            "currencyCode": "NGN",
            "originalAccountNumber": "12345467890"
        },
        {
            "transRef": "trans-02",
            "paymentReference": "pmnt9274",
            "narration": "Payment two",
            "benficiaryName": "Jane Doe",
            "benficiaryEmail": "janedoe@test.com",
            "benficiaryPhone": "08083372819",
            "benficiaryLocation": "Lagos",
            "benficiaryBankCode": "044",
            "benficiaryAccountNumber": "4390720129",
            "amount": "2500.00",
            "currencyCode": "NGN",
            "originalAccountNumber": "12345467890"
        }
    ]
}
