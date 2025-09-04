"""Tests for the Eastmoney Trading Agent"""

import os
from typing import Any

import pytest
from loguru import logger

from emta.core.agent import TradingAgent
from emta.models.trading import OrderType


@pytest.fixture(scope="session")  # type: ignore[misc]
def storage() -> dict[str, Any]:
    return {}


class TestTradingAgent:
    """Tests for the TradingAgent class"""

    def test_init(self) -> None:
        """Test TradingAgent initialization"""
        agent = TradingAgent()
        assert agent.username is None
        assert agent.password is None
        assert agent.is_logged_in is False

    def test_init_with_credentials(self) -> None:
        """Test TradingAgent initialization with credentials"""
        agent = TradingAgent("test_user", "test_pass")
        assert agent.username == "test_user"
        assert agent.password == "test_pass"

    def test_login(self, storage: dict[str, Any]) -> None:
        """Test TradingAgent login with credentials from environment variables"""
        logger.info("test_login")

        agent = TradingAgent(
            os.getenv("EM_USERNAME", "test_user"),
            os.getenv("EM_PASSWORD", "test_pass"),
        )
        result = agent.login()

        assert result is True
        assert agent.is_logged_in is True
        storage["agent"] = agent

    def test_get_account_info(self, storage: dict[str, Any]) -> None:
        """Test getting account information"""

        agent = storage["agent"]
        assert agent.is_logged_in is True

        account_info = agent.get_account_info()
        assert isinstance(account_info, dict)
        assert "username" in account_info
        assert "account_balance" in account_info

    def test_get_account_info_not_logged_in(self) -> None:
        """Test getting account info when not logged in"""
        agent = TradingAgent()
        account_info = agent.get_account_info()
        assert account_info == []

    def test_place_order(self, storage: dict[str, Any]) -> None:
        """Test placing an order"""
        agent = storage["agent"]
        orders = agent.place_order("000001", OrderType.BUY, 100, 11.5)
        storage["orders"] = orders
        assert orders is not None
        assert isinstance(orders, list)

    def test_place_order_not_logged_in(self) -> None:
        """Test placing an order when not logged in"""
        agent = TradingAgent()
        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        assert order_id is None

    def test_cancel_order(self, storage: dict[str, Any]) -> None:
        """Test cancelling an order"""
        agent = storage["agent"]
        orders = agent.query_orders()
        logger.info(orders)
        orders = storage["orders"]
        for order in orders:
            result = agent.cancel_order(order)
            assert result is True

    def test_cancel_order_not_logged_in(self) -> None:
        """Test cancelling an order when not logged in"""
        agent = TradingAgent()
        result = agent.cancel_order("test_order_id")
        assert result is False

    def test_query_order(self, storage: dict[str, Any]) -> None:
        """Test getting order status"""
        agent = storage["agent"]
        agent.query_orders()
        orders = agent.query_orders()

        logger.info(orders)
