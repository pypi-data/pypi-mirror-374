"""Browser Agent for CLI - Natural language browser automation.

This module provides a browser automation agent that understands natural language
requests for taking screenshots and other browser operations via the ConnectOnion CLI.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict
import re
from connectonion import Agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check Playwright availability
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Path to the browser agent system prompt
PROMPT_PATH = Path(__file__).parent / "prompts" / "browser_agent.md"


class BrowserAutomation:
    """Browser automation for screenshots."""
    
    def __init__(self):
        self._screenshots = []
    
    def take_screenshot(self, url: str, path: str = "", 
                       width: int = 1920, height: int = 1080,
                       full_page: bool = False) -> str:
        """Take a screenshot of the specified URL.
        
        Args:
            url: The URL to screenshot (e.g., "localhost:3000", "example.com")
            path: Optional path to save the screenshot (auto-generates if empty)
            width: Viewport width in pixels (default 1920)
            height: Viewport height in pixels (default 1080)
            full_page: If True, captures entire page height
            
        Returns:
            Success or error message
        """
        if not PLAYWRIGHT_AVAILABLE:
            return 'Browser tools not installed. Run: pip install playwright && playwright install chromium'
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}' if '.' in url else f'http://{url}'
        
        # Generate filename if needed
        if not path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = f'screenshot_{timestamp}.png'
        elif not path.endswith(('.png', '.jpg', '.jpeg')):
            path += '.png'
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Take screenshot
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": width, "height": height})
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.screenshot(path=path, full_page=full_page)
            browser.close()
        
        self._screenshots.append(path)
        return f'Screenshot saved: {path}'
    
    def screenshot_with_iphone_viewport(self, url: str, path: str = "") -> str:
        """Take a screenshot with iPhone viewport (390x844)."""
        return self.take_screenshot(url, path, width=390, height=844)
    
    def screenshot_with_ipad_viewport(self, url: str, path: str = "") -> str:
        """Take a screenshot with iPad viewport (768x1024)."""
        return self.take_screenshot(url, path, width=768, height=1024)
    
    def screenshot_with_desktop_viewport(self, url: str, path: str = "") -> str:
        """Take a screenshot with desktop viewport (1920x1080)."""
        return self.take_screenshot(url, path, width=1920, height=1080)


# Removed create_browser_agent to reduce indirection; agent is constructed inline


# Removed thin wrapper to reduce indirection


def execute_browser_command(command: str) -> Dict:
    """Execute a browser command using natural language if possible, otherwise fall back.

    Returns dict with keys: success, and path or error.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'sk-your-key-here':
        return {
            'success': False,
            'error': 'Natural language browser agent unavailable. Set OPENAI_API_KEY and try again.'
        }

    browser = BrowserAutomation()
    agent = Agent(
        name="browser_cli",
        system_prompt=PROMPT_PATH,
        tools=[browser],
        max_iterations=10
    )
    response = agent.input(command)
    if 'saved' in response.lower():
        path_match = re.search(r'([^\s]+\.(?:png|jpg|jpeg))', response, re.IGNORECASE)
        path = path_match.group(1) if path_match else 'screenshot.png'
        return {'success': True, 'path': path}
    return {'success': False, 'error': response}


# Legacy test helpers removed to simplify API; agent now handles parameter prompting