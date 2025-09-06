"""Tests for port manager functionality."""

import socket
from unittest.mock import Mock, patch

from epic_llm.managers.port import PortManager


class TestPortManagerInitialization:
    """Test PortManager initialization."""

    def test_port_manager_creation(self):
        """Test creating port manager instance."""
        manager = PortManager()
        assert manager is not None
        assert manager.start_port == 8000
        assert manager.end_port == 8999
        assert manager.allocated_ports == set()

    def test_port_manager_custom_range(self):
        """Test port manager with custom port range."""
        manager = PortManager(start_port=9000, end_port=9100)
        assert manager.start_port == 9000
        assert manager.end_port == 9100


class TestPortAllocation:
    """Test port allocation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PortManager()

    def test_get_available_port_success(self):
        """Test getting an available port."""
        with patch.object(self.manager, "is_port_available", return_value=True):
            port = self.manager.get_available_port()
            assert port >= self.manager.start_port
            assert port <= self.manager.end_port
            assert port in self.manager.allocated_ports

    def test_get_available_port_with_preferred(self):
        """Test getting available port with preferred port."""
        preferred_port = 8080
        with patch.object(self.manager, "is_port_available", return_value=True):
            port = self.manager.get_available_port(preferred_port)
            assert port == preferred_port
            assert port in self.manager.allocated_ports

    def test_get_available_port_preferred_unavailable(self):
        """Test getting port when preferred port is unavailable."""
        preferred_port = 8080

        def mock_is_port_available(port):
            return port != preferred_port

        with patch.object(
            self.manager, "is_port_available", side_effect=mock_is_port_available
        ):
            port = self.manager.get_available_port(preferred_port)
            assert port != preferred_port
            assert port >= self.manager.start_port
            assert port <= self.manager.end_port
            assert port in self.manager.allocated_ports

    def test_get_available_port_all_ports_taken(self):
        """Test getting port when all ports in range are taken."""
        with patch.object(self.manager, "is_port_available", return_value=False):
            port = self.manager.get_available_port()
            assert port is None

    def test_get_available_port_skips_allocated(self):
        """Test that allocated ports are skipped."""
        # Pre-allocate a port
        self.manager.allocated_ports.add(8080)

        def mock_is_port_available(port):
            return port not in self.manager.allocated_ports

        with patch.object(
            self.manager, "is_port_available", side_effect=mock_is_port_available
        ):
            port = self.manager.get_available_port(8080)
            assert port != 8080


class TestPortChecking:
    """Test port availability checking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PortManager()

    def test_is_port_available_true(self):
        """Test checking available port."""
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None  # No exception = port available

            result = self.manager.is_port_available(8080)
            assert result is True
            mock_sock.bind.assert_called_once_with(("localhost", 8080))

    def test_is_port_available_false(self):
        """Test checking unavailable port."""
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.side_effect = OSError("Port in use")

            result = self.manager.is_port_available(8080)
            assert result is False

    def test_is_port_available_ipv6_fallback(self):
        """Test IPv6 fallback when IPv4 fails."""
        with patch("socket.socket") as mock_socket:
            mock_sock_v4 = Mock()
            mock_sock_v6 = Mock()

            def socket_side_effect(family, *args):
                if family == socket.AF_INET:
                    return mock_sock_v4
                elif family == socket.AF_INET6:
                    return mock_sock_v6
                return Mock()

            mock_socket.side_effect = socket_side_effect
            mock_sock_v4.__enter__.return_value = mock_sock_v4
            mock_sock_v6.__enter__.return_value = mock_sock_v6
            mock_sock_v4.bind.side_effect = OSError("IPv4 failed")
            mock_sock_v6.bind.return_value = None  # IPv6 succeeds

            result = self.manager.is_port_available(8080)
            assert result is True


class TestPortRelease:
    """Test port release functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PortManager()

    def test_release_port_success(self):
        """Test releasing an allocated port."""
        port = 8080
        self.manager.allocated_ports.add(port)

        self.manager.release_port(port)

        assert port not in self.manager.allocated_ports

    def test_release_port_not_allocated(self):
        """Test releasing a port that wasn't allocated."""
        port = 8080
        # Port not in allocated_ports initially

        # Should not raise an exception
        self.manager.release_port(port)

        assert port not in self.manager.allocated_ports

    def test_release_all_ports(self):
        """Test releasing all allocated ports."""
        ports = [8080, 8081, 8082]
        for port in ports:
            self.manager.allocated_ports.add(port)

        for port in ports:
            self.manager.release_port(port)

        assert len(self.manager.allocated_ports) == 0


class TestPortManagerEdgeCases:
    """Test edge cases and error conditions."""

    def test_port_manager_small_range(self):
        """Test port manager with very small range."""
        manager = PortManager(start_port=8000, end_port=8001)

        with patch.object(manager, "is_port_available", return_value=True):
            port1 = manager.get_available_port()
            port2 = manager.get_available_port()
            port3 = manager.get_available_port()  # Should be None

            assert port1 in [8000, 8001]
            assert port2 in [8000, 8001]
            assert port1 != port2
            assert port3 is None

    def test_port_manager_single_port_range(self):
        """Test port manager with single port range."""
        manager = PortManager(start_port=8000, end_port=8000)

        with patch.object(manager, "is_port_available", return_value=True):
            port1 = manager.get_available_port()
            port2 = manager.get_available_port()

            assert port1 == 8000
            assert port2 is None

    def test_port_manager_invalid_range(self):
        """Test port manager with invalid range."""
        # This tests the current implementation - it may need adjustment
        # if validation is added to the constructor
        manager = PortManager(start_port=9000, end_port=8000)

        with patch.object(manager, "is_port_available", return_value=True):
            port = manager.get_available_port()
            # With invalid range, should return None
            assert port is None

    def test_is_port_available_boundary_values(self):
        """Test port availability checking with boundary values."""
        manager = PortManager()

        # Test with port 0 (should work)
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None

            result = manager.is_port_available(0)
            assert result is True

        # Test with port 65535 (max port)
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock
            mock_sock.bind.return_value = None

            result = manager.is_port_available(65535)
            assert result is True

    def test_concurrent_port_allocation(self):
        """Test concurrent port allocation scenarios."""
        manager = PortManager()

        # Simulate race condition where port becomes unavailable
        # between check and allocation
        call_count = 0

        def mock_is_port_available(port):
            nonlocal call_count
            call_count += 1
            # First call returns True, subsequent calls False
            return call_count == 1

        with patch.object(
            manager, "is_port_available", side_effect=mock_is_port_available
        ):
            port = manager.get_available_port()
            # Should still get a port due to retry logic in range
            assert port is None or (
                port >= manager.start_port and port <= manager.end_port
            )


class TestPortManagerIntegration:
    """Test port manager integration scenarios."""

    def test_realistic_port_allocation_scenario(self):
        """Test realistic port allocation with some ports taken."""
        manager = PortManager(start_port=8000, end_port=8010)

        # Simulate some ports being taken
        taken_ports = {8001, 8003, 8005}

        def mock_is_port_available(port):
            return port not in taken_ports and port not in manager.allocated_ports

        with patch.object(
            manager, "is_port_available", side_effect=mock_is_port_available
        ):
            # Allocate several ports
            allocated = []
            for _ in range(5):
                port = manager.get_available_port()
                if port:
                    allocated.append(port)

            # Check that we got unique ports
            assert len(allocated) == len(set(allocated))
            # Check that none of the allocated ports were in taken_ports
            assert not any(port in taken_ports for port in allocated)

    def test_port_manager_state_consistency(self):
        """Test that port manager state remains consistent."""
        manager = PortManager()

        with patch.object(manager, "is_port_available", return_value=True):
            # Allocate some ports
            ports = []
            for _ in range(3):
                port = manager.get_available_port()
                if port:
                    ports.append(port)

            # Check state consistency
            assert len(manager.allocated_ports) == len(ports)
            for port in ports:
                assert port in manager.allocated_ports

            # Release one port
            if ports:
                manager.release_port(ports[0])
                assert ports[0] not in manager.allocated_ports
                assert len(manager.allocated_ports) == len(ports) - 1
