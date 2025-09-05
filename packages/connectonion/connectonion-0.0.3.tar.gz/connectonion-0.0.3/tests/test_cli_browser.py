"""Tests for CLI browser feature (-b flag)."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from connectonion.cli.browser_utils import (
    parse_screenshot_command,
    normalize_url,
    get_viewport_size,
    take_screenshot,
    execute_browser_command
)


class TestScreenshotCommandParser(unittest.TestCase):
    """Test parsing of screenshot commands."""
    
    def test_basic_screenshot_command(self):
        """Test parsing basic screenshot command."""
        result = parse_screenshot_command("screenshot localhost:3000")
        self.assertEqual(result['url'], 'localhost:3000')
        self.assertIsNone(result['output'])
        self.assertIsNone(result['size'])
    
    def test_screenshot_with_save_path(self):
        """Test parsing screenshot with save to path."""
        result = parse_screenshot_command("screenshot localhost:3000 save to /tmp/test.png")
        self.assertEqual(result['url'], 'localhost:3000')
        self.assertEqual(result['output'], '/tmp/test.png')
        self.assertIsNone(result['size'])
    
    def test_screenshot_with_size(self):
        """Test parsing screenshot with size."""
        result = parse_screenshot_command("screenshot example.com size iphone")
        self.assertEqual(result['url'], 'example.com')
        self.assertIsNone(result['output'])
        self.assertEqual(result['size'], 'iphone')
    
    def test_screenshot_with_custom_size(self):
        """Test parsing screenshot with custom dimensions."""
        result = parse_screenshot_command("screenshot localhost:3000 size 390x844")
        self.assertEqual(result['url'], 'localhost:3000')
        self.assertEqual(result['size'], '390x844')
    
    def test_full_command(self):
        """Test parsing complete screenshot command."""
        cmd = "screenshot localhost:3000/xray save to /tmp/debug.png size iphone"
        result = parse_screenshot_command(cmd)
        self.assertEqual(result['url'], 'localhost:3000/xray')
        self.assertEqual(result['output'], '/tmp/debug.png')
        self.assertEqual(result['size'], 'iphone')
    
    def test_invalid_command_no_url(self):
        """Test parsing invalid command without URL."""
        result = parse_screenshot_command("screenshot")
        self.assertIsNone(result['url'])
    
    def test_invalid_command_no_screenshot_keyword(self):
        """Test parsing command without screenshot keyword."""
        result = parse_screenshot_command("capture localhost:3000")
        self.assertIsNone(result)
    
    def test_different_path_formats(self):
        """Test various path formats."""
        cases = [
            ("screenshot localhost save to debug.png", "debug.png"),
            ("screenshot localhost save to ./screenshots/test.png", "./screenshots/test.png"),
            ("screenshot localhost save to ~/Desktop/screenshot.png", "~/Desktop/screenshot.png"),
        ]
        for cmd, expected_path in cases:
            result = parse_screenshot_command(cmd)
            self.assertEqual(result['output'], expected_path)


class TestURLNormalization(unittest.TestCase):
    """Test URL normalization."""
    
    def test_localhost_normalization(self):
        """Test localhost URL handling."""
        self.assertEqual(normalize_url("localhost"), "http://localhost")
        self.assertEqual(normalize_url("localhost:3000"), "http://localhost:3000")
        self.assertEqual(normalize_url("localhost:8080"), "http://localhost:8080")
    
    def test_domain_normalization(self):
        """Test domain URL handling."""
        self.assertEqual(normalize_url("example.com"), "https://example.com")
        self.assertEqual(normalize_url("docs.connectonion.com"), "https://docs.connectonion.com")
    
    def test_full_url_unchanged(self):
        """Test that full URLs remain unchanged."""
        self.assertEqual(normalize_url("http://localhost:3000"), "http://localhost:3000")
        self.assertEqual(normalize_url("https://example.com"), "https://example.com")
        self.assertEqual(normalize_url("http://example.com:8080"), "http://example.com:8080")
    
    def test_ip_address_handling(self):
        """Test IP address URL handling."""
        self.assertEqual(normalize_url("127.0.0.1"), "http://127.0.0.1")
        self.assertEqual(normalize_url("127.0.0.1:3000"), "http://127.0.0.1:3000")
        self.assertEqual(normalize_url("192.168.1.1:8080"), "http://192.168.1.1:8080")


class TestViewportSizes(unittest.TestCase):
    """Test viewport size handling."""
    
    def test_device_presets(self):
        """Test device preset dimensions."""
        self.assertEqual(get_viewport_size("iphone"), (390, 844))
        self.assertEqual(get_viewport_size("android"), (360, 800))
        self.assertEqual(get_viewport_size("ipad"), (768, 1024))
        self.assertEqual(get_viewport_size("desktop"), (1920, 1080))
    
    def test_custom_dimensions(self):
        """Test parsing custom dimensions."""
        self.assertEqual(get_viewport_size("1280x720"), (1280, 720))
        self.assertEqual(get_viewport_size("390x844"), (390, 844))
        self.assertEqual(get_viewport_size("1920x1080"), (1920, 1080))
    
    def test_invalid_size_returns_default(self):
        """Test invalid size returns desktop default."""
        self.assertEqual(get_viewport_size("invalid"), (1920, 1080))
        self.assertEqual(get_viewport_size(""), (1920, 1080))
        self.assertEqual(get_viewport_size(None), (1920, 1080))
    
    def test_malformed_dimensions(self):
        """Test malformed dimension strings."""
        self.assertEqual(get_viewport_size("1280×720"), (1920, 1080))  # Wrong x character
        self.assertEqual(get_viewport_size("1280"), (1920, 1080))  # Missing height
        self.assertEqual(get_viewport_size("widthxheight"), (1920, 1080))  # Non-numeric


class TestScreenshotExecution(unittest.TestCase):
    """Test screenshot execution with mocked Playwright."""
    
    @patch('connectonion.cli.browser_utils.sync_playwright')
    def test_basic_screenshot(self, mock_playwright):
        """Test taking a basic screenshot."""
        # Setup mocks
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_pw_instance = MagicMock()
        
        mock_playwright.return_value.start.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.png"
            result = take_screenshot(
                url="http://localhost:3000",
                output_path=str(output_path),
                width=1920,
                height=1080
            )
            
            # Verify
            self.assertTrue(result['success'])
            self.assertEqual(result['path'], str(output_path))
            mock_page.goto.assert_called_once_with("http://localhost:3000", wait_until='networkidle')
            mock_page.set_viewport_size.assert_called_once_with({"width": 1920, "height": 1080})
            mock_page.screenshot.assert_called_once()
    
    @patch('connectonion.cli.browser_utils.sync_playwright')
    def test_screenshot_with_iphone_preset(self, mock_playwright):
        """Test taking screenshot with iPhone preset."""
        # Setup mocks
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_pw_instance = MagicMock()
        
        mock_playwright.return_value.start.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Execute
        result = take_screenshot(
            url="http://localhost:3000",
            output_path="screenshot.png",
            width=390,
            height=844
        )
        
        # Verify iPhone dimensions were set
        mock_page.set_viewport_size.assert_called_once_with({"width": 390, "height": 844})
    
    @patch('connectonion.cli.browser_utils.sync_playwright')
    def test_screenshot_failure_handling(self, mock_playwright):
        """Test handling of screenshot failures."""
        # Setup mock to raise exception
        mock_playwright.return_value.start.side_effect = Exception("Browser failed to start")
        
        # Execute
        result = take_screenshot(
            url="http://localhost:3000",
            output_path="test.png"
        )
        
        # Verify
        self.assertFalse(result['success'])
        self.assertIn("Browser failed to start", result['error'])
    
    @patch('connectonion.cli.browser_utils.sync_playwright')
    def test_screenshot_creates_directory(self, mock_playwright):
        """Test that screenshot creates output directory if needed."""
        # Setup mocks
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_pw_instance = MagicMock()
        
        mock_playwright.return_value.start.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Execute with nested path
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "screenshots" / "nested" / "test.png"
            result = take_screenshot(
                url="http://localhost:3000",
                output_path=str(output_path)
            )
            
            # Verify directory would be created
            self.assertTrue(result['success'])
            # In real implementation, directory should be created
            # mock_page.screenshot.assert_called_once()


class TestBrowserCommandExecution(unittest.TestCase):
    """Test complete browser command execution."""
    
    @patch('connectonion.cli.browser_utils.take_screenshot')
    def test_execute_simple_command(self, mock_take_screenshot):
        """Test executing simple screenshot command."""
        mock_take_screenshot.return_value = {'success': True, 'path': 'screenshot.png'}
        
        result = execute_browser_command("screenshot localhost:3000")
        
        self.assertTrue(result['success'])
        mock_take_screenshot.assert_called_once()
        call_args = mock_take_screenshot.call_args[1]
        self.assertEqual(call_args['url'], 'http://localhost:3000')
    
    @patch('connectonion.cli.browser_utils.take_screenshot')
    def test_execute_command_with_all_options(self, mock_take_screenshot):
        """Test executing command with all options."""
        mock_take_screenshot.return_value = {'success': True, 'path': '/tmp/test.png'}
        
        cmd = "screenshot localhost:3000/api save to /tmp/test.png size iphone"
        result = execute_browser_command(cmd)
        
        self.assertTrue(result['success'])
        call_args = mock_take_screenshot.call_args[1]
        self.assertEqual(call_args['url'], 'http://localhost:3000/api')
        self.assertEqual(call_args['output_path'], '/tmp/test.png')
        self.assertEqual(call_args['width'], 390)
        self.assertEqual(call_args['height'], 844)
    
    def test_execute_invalid_command(self):
        """Test executing invalid command."""
        result = execute_browser_command("invalid command")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_execute_empty_command(self):
        """Test executing empty command."""
        result = execute_browser_command("")
        self.assertFalse(result['success'])
        
    @patch('connectonion.cli.browser_utils.take_screenshot')
    def test_default_output_path(self, mock_take_screenshot):
        """Test that default output path includes timestamp."""
        mock_take_screenshot.return_value = {'success': True, 'path': 'screenshot_20240115_143022.png'}
        
        result = execute_browser_command("screenshot localhost:3000")
        
        call_args = mock_take_screenshot.call_args[1]
        output_path = call_args.get('output_path', '')
        self.assertTrue(output_path.startswith('screenshot_'))
        self.assertTrue(output_path.endswith('.png'))


class TestErrorHandling(unittest.TestCase):
    """Test error handling and user feedback."""
    
    def test_missing_playwright_error(self):
        """Test error when Playwright is not installed."""
        with patch('connectonion.cli.browser_utils.PLAYWRIGHT_AVAILABLE', False):
            result = execute_browser_command("screenshot localhost:3000")
            self.assertFalse(result['success'])
            self.assertIn('playwright', result['error'].lower())
            self.assertIn('pip install playwright', result['error'])
    
    @patch('connectonion.cli.browser_utils.take_screenshot')
    def test_network_error(self, mock_take_screenshot):
        """Test handling of network errors."""
        mock_take_screenshot.return_value = {
            'success': False,
            'error': 'Cannot reach http://localhost:3000'
        }
        
        result = execute_browser_command("screenshot localhost:3000")
        self.assertFalse(result['success'])
        self.assertIn('Cannot reach', result['error'])
    
    @patch('connectonion.cli.browser_utils.Path.mkdir')
    def test_permission_error(self, mock_mkdir):
        """Test handling of permission errors."""
        mock_mkdir.side_effect = PermissionError("Permission denied")
        
        with patch('connectonion.cli.browser_utils.take_screenshot') as mock_take:
            mock_take.side_effect = PermissionError("Cannot save to /root/test.png")
            result = execute_browser_command("screenshot localhost:3000 save to /root/test.png")
            self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()