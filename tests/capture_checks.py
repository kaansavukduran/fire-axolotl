# SPDX-License-Identifier: MPL-2.0
import unittest
from unittest.mock import Mock, patch
from selenium.common.exceptions import WebDriverException
from gecko_controls import capture_screenshot


class ScreenshotTests(unittest.TestCase):
    def test_transient_native_snapshot_is_retried_but_persistent_failure_is_not_hidden(self):
        driver = Mock()
        transient = WebDriverException('Unable to capture screenshot: ')
        with patch('gecko_controls.time.sleep'):
            driver.save_screenshot.side_effect = [transient, True]
            self.assertTrue(capture_screenshot(driver, 'native.png'))
            self.assertEqual(driver.save_screenshot.call_count, 2)
            driver.reset_mock()
            driver.save_screenshot.side_effect = transient
            with self.assertRaises(WebDriverException):
                capture_screenshot(driver, 'native.png')
            self.assertEqual(driver.save_screenshot.call_count, 3)

    def test_unrelated_webdriver_failure_is_immediate(self):
        driver = Mock()
        driver.save_screenshot.side_effect = WebDriverException('Disconnected browser')
        with self.assertRaises(WebDriverException):
            capture_screenshot(driver, 'native.png')
        self.assertEqual(driver.save_screenshot.call_count, 1)
