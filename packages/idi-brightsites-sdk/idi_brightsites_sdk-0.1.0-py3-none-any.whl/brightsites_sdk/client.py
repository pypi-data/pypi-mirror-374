"""Brightsites API client."""

from typing import Any

from httpx import Client, Response

from .models import OrdersList, Product, ProductOptionsList, ProductsList, ProductSubOptionsList


class BrightsitesServices:
    """A class wrapping Brightsites interaction."""

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 10.0,
    ) -> None:
        """Initialize the BrightsitesServices class."""
        self.client = Client(
            base_url=base_url,
            params={"token": token},
            timeout=timeout,
        )

    def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Response:
        """Make a request to Brightsites."""
        args: dict[str, str | dict[str, str]] = {
            "url": path,
            "method": method,
        }

        if params is not None:
            args["params"] = params

        if json is not None:
            args["json"] = json

        return self.client.request(**args)  # type: ignore[arg-type]

    def list_orders(self) -> OrdersList:
        """List orders."""
        response = self._make_request(
            method="GET",
            path="/orders",
        )
        response.raise_for_status()
        return OrdersList.model_validate(response.json())

    def list_products(self) -> ProductsList:
        """List products."""
        response = self._make_request(
            method="GET",
            path="/products",
        )
        response.raise_for_status()
        return ProductsList.model_validate(response.json())

    def get_product(self, product_id: int) -> Product:
        """Get a product by ID."""
        response = self._make_request(
            method="GET",
            path=f"/products/{product_id}",
        )
        response.raise_for_status()
        return Product.model_validate(response.json())

    def list_product_options(self, product_id: int) -> ProductOptionsList:
        """Get product options."""
        response = self._make_request(
            method="GET",
            path=f"/products/{product_id}/options",
        )
        response.raise_for_status()
        return ProductOptionsList.model_validate(response.json())

    def list_product_sub_options(self, product_id: int, option_id: int) -> ProductSubOptionsList:
        """Get product sub-options."""
        response = self._make_request(
            method="GET",
            path=f"/products/{product_id}/options/{option_id}/sub_options",
        )
        response.raise_for_status()
        return ProductSubOptionsList.model_validate(response.json())
