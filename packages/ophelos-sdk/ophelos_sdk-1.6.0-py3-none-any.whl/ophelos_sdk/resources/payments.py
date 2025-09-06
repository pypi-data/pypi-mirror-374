"""
Payments resource for Ophelos API.
"""

from typing import Any, Dict, List, Optional, Union, cast

from ..models import PaginatedResponse, Payment
from .base import BaseResource


class PaymentsResource(BaseResource):
    """Manages payment operations."""

    def list(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List all payments.

        Args:
            limit: Maximum number of results to return
            after: Cursor for pagination (after this ID)
            before: Cursor for pagination (before this ID)
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated list of payments
        """
        params = self._build_list_params(limit=limit, after=after, before=before, expand=expand, **kwargs)
        response_tuple = self.http_client.get("payments", params=params, return_response=True)
        return self._parse_list_response(response_tuple, Payment)

    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        expand: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        Search payments.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            expand: List of fields to expand
            **kwargs: Additional query parameters

        Returns:
            Paginated search results
        """
        params = self._build_search_params(query, limit, expand, **kwargs)
        response_tuple = self.http_client.get("payments/search", params=params, return_response=True)
        return self._parse_list_response(response_tuple, Payment)

    def get(self, payment_id: str, expand: Optional[List[str]] = None) -> Payment:
        """
        Get a specific payment by ID.

        Args:
            payment_id: Payment ID
            expand: List of fields to expand

        Returns:
            Payment instance
        """
        params = self._build_expand_params(expand)
        response_tuple = self.http_client.get(f"payments/{payment_id}", params=params, return_response=True)
        return cast(Payment, self._parse_response(response_tuple, Payment))

    def create(self, debt_id: str, data: Union[Dict[str, Any], Payment], expand: Optional[List[str]] = None) -> Payment:
        """
        Create a payment for a debt.

        Args:
            debt_id: Debt ID
            data: Payment data (dictionary) or Payment model instance
            expand: List of fields to expand

        Returns:
            Created payment instance
        """
        # Prepare data (handles both dict and model instances)
        if hasattr(data, "to_api_body"):
            api_data = data.to_api_body()
        else:
            api_data = data

        if expand:
            params = self._build_expand_params(expand)
            response_tuple = self.http_client.post(
                f"debts/{debt_id}/payments", data=api_data, params=params, return_response=True
            )
        else:
            response_tuple = self.http_client.post(f"debts/{debt_id}/payments", data=api_data, return_response=True)
        return cast(Payment, self._parse_response(response_tuple, Payment))

    def update(
        self,
        debt_id: str,
        payment_id: str,
        data: Union[Dict[str, Any], Payment],
        expand: Optional[List[str]] = None,
    ) -> Payment:
        """
        Update a payment for a debt.

        Args:
            debt_id: Debt ID
            payment_id: Payment ID
            data: Updated payment data (dictionary) or Payment model instance
            expand: List of fields to expand

        Returns:
            Updated payment instance
        """
        # Prepare data (handles both dict and model instances)
        if hasattr(data, "to_api_body"):
            api_data = data.to_api_body()
        else:
            api_data = data

        if expand:
            params = self._build_expand_params(expand)
            response_tuple = self.http_client.put(
                f"debts/{debt_id}/payments/{payment_id}", data=api_data, params=params, return_response=True
            )
        else:
            response_tuple = self.http_client.put(
                f"debts/{debt_id}/payments/{payment_id}", data=api_data, return_response=True
            )
        return cast(Payment, self._parse_response(response_tuple, Payment))
