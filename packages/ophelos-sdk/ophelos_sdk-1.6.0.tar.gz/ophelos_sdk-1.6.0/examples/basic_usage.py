#!/usr/bin/env python3
"""
Ophelos SDK - Getting Started Guide

This comprehensive example demonstrates:
- Client setup and authentication
- Basic CRUD operations across all resources
- Invoice creation with line items and metadata
- Error handling and best practices
- Common use cases and patterns
"""

import os

from ophelos_sdk import OphelosClient, WebhookHandler
from ophelos_sdk.exceptions import AuthenticationError, NotFoundError, TimeoutError, UnexpectedError, ValidationError


def setup_client():
    """Initialize and test the Ophelos client."""
    print("🚀 Setting up Ophelos SDK Client")
    print("=" * 50)

    client = OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv(
            "OPHELOS_CLIENT_SECRET",
            "your_client_secret",
        ),
        audience=os.getenv("OPHELOS_AUDIENCE", "http://localhost:3000"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "development"),  # staging, development, or production
        version=os.getenv("OPHELOS_VERSION", "2025-04-01"),
    )

    print(f"Environment: {client.authenticator.environment}")
    print(f"Base URL: {client.http_client.base_url}")

    # Test connection
    print("\nTesting connection...")
    try:
        if client.test_connection():
            print("✅ Connected to Ophelos API successfully!")
            return client
        else:
            print("❌ Failed to connect to Ophelos API")
            return None
    except AuthenticationError:
        print("❌ Authentication failed - check your credentials")
        return None
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def tenant_operations(client):
    """Demonstrate tenant operations."""
    print("\n" + "=" * 50)
    print("🏢 TENANT OPERATIONS")
    print("=" * 50)

    try:
        tenant = client.tenants.get_me()
        print(f"Tenant ID: {tenant.id}")
        print(f"Tenant Name: {tenant.name}")
        print(f"Description: {tenant.description or 'N/A'}")
        print(f"Created: {tenant.created_at}")

    except Exception as e:
        print(f"❌ Tenant error: {e}")


def debt_operations(client):
    """Demonstrate debt operations."""
    print("\n" + "=" * 50)
    print("💰 DEBT OPERATIONS")
    print("=" * 50)

    try:
        # List debts
        print("--- Listing Debts ---")
        debts = client.debts.list(limit=1, expand=["customer.contact_details", "organisation", "payments"])
        print(f"Found {len(debts.data)} debts (has_more: {debts.has_more})")

        for debt in debts.data:
            customer_name = "Unknown"
            if debt.customer:
                if isinstance(debt.customer, str):
                    customer_name = f"Customer ID: {debt.customer}"
                else:
                    customer_name = debt.customer.full_name or "N/A"
            print(f"  Debt {debt.id}: {debt.status.value} - ${debt.summary.amount_total / 100:.2f} ({customer_name})")

        if debts.data:
            debt_id = debts.data[0].id
            print(f"\n--- Debt Details: {debt_id} ---")
            debt = client.debts.get(debt_id, expand=["customer.contact_details", "organisation", "payments"])

            print(f"Status: {debt.status.value}")
            print(f"Amount: ${debt.summary.amount_total / 100:.2f}")
            print(f"Currency: {debt.currency or 'N/A'}")
            print(f"Account Number: {debt.account_number or 'N/A'}")

            if debt.customer:
                if isinstance(debt.customer, str):
                    print("Customer is a string")
                    print(f"Customer ID: {debt.customer}")
                else:
                    print("Customer is a model object")
                    print(f"Customer: {debt.customer.full_name or 'N/A'}")

            if debt.organisation:
                if isinstance(debt.organisation, str):
                    print("Organisation is a string")
                    print(f"Organisation ID: {debt.organisation}")
                else:
                    print("Organisation is a model object")
                    print(f"Organisation: {debt.organisation.name}")

            if debt.payments:
                print(f"Payments: {len(debt.payments)} payment(s)")

            print(f"Request url: {debt.request_info['url']}")
            print(f"Request method: {debt.request_info['method']}")
            print(f"Request headers: {debt.request_info['headers']}")

            print(f"Response raw json: {debt.response_raw.json()}")
            print(f"Response status code: {debt.response_info['status_code']}")
            print(f"Response headers: {debt.response_info['headers']}")
            print(f"Response elapsed: {debt.response_info['elapsed_ms']}")
            print(f"Response encoding: {debt.response_info['encoding']}")
            print(f"Response url: {debt.response_info['url']}")
            print(f"Response reason: {debt.response_info['reason']}")

        # Debt lifecycle operations
        print("\n--- Debt Lifecycle Operations ---")
        if debts.data:
            debt_id = "deb_GJxgKWlXEGVZfP0Wa4yANV28"

            # Demonstrate withdraw operation
            print(f"--- Withdraw Operation: {debt_id} ---")
            try:
                withdraw_data = {
                    "reason": "Customer requested withdrawal - contacted support requesting "
                    "debt withdrawal (Ref: WITHDRAW-2024-001)"
                }

                print(f"Withdrawing debt {debt_id}...")
                print(f"Withdrawal info: {withdraw_data['reason']}")

                # Perform withdrawal
                withdrawn_debt = client.debts.ready(debt_id, withdraw_data)
                print("✅ Debt withdrawn successfully!")
                print(f"   New status: {withdrawn_debt.status.value}")
                print(f"   Updated at: {withdrawn_debt.updated_at}")

                if hasattr(withdrawn_debt.status, "reason") and withdrawn_debt.status.reason:
                    print(f"   Withdrawal reason: {withdrawn_debt.status.reason}")

                # Show other lifecycle operations available
                print("\n--- Other Lifecycle Operations Available ---")
                print("  • ready() - Mark debt as ready for processing")
                print("  • pause() - Pause debt processing")
                print("  • resume() - Resume paused debt")
                print("  • settle() - Settle the debt")
                print("  • dispute() - Mark debt as disputed")
                print("  • resolve_dispute() - Resolve debt dispute")

            except Exception as e:
                print(f"❌ Withdrawal operation failed: {e}")
                print("   This might be due to debt status or permissions")

                # Show example of other operations that might work
                print("\n--- Alternative: Pause Operation Example ---")
                try:
                    pause_data = {"reason": "Customer requested pause - temporary pause for customer review"}
                    paused_debt = client.debts.pause(debt_id, pause_data)
                    print("✅ Debt paused successfully!")
                    print(f"   New status: {paused_debt.status.value}")
                except Exception as pause_error:
                    print(f"❌ Pause operation also failed: {pause_error}")

        # Search debts
        print("\n--- Searching Debts ---")
        try:
            search_results = client.debts.search("status:initializing", limit=3)
            print(f"Request url: {search_results.request_info['url']}")

            print(f"Found {len(search_results.data)} initializing debts")
            for debt in search_results.data:
                print(f"  initializing debt {debt.id}: ${debt.summary.amount_total / 100:.2f}")
        except Exception as e:
            print(f"Search not available: {e}")

    except Exception as e:
        print(f"❌ Debt operations error: {e}")


def customer_operations(client):
    """Demonstrate customer operations."""
    print("\n" + "=" * 50)
    print("👥 CUSTOMER OPERATIONS")
    print("=" * 50)

    try:
        # List customers
        customers = client.customers.list(limit=5)
        print(f"Found {len(customers.data)} customers")

        for customer in customers.data:
            # Handle both model objects and dictionaries (fallback)
            if hasattr(customer, "full_name"):
                # It's a Customer model object
                name = customer.full_name or f"{customer.first_name or ''} {customer.last_name or ''}".strip()
                customer_id = customer.id
            else:
                # It's a dictionary (parsing failed, fallback)
                name = (
                    customer.get("full_name")
                    or f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                )
                customer_id = customer.get("id", "Unknown")

            print(f"  Customer {customer_id}: {name or 'No name'}")

        if customers.data:
            first_customer = customers.data[0]
            if hasattr(first_customer, "id"):
                customer_id = first_customer.id
            else:
                customer_id = first_customer.get("id", "Unknown")

            print(f"\n--- Customer Details: {customer_id} ---")
            customer = client.customers.get(customer_id, expand=["contact_details"])

            # Handle both model objects and dictionaries safely
            if hasattr(customer, "full_name"):
                # It's a Customer model object
                print(f"Name: {customer.full_name or 'N/A'}")
                print(f"DOB: {customer.date_of_birth or 'N/A'}")
                print(f"Locale: {customer.preferred_locale or 'N/A'}")

                if customer.contact_details:
                    print(f"Contact details: {len(customer.contact_details)} item(s)")
            else:
                # It's a dictionary (parsing failed, fallback)
                print(f"Name: {customer.get('full_name', 'N/A')}")
                print(f"DOB: {customer.get('date_of_birth', 'N/A')}")
                print(f"Locale: {customer.get('preferred_locale', 'N/A')}")

                contact_details = customer.get("contact_details", [])
                if contact_details:
                    print(f"Contact details: {len(contact_details)} item(s)")

    except Exception as e:
        print(f"❌ Customer operations error: {e}")


def payment_operations(client):
    """Demonstrate payment operations."""
    print("\n" + "=" * 50)
    print("💳 PAYMENT OPERATIONS")
    print("=" * 50)

    try:
        # List payments
        payments = client.payments.list(limit=5)
        print(f"Found {len(payments.data)} payments")

        for payment in payments.data:
            print(f"  Payment {payment.id}: {payment.status} - ${payment.amount / 100:.2f}")
            print(f"    Transaction: {payment.transaction_at}")

    except Exception as e:
        print(f"❌ Payment operations error: {e}")


def invoice_operations(client):
    """Demonstrate invoice operations."""
    print("\n" + "=" * 50)
    print("🧾 INVOICE OPERATIONS")
    print("=" * 50)

    try:
        # First, get a debt to work with
        print("--- Getting a debt for invoice operations ---")
        debts = client.debts.list(limit=1)

        if not debts.data:
            print("❌ No debts available for invoice operations")
            return

        debt_id = debts.data[0].id
        print(f"Using debt: {debt_id}")

        # Create an invoice
        print(f"\n--- Creating Invoice for Debt: {debt_id} ---")

        # Prepare invoice data
        from datetime import date, datetime, timedelta

        today = date.today()
        due_date = today + timedelta(days=30)
        # Use a past timestamp - transactions must be in the past or present
        transaction_time = (datetime.now() - timedelta(hours=1)).isoformat()

        invoice_data = {
            "reference": f"INV-{today.strftime('%Y%m%d')}-001",
            "description": "Monthly service invoice",
            "invoiced_on": today.isoformat(),
            "due_on": due_date.isoformat(),
            "line_items": [
                {
                    "kind": "debt",
                    "description": "Principal debt amount",
                    "amount": 10000,  # $100.00 in cents
                    "currency": "GBP",
                    "transaction_at": transaction_time,
                },
                {
                    "kind": "interest",
                    "description": "Monthly interest charge",
                    "amount": 500,  # $5.00 in cents
                    "currency": "GBP",
                    "transaction_at": transaction_time,
                },
                {
                    "kind": "fee",
                    "description": "Processing fee",
                    "amount": 250,  # $2.50 in cents
                    "currency": "GBP",
                    "transaction_at": transaction_time,
                },
            ],
            "metadata": {"created_by": "sdk_example", "invoice_type": "monthly", "department": "billing"},
        }

        print(f"Creating invoice for debt: {debt_id}")
        print(f"Invoice data: {invoice_data}")
        try:
            created_invoice = client.invoices.create(debt_id, invoice_data)
            print("✅ Invoice created successfully!")
            print(f"   Invoice ID: {created_invoice.id}")
            print(f"   Reference: {created_invoice.reference}")
            print(f"   Status: {created_invoice.status}")
            print(f"   Invoiced On: {created_invoice.invoiced_on}")
            print(f"   Due On: {created_invoice.due_on}")
            print(f"   Description: {created_invoice.description}")

            if created_invoice.line_items:
                print(f"   Line Items: {len(created_invoice.line_items)} item(s)")
                for i, line_item in enumerate(created_invoice.line_items[:3], 1):
                    if hasattr(line_item, "kind"):  # It's a LineItem object
                        amount_display = f"${line_item.amount / 100:.2f}" if line_item.amount else "N/A"
                        # Handle both enum and string values for kind
                        kind_display = line_item.kind.value if hasattr(line_item.kind, "value") else str(line_item.kind)
                        print(f"     {i}. {kind_display}: {line_item.description} - {amount_display}")
                    else:  # It's a string ID
                        print(f"     {i}. Line item ID: {line_item}")

            # Get the created invoice with expanded line items
            print(f"\n--- Getting Invoice Details: {created_invoice.id} ---")
            invoice_details = client.invoices.get(debt_id, created_invoice.id, expand=["line_items"])

            print("Invoice Details:")
            print(f"   ID: {invoice_details.id}")
            print(f"   Reference: {invoice_details.reference}")
            print(f"   Status: {invoice_details.status}")
            print(f"   Currency: {invoice_details.currency}")
            print(f"   Created: {invoice_details.created_at}")
            print(f"   Updated: {invoice_details.updated_at}")

            if invoice_details.line_items:
                total_amount = 0
                print(f"   Expanded Line Items: {len(invoice_details.line_items)} item(s)")
                for i, line_item in enumerate(invoice_details.line_items, 1):
                    if hasattr(line_item, "kind"):  # It's a LineItem object
                        amount_display = f"${line_item.amount / 100:.2f}" if line_item.amount else "N/A"
                        total_amount += line_item.amount or 0
                        # Handle both enum and string values for kind
                        kind_display = line_item.kind.value if hasattr(line_item.kind, "value") else str(line_item.kind)
                        print(f"     {i}. {kind_display}: {line_item.description} ({amount_display})")
                        print(f"        ID: {line_item.id}")
                        print(f"        Transaction at: {line_item.transaction_at}")
                        if line_item.metadata:
                            print(f"        Metadata: {line_item.metadata}")
                    else:  # It's a string ID
                        print(f"     {i}. Line item ID: {line_item}")

                if total_amount > 0:
                    print(f"   Total Amount: ${total_amount / 100:.2f}")

            # Update the invoice
            print(f"\n--- Updating Invoice: {created_invoice.id} ---")
            update_data = {
                "description": "Updated monthly service invoice with additional details",
                "metadata": {
                    "created_by": "sdk_example",
                    "invoice_type": "monthly",
                    "department": "billing",
                    "updated_reason": "Added more detailed description",
                },
            }

            try:
                updated_invoice = client.invoices.update(debt_id, created_invoice.id, update_data)
                print("✅ Invoice updated successfully!")
                print(f"   Updated Description: {updated_invoice.description}")
                print(f"   Updated At: {updated_invoice.updated_at}")

                if updated_invoice.metadata:
                    print(f"   Updated Metadata: {updated_invoice.metadata}")

            except Exception as update_error:
                print(f"❌ Invoice update failed: {update_error}")
                print(f"   Error type: {type(update_error).__name__}")

                # Show detailed error information if available
                if hasattr(update_error, "status_code"):
                    print(f"   Status code: {update_error.status_code}")
                if hasattr(update_error, "response_data"):
                    print(f"   Response data: {update_error.response_data}")
                if hasattr(update_error, "response_raw") and update_error.response_raw:
                    try:
                        response_json = update_error.response_raw.json()
                        print(f"   API Response: {response_json}")
                    except Exception:
                        print(f"   Response text: {update_error.response_raw.text}")

            # Search invoices for this debt
            print(f"\n--- Searching Invoices for Debt: {debt_id} ---")
            try:
                search_results = client.invoices.search(debt_id, f"reference:{created_invoice.reference}", limit=5)
                print(f"Found {len(search_results.data)} invoices matching reference")
                for invoice in search_results.data:
                    print(f"  Invoice {invoice.id}: {invoice.reference} - {invoice.status}")
            except Exception as search_error:
                print(f"❌ Invoice search failed: {search_error}")
                print(f"   Error type: {type(search_error).__name__}")

                # Show detailed error information if available
                if hasattr(search_error, "status_code"):
                    print(f"   Status code: {search_error.status_code}")
                if hasattr(search_error, "response_data"):
                    print(f"   Response data: {search_error.response_data}")
                if hasattr(search_error, "response_raw") and search_error.response_raw:
                    try:
                        response_json = search_error.response_raw.json()
                        print(f"   API Response: {response_json}")
                    except Exception:
                        print(f"   Response text: {search_error.response_raw.text}")

        except Exception as create_error:
            print(f"❌ Invoice creation failed: {create_error}")
            print(f"   Error type: {type(create_error).__name__}")

            # Show detailed error information if available
            if hasattr(create_error, "status_code"):
                print(f"   Status code: {create_error.status_code}")
            if hasattr(create_error, "message"):
                print(f"   Error message: {create_error.message}")
            if hasattr(create_error, "response_data"):
                print(f"   Response data: {create_error.response_data}")
            if hasattr(create_error, "details"):
                print(f"   Error details: {create_error.details}")
            if hasattr(create_error, "request_info"):
                print(f"   Request info: {create_error.request_info}")
            if hasattr(create_error, "response_info"):
                print(f"   Response info: {create_error.response_info}")

    except Exception as e:
        print(f"❌ Invoice operations error: {e}")
        print(f"   Error type: {type(e).__name__}")

        # Show detailed error information if available
        if hasattr(e, "status_code"):
            print(f"   Status code: {e.status_code}")
        if hasattr(e, "message"):
            print(f"   Error message: {e.message}")
        if hasattr(e, "response_data"):
            print(f"   Response data: {e.response_data}")
        if hasattr(e, "details"):
            print(f"   Error details: {e.details}")
        if hasattr(e, "request_info"):
            print(f"   Request info: {e.request_info}")
        if hasattr(e, "response_info"):
            print(f"   Response info: {e.response_info}")


def invoice_model_operations(client):
    """Demonstrate invoice operations using model objects."""
    print("\n" + "=" * 50)
    print("🧾 INVOICE MODEL OPERATIONS")
    print("=" * 50)

    try:
        # Import the models we'll use
        from datetime import date, datetime, timedelta

        from ophelos_sdk.models import Invoice, LineItem, LineItemKind

        # First, get a debt to work with
        print("--- Getting a debt for invoice model operations ---")
        debts = client.debts.list(limit=1)

        if not debts.data:
            print("❌ No debts available for invoice model operations")
            return

        debt_id = debts.data[0].id
        print(f"Using debt: {debt_id}")

        # Create invoice using model objects
        print("\n--- Creating Invoice Using Model Objects ---")

        today = date.today()
        due_date = today + timedelta(days=30)
        transaction_time = datetime.now() - timedelta(hours=1)

        # Create line items using the LineItem model
        line_items = [
            LineItem(
                kind=LineItemKind.DEBT,
                description="Principal debt amount",
                amount=15000,  # $150.00 in cents
                currency="GBP",
                transaction_at=transaction_time,
                metadata={"category": "principal", "priority": "high"},
            ),
            LineItem(
                kind=LineItemKind.INTEREST,
                description="Accrued interest",
                amount=750,  # $7.50 in cents
                currency="GBP",
                transaction_at=transaction_time,
                metadata={"rate": "5.0%", "period": "monthly"},
            ),
            LineItem(
                kind=LineItemKind.FEE,
                description="Late payment fee",
                amount=2500,  # $25.00 in cents
                currency="GBP",
                transaction_at=transaction_time,
                metadata={"type": "late_fee", "days_overdue": "15"},
            ),
        ]

        # Create the invoice using the Invoice model
        invoice = Invoice(
            reference=f"INV-MODEL-{today.strftime('%Y%m%d')}-001",
            description="Invoice created using model objects",
            invoiced_on=today,
            due_on=due_date,
            line_items=line_items,
            metadata={
                "created_by": "sdk_model_example",
                "invoice_type": "model_based",
                "department": "collections",
                "total_items": str(len(line_items)),
            },
        )

        print("Created Invoice model:")
        print(f"   Reference: {invoice.reference}")
        print(f"   Description: {invoice.description}")
        print(f"   Invoiced On: {invoice.invoiced_on}")
        print(f"   Due On: {invoice.due_on}")
        print(f"   Line Items: {len(invoice.line_items)} item(s)")

        # Display line items before sending
        for i, line_item in enumerate(invoice.line_items, 1):
            # Handle both enum and string values for kind
            kind_display = line_item.kind.value if hasattr(line_item.kind, "value") else str(line_item.kind)
            print(f"     {i}. {kind_display}: {line_item.description}")
            print(f"        Amount: ${line_item.amount / 100:.2f}")
            print(f"        Metadata: {line_item.metadata}")

        # Send model directly to API with expand
        print("\n--- Sending Invoice Model Directly to API ---")
        try:
            # Pass the model object directly with expand parameter - the resource should handle the conversion
            created_invoice = client.invoices.create(debt_id, invoice, expand=["line_items"])
            print("✅ Invoice created successfully using model!")
            print(f"   Invoice ID: {created_invoice.id}")
            print(f"   Reference: {created_invoice.reference}")
            print(f"   Status: {created_invoice.status}")

            # Show model vs API response comparison
            print("\n--- Model vs API Response Comparison ---")
            print(f"Model reference: {invoice.reference}")
            print(f"API reference:   {created_invoice.reference}")
            print(f"Model description: {invoice.description}")
            print(f"API description:   {created_invoice.description}")
            print(f"Model line items: {len(invoice.line_items)}")
            print(f"API line items:   {len(created_invoice.line_items) if created_invoice.line_items else 0}")

            # Demonstrate model validation
            print("\n--- Model Validation Example ---")
            try:
                # Try to create an invalid line item
                invalid_line_item = LineItem(
                    kind="invalid_kind",  # This should fail validation
                    description="Invalid line item",
                    amount=1000,
                    currency="GBP",
                    transaction_at=transaction_time,
                )
                print("This shouldn't print - validation should catch the error")
            except Exception as validation_error:
                print(f"✅ Model validation caught error: {validation_error}")
                print("   This shows the model validates data before sending to API")

            # Demonstrate working with expanded invoice data
            print("\n--- Working with Retrieved Invoice Model ---")
            retrieved_invoice = client.invoices.get(debt_id, created_invoice.id, expand=["line_items"])

            # Convert API response back to model (if needed)
            print(f"Retrieved invoice type: {type(retrieved_invoice)}")
            print(f"Retrieved invoice ID: {retrieved_invoice.id}")
            print(f"Retrieved invoice status: {retrieved_invoice.status}")

            if retrieved_invoice.line_items:
                print("Retrieved line items:")
                for i, line_item in enumerate(retrieved_invoice.line_items, 1):
                    if hasattr(line_item, "kind"):
                        kind_display = line_item.kind.value if hasattr(line_item.kind, "value") else str(line_item.kind)
                        print(f"   {i}. {kind_display}: {line_item.description}")
                        print(f"      Amount: ${line_item.amount / 100:.2f}")
                        if hasattr(line_item, "metadata") and line_item.metadata:
                            print(f"      Metadata: {line_item.metadata}")

        except Exception as create_error:
            print(f"❌ Model-based invoice creation failed: {create_error}")
            print(f"   Error type: {type(create_error).__name__}")

            # Show detailed error information
            if hasattr(create_error, "status_code"):
                print(f"   Status code: {create_error.status_code}")
            if hasattr(create_error, "response_data"):
                print(f"   Response data: {create_error.response_data}")
            if hasattr(create_error, "details"):
                print(f"   Error details: {create_error.details}")

    except Exception as e:
        print(f"❌ Invoice model operations error: {e}")
        print(f"   Error type: {type(e).__name__}")

        # Show detailed error information
        if hasattr(e, "response_data"):
            print(f"   Response data: {e.response_data}")


def webhook_operations(client):
    """Demonstrate webhook operations."""
    print("\n" + "=" * 50)
    print("🔗 WEBHOOK OPERATIONS")
    print("=" * 50)

    try:
        # List webhooks
        webhooks = client.webhooks.list(limit=3)
        print(f"Found {len(webhooks.data)} webhooks")

        for webhook in webhooks.data:
            status = "enabled" if webhook.enabled else "disabled"
            print(f"  Webhook {webhook.id}: {status}")
            print(f"    URL: {webhook.url}")
            print(f"    Events: {', '.join(webhook.enabled_events[:3])}")

        # Webhook handling example
        print("\n--- Webhook Handling Example ---")
        webhook_secret = os.getenv("OPHELOS_WEBHOOK_SECRET", "your_webhook_secret")
        webhook_handler = WebhookHandler(webhook_secret)

        # Sample webhook payload
        sample_payload = """{
            "id": "evt_123456789",
            "object": "event",
            "type": "debt.created",
            "created_at": "2024-01-15T10:30:00Z",
            "livemode": false,
            "data": {
                "id": "debt_123",
                "object": "debt",
                "status": "prepared",
                "total_amount": 10000,
                "currency": "GBP"
            }
        }"""

        # Parse webhook event
        event = webhook_handler.parse_event(sample_payload)
        print(f"Sample webhook event: {event.type}")
        print(f"Event data: {event.data.get('object', 'N/A')}")

    except Exception as e:
        print(f"❌ Webhook operations error: {e}")


def demonstrate_api_error_handling(client):
    """Demonstrate proper error handling."""
    print("\n" + "=" * 50)
    print("⚠️ ERROR HANDLING EXAMPLES")
    print("=" * 50)

    # Try to get a non-existent debt
    print("--- Handling Not Found Error ---")
    try:
        client.debts.get("non-existent-id")
        print("This shouldn't print")
    except NotFoundError as e:
        print(f"✅ Caught API error: {e}")
        print(f"   Status code: {e.status_code}")
        print(f"   Error message: {e.message}")
        print(f"   Error status code: {e.status_code}")
        print(f"   Error response data: {e.response_data}")
        print(f"   Error details: {e.details}")
        print(f"   Error request info: {e.request_info}")
        print(f"   Error response info: {e.response_info}")
        print(f"   Error response raw: {e.response_raw.json()}")
        print(f"   Error response url: {e.response_raw.url}")
        print(f"   Error response status code: {e.response_raw.status_code}")
        print(f"   Error response headers: {e.response_raw.headers}")
        print(f"   Error response elapsed: {e.response_raw.elapsed}")
        print(f"   Error response encoding: {e.response_raw.encoding}")
        print(f"   Error response reason: {e.response_raw.reason}")
        print(f"   Error response text: {e.response_raw.text}")
        print(f"   Error request headers: {e.response_raw.request.headers}")
        print(f"   Error request method: {e.response_raw.request.method}")
        print(f"   Error request url: {e.response_raw.request.url}")
        print(f"   Error request body: {e.response_raw.request.body}")

    # Try invalid search
    print("\n--- Handling Validation Error ---")
    try:
        client.debts.create({"invalid": "data"})
    except ValidationError as e:
        print(f"✅ Caught validation error: {e}")
        print(f"   Status code: {e.status_code}")
        print(f"   Error message: {e.message}")
        print(f"   Error status code: {e.status_code}")
        print(f"   Error response data: {e.response_data}")
        print(f"   Error details: {e.details}")
        print(f"   Error request info: {e.request_info}")
        print(f"   Error response info: {e.response_info}")
        print(f"   Error response raw: {e.response_raw.json()}")
        print(f"   Error response url: {e.response_raw.url}")
        print(f"   Error response status code: {e.response_raw.status_code}")
        print(f"   Error response headers: {e.response_raw.headers}")
        print(f"   Error response elapsed: {e.response_raw.elapsed}")
        print(f"   Error response encoding: {e.response_raw.encoding}")
        print(f"   Error response reason: {e.response_raw.reason}")
        print(f"   Error response text: {e.response_raw.text}")
        print(f"   Error request headers: {e.response_raw.request.headers}")
        print(f"   Error request method: {e.response_raw.request.method}")
        print(f"   Error request url: {e.response_raw.request.url}")
        print(f"   Error request body: {e.response_raw.request.body}")
    except Exception as e:
        print(f"Other error: {e}")


def demonstrate_timeout_error_handling(client):
    """Demonstrate timeout error handling."""
    print("\n" + "=" * 50)
    print("⚠️ TIMEOUT ERROR HANDLING EXAMPLES")
    print("=" * 50)

    print("\n--- Handling Timeout Error ---")
    try:
        # Use a valid but slow IP to simulate timeout (use httpbin.org delay endpoint)
        original_timeout = client.http_client.timeout
        original_max_retries = client.http_client.max_retries
        original_base_url = client.http_client.base_url

        client.http_client.base_url = "https://httpbin.org"  # Public testing service
        client.http_client.timeout = 1  # 1 second timeout
        client.http_client.max_retries = 0

        # Clear cached session so new settings take effect
        if hasattr(client.http_client._local, "session"):
            delattr(client.http_client._local, "session")

        # Use httpbin's delay endpoint - delays response by 3 seconds
        client.http_client.get("/delay/3")  # This should timeout after 1 second
        print("This shouldn't print")

    except TimeoutError as e:
        print(f"✅ Caught timeout error: {e}")
        print(f"   Error message: {e.message}")
        print(f"   Error details: {e.details}")
        print(f"   Error request info: {e.request_info}")
        print(f"   Error response info: {e.response_info}")
        print(f"   Error response raw: {e.response_raw}")

    except UnexpectedError as e:
        print(f"✅ Caught unexpected error (may happen with httpbin): {e}")
        print(f"   Error message: {e.message}")
        print(f"   Original error: {e.original_error}")

    except Exception as e:
        print(f"❌ Caught different error type: {type(e).__name__}: {e}")

    finally:
        # Restore original settings
        client.http_client.base_url = original_base_url
        client.http_client.timeout = original_timeout
        client.http_client.max_retries = original_max_retries


def demonstrate_unexpected_error_handling(client):
    """Demonstrate unexpected error handling."""
    print("\n" + "=" * 50)
    print("⚠️ UNEXPECTED ERROR HANDLING EXAMPLES")
    print("=" * 50)

    print("\n--- Handling Unexpected Error ---")
    try:
        # Save original settings
        original_base_url = client.http_client.base_url
        original_timeout = client.http_client.timeout
        original_max_retries = client.http_client.max_retries

        # Use localhost with a port that refuses connections (not timeout)
        # This will cause a "Connection refused" error, not a timeout error
        client.http_client.base_url = "http://127.0.0.1:1"  # Port 1 should refuse connections
        client.http_client.timeout = 5  # Normal timeout
        client.http_client.max_retries = 0

        # Clear cached session so new settings take effect
        if hasattr(client.http_client._local, "session"):
            delattr(client.http_client._local, "session")

        client.debts.get("any-id")  # This will trigger UnexpectedError
        print("This shouldn't print")

    except UnexpectedError as e:
        print(f"✅ Caught unexpected error: {e}")
        print(f"   Error type: {type(e)}")
        print(f"   Error message: {e.message}")
        print(f"   Original error: {e.original_error}")
        print(f"   Request info: {e.request_info}")
        print(f"   Response info: {e.response_info}")  # Will be None
        print(f"   Response raw: {e.response_raw}")  # Will be None

    except Exception as e:
        print(f"❌ Caught different error type: {type(e).__name__}: {e}")

    finally:
        # Restore original settings
        client.http_client.base_url = original_base_url
        client.http_client.timeout = original_timeout
        client.http_client.max_retries = original_max_retries

        # Clear session again to restore original settings
        if hasattr(client.http_client._local, "session"):
            delattr(client.http_client._local, "session")


def demonstrate_cross_resource_iterators(client):
    """Show consistent iterator API across resources."""
    print("\n--- Cross-Resource Iterators ---")
    print("All resources support the same iterator API:")
    resources = [
        ("Debts", client.debts),
        ("Customers", client.customers),
        ("Payments", client.payments),
    ]

    for name, resource in resources:
        try:
            count = 0
            for item in resource.iterate(limit_per_page=2, max_pages=2):
                count += 1
                if count <= 3:
                    print(f"  {name}: {item.id}")
                elif count == 4:
                    print(f"    ... ({count}+ items)")
                    break
        except Exception:
            print(f"  {name}: No data available")


def main():
    """Run all examples."""
    print("📚 Ophelos SDK - Complete Getting Started Guide")

    # Check for required environment variables
    required_vars = ["OPHELOS_CLIENT_ID", "OPHELOS_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("\n💡 Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n   Set these environment variables:")
        print("   export OPHELOS_CLIENT_ID='your_client_id'")
        print("   export OPHELOS_CLIENT_SECRET='your_client_secret'")
        print("   export OPHELOS_AUDIENCE='your_audience'")
        print("   export OPHELOS_ENVIRONMENT='staging'  # optional")
        return

    # Setup client
    client = setup_client()
    if not client:
        return

    try:
        tenant_operations(client)
        debt_operations(client)
        customer_operations(client)
        payment_operations(client)
        invoice_operations(client)
        invoice_model_operations(client)
        webhook_operations(client)
        demonstrate_api_error_handling(client)
        demonstrate_timeout_error_handling(client)
        demonstrate_unexpected_error_handling(client)
        demonstrate_cross_resource_iterators(client)

        print("\n" + "=" * 50)
        print("🎉 All examples completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"Error type: {type(e)}")


if __name__ == "__main__":
    main()
