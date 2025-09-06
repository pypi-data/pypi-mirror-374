#!/usr/bin/env python3

"""
Example demonstrating PaymentsResource create and update methods.

This example shows how to:
1. Create payments using both dictionary and Payment model instances
2. Update payments using both dictionary and Payment model instances
3. Handle datetime and currency values correctly
4. Perform partial updates with only specific fields like metadata
"""

from datetime import datetime

from ophelos_sdk import OphelosClient
from ophelos_sdk.models import Currency, Payment


def main():
    """
    Demonstrate PaymentsResource create and update methods.
    """

    # Initialize client (you would use your actual credentials)
    client = OphelosClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        audience="your_audience",
        environment="development",
    )

    debt_id = "debt_123"  # Replace with actual debt ID

    print("=== PaymentsResource Create and Update Examples ===\n")

    # Example 1: Create payment using dictionary
    print("1. Creating payment using dictionary...")
    payment_dict = {
        "transaction_at": "2023-12-01T10:30:00",
        "transaction_ref": "DICT-REF-001",
        "amount": 10000,  # £100.00 in pence
        "currency": "GBP",
        "metadata": {"source": "dictionary_example", "channel": "online"},
    }

    try:
        # This would make an actual API call
        # created_payment = client.payments.create(debt_id, payment_dict)
        # print(f"Created payment: {created_payment.id}")
        print(f"Would create payment with data: {payment_dict}")
    except Exception as e:
        print(f"Error creating payment: {e}")

    print()

    # Example 2: Create payment using Payment model
    print("2. Creating payment using Payment model...")
    payment_model = Payment(
        transaction_at=datetime(2023, 12, 1, 14, 45, 30),
        transaction_ref="MODEL-REF-001",
        amount=25000,  # £250.00 in pence
        currency=Currency.GBP,
        metadata={"source": "model_example", "channel": "mobile"},
    )

    try:
        # This would make an actual API call
        # created_payment = client.payments.create(debt_id, payment_model)
        # print(f"Created payment: {created_payment.id}")
        print(f"Would create payment with model: {payment_model}")
        print(f"Model serialized to: {payment_model.to_api_body()}")
    except Exception as e:
        print(f"Error creating payment: {e}")

    print()

    # Example 3: Update payment using dictionary
    print("3. Updating payment using dictionary...")
    payment_id = "payment_456"  # Replace with actual payment ID
    update_dict = {
        "transaction_ref": "UPDATED-REF-001",
        "metadata": {"source": "updated_dictionary", "updated_at": "2023-12-01T16:00:00"},
    }

    try:
        # This would make an actual API call
        # updated_payment = client.payments.update(debt_id, payment_id, update_dict)
        # print(f"Updated payment: {updated_payment.id}")
        print(f"Would update payment {payment_id} with data: {update_dict}")
    except Exception as e:
        print(f"Error updating payment: {e}")

    print()

    # Example 4: Update payment using Payment model
    print("4. Updating payment using Payment model...")
    update_model = Payment(
        transaction_at=datetime(2023, 12, 1, 16, 30, 0),
        transaction_ref="UPDATED-MODEL-REF-001",
        amount=30000,  # £300.00 in pence
        currency=Currency.GBP,
        metadata={"source": "updated_model", "validation": "passed"},
    )

    try:
        # This would make an actual API call
        # updated_payment = client.payments.update(debt_id, payment_id, update_model)
        # print(f"Updated payment: {updated_payment.id}")
        print(f"Would update payment {payment_id} with model: {update_model}")
        print(f"Model serialized to: {update_model.to_api_body()}")
    except Exception as e:
        print(f"Error updating payment: {e}")

    print()

    # Example 5: Partial update with only metadata (new feature!)
    print("5. Partial update with only metadata...")
    metadata_only_update = Payment(
        metadata={"status": "verified", "notes": "Customer confirmed payment", "updated_by": "system"}
    )

    try:
        # This would make an actual API call
        # updated_payment = client.payments.update(debt_id, payment_id, metadata_only_update)
        # print(f"Updated payment: {updated_payment.id}")
        print(f"Would update payment {payment_id} with metadata only: {metadata_only_update}")
        print(f"Model serialized to: {metadata_only_update.to_api_body()}")
    except Exception as e:
        print(f"Error updating payment metadata: {e}")

    print()

    # Example 6: Partial update with only transaction reference
    print("6. Partial update with only transaction reference...")
    ref_only_update = Payment(transaction_ref="CORRECTED-REF-789")

    try:
        # This would make an actual API call
        # updated_payment = client.payments.update(debt_id, payment_id, ref_only_update)
        # print(f"Updated payment: {updated_payment.id}")
        print(f"Would update payment {payment_id} with transaction_ref only: {ref_only_update}")
        print(f"Model serialized to: {ref_only_update.to_api_body()}")
    except Exception as e:
        print(f"Error updating payment reference: {e}")

    print()

    # Example 7: Using expand parameter
    print("7. Creating payment with expand parameter...")
    expanded_payment_dict = {
        "transaction_at": "2023-12-01T18:00:00",
        "transaction_ref": "EXPANDED-REF-001",
        "amount": 15000,  # £150.00 in pence
        "currency": "GBP",
        "metadata": {"source": "expanded_example"},
    }

    try:
        # This would make an actual API call with expanded response
        # created_payment = client.payments.create(debt_id, expanded_payment_dict, expand=["debt"])
        # print(f"Created payment with expanded debt: {created_payment}")
        print(f"Would create payment with expand=['debt'] and data: {expanded_payment_dict}")
    except Exception as e:
        print(f"Error creating payment with expand: {e}")

    print("\n=== Key Features ===")
    print("✓ Both dictionary and Payment model instances are supported")
    print("✓ Automatic serialization of datetime objects to ISO format")
    print("✓ Currency enum support (Currency.GBP, Currency.USD, etc.)")
    print("✓ Metadata support for custom fields")
    print("✓ Optional expand parameter for including related objects")
    print("✓ Consistent API with other Ophelos SDK resources")
    print("✓ Partial updates - only provide the fields you want to update")
    print("✓ All API body fields are now optional for flexible updates")


if __name__ == "__main__":
    main()
