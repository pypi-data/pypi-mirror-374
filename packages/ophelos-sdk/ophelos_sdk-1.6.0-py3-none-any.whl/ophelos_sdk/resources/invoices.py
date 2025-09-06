"""
Invoices resource manager for Ophelos API.
"""

from typing import Any, Dict, List, Optional, Union, cast

from ..models import Invoice, PaginatedResponse
from .base import BaseResource


class InvoicesResource(BaseResource):
    """Resource manager for invoice operations."""

    def get(self, debt_id: str, invoice_id: str, expand: Optional[List[str]] = None) -> Invoice:
        """
        Get a specific invoice for a debt.

        Args:
            debt_id: Debt ID
            invoice_id: Invoice ID
            expand: List of fields to expand (e.g., ["line_items"])

        Returns:
            Invoice instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get(
            f"debts/{debt_id}/invoices/{invoice_id}", params=params, return_response=True
        )
        return cast(Invoice, self._parse_response(response_tuple, Invoice))

    def create(self, debt_id: str, data: Union[Dict[str, Any], Invoice], expand: Optional[List[str]] = None) -> Invoice:
        """
        Create a new invoice for a debt.

        Args:
            debt_id: Debt ID
            data: Invoice data (dictionary) or Invoice model instance
            expand: List of fields to expand

        Returns:
            Created invoice instance
        """
        # Prepare data (handles both dict and model instances)
        if hasattr(data, "to_api_body"):
            api_data = data.to_api_body()
        else:
            api_data = data

        if expand:
            params = self._build_expand_params(expand)
            response_tuple = self.http_client.post(
                f"debts/{debt_id}/invoices", data=api_data, params=params, return_response=True
            )
        else:
            response_tuple = self.http_client.post(f"debts/{debt_id}/invoices", data=api_data, return_response=True)
        return cast(Invoice, self._parse_response(response_tuple, Invoice))

    def update(
        self, debt_id: str, invoice_id: str, data: Union[Dict[str, Any], Invoice], expand: Optional[List[str]] = None
    ) -> Invoice:
        """
        Update an invoice.

        Args:
            debt_id: Debt ID
            invoice_id: Invoice ID
            data: Updated invoice data (dictionary) or Invoice model instance
            expand: List of fields to expand

        Returns:
            Updated invoice instance
        """
        # Prepare data (handles both dict and model instances)
        if hasattr(data, "to_api_body"):
            api_data = data.to_api_body()
        else:
            api_data = data

        if expand:
            params = self._build_expand_params(expand)
            response_tuple = self.http_client.put(
                f"debts/{debt_id}/invoices/{invoice_id}", data=api_data, params=params, return_response=True
            )
        else:
            response_tuple = self.http_client.put(
                f"debts/{debt_id}/invoices/{invoice_id}", data=api_data, return_response=True
            )
        return cast(Invoice, self._parse_response(response_tuple, Invoice))

    def search(
        self,
        debt_id: str,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        Search invoices for a debt.

        Args:
            debt_id: Debt ID
            query: Search query string (e.g., "status:paid")
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated response with invoice data
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_tuple = self.http_client.get(f"debts/{debt_id}/invoices/search", params=params, return_response=True)
        return self._parse_list_response(response_tuple, Invoice)
