########################################################################################################################
########################################################################################################################
###   Selenium driver for WhisperTrades.com API                                                                      ###
###                                                                                                                  ###
###   Authored by Paul Nobrgea   Contact: Paul@PaulNobrega.net                                                       ###
###   Python Version 3.10                                                                                            ###
########################################################################################################################
########################################################################################################################
import os
import platform
import warnings
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import copy
import chromedriver_autoinstaller


class SeleniumDriver:
    """
    Selenium-based driver for automating WhisperTrades.com UI actions.

    Handles login, bot management, and settings manipulation via browser automation.
    Designed for robust, isolated browser sessions.

    Args:
        endpts: API endpoints object for broker/bot lookups.
    """

    def _require_enabled(method):
        def wrapper(self, *args, **kwargs):
            if not getattr(self, 'is_enabled', False):
                raise Exception('Selenium Driver is not enabled. You must first call WD.via_selenium.enable(user_name, password, ...) with valid WhisperTrades credentials before using via_selenium functions.')
            return method(self, *args, **kwargs)
        return wrapper

    def __init__(self, endpts: object) -> None:
        self._endpts: object = endpts
        self.webdriver: uc.Chrome | None = None
        self.headless: bool | None = None
        self.verbose: bool | None = None
        self.user_name: str | None = None
        self.password: str | None = None
        self.delay_time_sec: int | None = None
        self._session_start_time: datetime | None = None
        self.login_url: str | None = None
        self.logout_url: str | None = None
        self.is_enabled: bool = False
        self._profile_dir: str | None = None
        return


    def __enter__(self) -> 'SeleniumDriver':
        """
        Enable use as a context manager (with statement).
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Cleanup resources when object is destroyed or context exits.
        """
        import shutil
        if self.webdriver is not None:
            self.webdriver.quit()
        if self._profile_dir:
            try:
                shutil.rmtree(self._profile_dir, ignore_errors=True)
            except Exception as e:
                warnings.warn(f'Failed to remove temp Chrome profile dir: {e}')
        return


    @_require_enabled
    def close(self) -> None:
        """
        Explicitly destroy the object and cleanup resources.
        """
        self.__exit__(None, None, None)
        return

    @_require_enabled
    def __configure_web_driver(self) -> None:
        """
        Configure and launch the Selenium browser with unique user profile for isolation.
        """

        def __get_chrome_version() -> int:
            os_name = platform.system()
            try:
                from chromedriver_autoinstaller.utils import get_chrome_version
                return int(get_chrome_version().split('.')[0])
            except Exception:
                if os_name.lower() == 'windows':
                    try:
                        return int(os.popen('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').read().split('REG_SZ')[-1].strip().split('.')[0])
                    except Exception:
                        raise Exception('Unable to determine Chrome version on Windows!')
                elif os_name.lower() == 'linux':
                    try:
                        ver = int(os.popen('chromium --version').read().split()[1].split('.')[0])
                    except Exception:
                        ver = int(os.popen('google-chrome --version').read().split()[-1].split('.')[0])
                    return ver
                else:
                    raise Exception('Incompatible operating system!')

        def __set_chrome_options(self_ref) -> uc.ChromeOptions:
            import tempfile
            options = uc.ChromeOptions()
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4515.159 Safari/537.36'
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')
            options.add_argument('--lang=en-US')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'--user-agent={user_agent}')
            # Add a unique user-data-dir for each instance to prevent cross talk
            self_ref._profile_dir = tempfile.mkdtemp(prefix="wt_chrome_profile_")
            options.add_argument(f'--user-data-dir={self_ref._profile_dir}')
            if self_ref.headless:
                options.add_argument('--headless')
            chrome_preferences = {'profile.default_content_settings': {"images": 2}}
            options.experimental_options["prefs"] = chrome_preferences
            return options

        try:
            chromedriver_autoinstaller.install()
        except Exception as e:
            warnings.warn(f'Could not auto-install chromedriver: {e}')

        try:
            self.webdriver = uc.Chrome(options=__set_chrome_options(self), version_main=__get_chrome_version())
        except Exception as e:
            warnings.warn(f'Could not start Chrome with detected version: {e}. Trying fallback version 114.')
            self.webdriver = uc.Chrome(options=__set_chrome_options(self), version_main=114)
        return

    @_require_enabled
    def __restart_webdriver(self) -> None:
        """
        Quit webdriver and reconfigure a new browser session.
        """
        if self.webdriver:
            self.webdriver.quit()
        self.__configure_web_driver()
        return
    
    @_require_enabled
    def __on_error_404(self, warn_except: str, error_str: str) -> bool:
        is_404 = True if 'page not found' in self.webdriver.title else False
        if is_404 and 'warn' in warn_except.lower():
            warnings.warn(error_str)
            return True
        elif is_404 and 'except' in warn_except.lower():
            raise Exception(error_str)
        return False

    @_require_enabled
    def __get_url_and_wait(self, url: str) -> bool:
        """
        Get specified url via self.webdriver. Wait for page load using Selenium's WebDriverWait.

        :param url: WhisperTrades.com url
        :type url: str
        :return: Bool value of successful url load
        :rtype: bool
        :raises Exception: If url cannot load within 2 seconds.
        """
        self.log_in_if_not()
        self.webdriver.get(url)
        try:
            WebDriverWait(self.webdriver, 2).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        except Exception:
            self.webdriver.get(url)
            try:
                WebDriverWait(self.webdriver, 2).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            except Exception:
                self._session_start_time = self._session_start_time - timedelta(minutes=60)
                raise Exception(f'UNABLE TO LOAD {url}')
        self._session_start_time = datetime.now()
        return False if self.__on_error_404('warn', f'Error 404: INVALID URL {url}') else True

    @_require_enabled
    def __authorization(self) -> bool:
        """
        Login to whispertrades.com via web UI login page

        :return: Bool value of authorization state
        :rtype: bool
        """

        if not self.is_enabled:
            raise Exception('Selenium Driver is not enabled.  Enabled command must be run first. Example:\nWD.via_selenium.enable(user_name: str, password: str, is_verbose: bool = False, is_headless: bool = True)')
        
        self.webdriver.get(self.login_url)
        time.sleep(1)
        username = self.webdriver.find_element(by=By.NAME, value="email")
        password = self.webdriver.find_element(by=By.NAME, value="password")
        login_btn = self.webdriver.find_element(by=By.CLASS_NAME, value="bg-green-primary")
        username.send_keys(self.user_name)
        password.send_keys(self.password)
        login_btn.click()
        time.sleep(1)
        self.__on_error_404('except', f'UNABLE TO LOGIN TO WHISPERTRADES.COM')
        self._session_start_time = datetime.now()
        return True

    def enable(self, user_name: str, password: str, is_verbose: bool = False, is_headless: bool = True) -> None:
        self.is_enabled = True
        self.webdriver = None
        self.headless = is_headless
        self.verbose = is_verbose
        self.user_name = user_name
        self.password = password
        self.delay_time_sec = 1
        self._session_start_time = datetime.now()
        self.login_url = "https://whispertrades.com/login"
        self.logout_url = "https://whispertrades.com/logout"
        self.__configure_web_driver()
        self.__authorization()
        self.current_bots = {}
        return
    

    @_require_enabled
    def is_logged_in(self) -> bool:
        """
        Determine if logged in by 1) if last session was less than 5 minutes ago or 2) presence of url redirect at login url

        :return: Bool value of logged in state
        :rtype: bool
        """
        if self._session_start_time + timedelta(minutes=2) > datetime.now():
            return True
        self.webdriver.get(self.login_url)
        time.sleep(0.3)
        return True if self.webdriver.current_url != self.login_url else False

    @_require_enabled
    def log_in_if_not(self) -> bool:
        """
        Login if not currently logged in

        :return: Bool value of logged in state
        :rtype: bool
        """
        if self.is_logged_in():
            return True
        else:
            for i in range(3):
                if self.__authorization():
                    break
            return self.is_logged_in()

    @_require_enabled
    def renew_accesss_token(self) -> bool:
        """
        Log out user and login again.

        :return: Bool value of authorization state
        :rtype: bool
        """
        self.revoke_accesss_token()
        return self.__authorization()

    @_require_enabled
    def revoke_accesss_token(self) -> None:
        """
        Log out user.
        """
        self.webdriver.get(self.logout_url)
        return
    
    @_require_enabled
    def __update_field(self, field, value) -> None:
        """
        Update a form field with a new value using keyboard shortcuts.
        Uses BACKSPACE to clear number fields, since DELETE may not work for <input type="number">.
        """
        from selenium.webdriver.common.keys import Keys
        try:
            # Try to clear with BACKSPACE (repeat 10 times)
            field.click()
            field.send_keys(Keys.END)
            for _ in range(10):
                field.send_keys(Keys.BACKSPACE)
            if value:
                field.send_keys(str(value))
        except Exception as e:
            warnings.warn(f'Failed to update field: {e}')
        return

    @_require_enabled
    def renew_schwab_connection(self, schwab_user: str, schwab_pass: str, blacklist: list=[]) -> bool:
        """
        Renew schwab connection with passed schwab credentials
        
        :param schwab_user: Schwab User Name
        :type schwab_user: string
        :param schwab_pass: Schwab Password
        :type schwab_pass: string
        :param blacklist: List of schwab WT broker numbers to not renew
        :type blacklist: list
        :return: Success as True or False
        :rtype: bool
        """

        def __find_and_wait(id='', timeout=5):
            try:
                element = WebDriverWait(self.webdriver, timeout).until(
                    EC.presence_of_element_located((By.ID, id))
                )
                if 'traceback' in element.text.lower():
                    raise NoSuchElementException
                return element
            except Exception:
                return None

        def __click_by_id_via_js(id):
            btn = __find_and_wait(id=id)
            if btn:
                return self.webdriver.execute_script ("arguments[0].click();",btn)
            return None
        
        def __click_by_id(id):
            element = __find_and_wait(id=id)
            if element:
                try:
                    return element.click()
                except Exception as e:
                    warnings.warn(f'Failed to click element by ID {id}: {e}')
            else:
                try:
                    __click_by_id_via_js(id)
                except Exception as e:
                    warnings.warn(f'Failed to click element by ID {id} via JS: {e}')
            return None

        all_brokers = self._endpts.brokers.get_all_broker_connections()
        connections = [d for d in all_brokers if d['broker'].lower() == 'schwab' and d['number'] not in blacklist]

        for c in connections:
            method = 'renew' if c['status'].lower() == 'active' else 'enable'
            schwab_renew_url = f"https://whispertrades.com/broker_connections/{c['number']}/{method}"
            print(f'Renew URL: {schwab_renew_url}')
            self.__get_url_and_wait(schwab_renew_url)
            user_field = __find_and_wait(id='loginIdInput')
            pass_field = __find_and_wait(id='passwordInput')
            login_btn = __find_and_wait(id='btnLogin')
            self.__update_field(user_field, schwab_user)
            self.__update_field(pass_field, schwab_pass)
            login_btn.click()

            new_device = None
            try:
                # Wait for either 'mobile_approve' or 'otp_sms' to appear (max 10s)
                WebDriverWait(self.webdriver, 10).until(
                    lambda d: d.find_elements(By.ID, 'mobile_approve') or d.find_elements(By.ID, 'otp_sms')
                )
                if self.webdriver.find_elements(By.ID, 'mobile_approve'):
                    id_selection = 'mobile_approve'
                    new_device = __click_by_id(id_selection)
                    try:
                        # Wait for the 'Yes, remember this device' radio button to be clickable
                        remember_radio = WebDriverWait(self.webdriver, 10).until(
                            EC.element_to_be_clickable((By.ID, 'remember-device-yes-content'))
                        )
                        remember_radio.click()
                        # Wait for the Continue button to be clickable and click it
                        continue_btn = WebDriverWait(self.webdriver, 10).until(
                            EC.element_to_be_clickable((By.ID, 'btnContinue'))
                        )
                        continue_btn.click()
                    except Exception as e:
                        warnings.warn(f'2FA remember device page not found or could not interact: {e}')
                elif self.webdriver.find_elements(By.ID, 'otp_sms'):
                    id_selection = 'otp_sms'
                    new_device = __click_by_id(id_selection)
                else:
                    warnings.warn('Neither mobile nor sms approval options found after waiting.')
                
            except Exception as e:
                warnings.warn(f'Failed to find mobile or sms approval options on page: {e}')
                new_device = None
            
            # Accept Terms Page
            if new_device:
                # If device is not yet trusted
                new_device.click()
            try:
                accept_terms = WebDriverWait(self.webdriver, 10).until(EC.element_to_be_clickable((By.ID, 'acceptTerms')))
                accept_terms.click()
                clicks = ['submit-btn', 'agree-modal-btn-', 'submit-btn']
                for c in clicks:
                    __click_by_id(c)
                confirm = WebDriverWait(self.webdriver, 10).until(EC.element_to_be_clickable((By.ID, 'submit-btn')))
                confirm.click()
            except Exception as e:
                warnings.warn(f'Failed to accept terms: {e}')
        return True

    @_require_enabled
    def get_entry_settings(self, bot_num: str) -> dict:
            """
            Get current WT Bot Entry Settings of specified bot number
            Scrapes all entry fields from the WhisperTrades bot form, including frequency, allocation, DTEs, strike selection, filters, toggles, etc.
            Handles missing/optional fields robustly.
            :param bot_num: WhisperTrades bot Number
            :type bot_num: string
            :return: Dictionary of settings
            :rtype: dict
            """

            # Helper functions must be defined before use
            def safe_find_value(by, value, attr='value', default=None):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.get_attribute(attr)
                except Exception:
                    return default

            def safe_find_checkbox(by, value, default=False):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.is_selected()
                except Exception:
                    return default

            def safe_find_select(by, value, default=None):
                try:
                    el = self.webdriver.find_element(by=by, value=value)
                    return el.get_attribute('value')
                except Exception:
                    return default

            wt_entry_edit_url = f'https://whispertrades.com/bots/{bot_num}/entry/edit'
            self.__get_url_and_wait(wt_entry_edit_url)

            # --- Allocation Section ---
            settings = {}
            # Frequency (dropdown)
            settings['frequency'] = safe_find_select(By.ID, 'form.frequency')
            # Maximum Entries Per Day (dropdown)
            settings['maximum_entries_per_day'] = safe_find_select(By.ID, 'form.maximum_entries_per_day')
            # Maximum Concurrent Positions (dropdown)
            settings['maximum_concurrent_positions'] = safe_find_select(By.ID, 'form.maximum_concurrent_positions')
            # Day of Week (dropdown)
            settings['day_of_week'] = safe_find_select(By.ID, 'form.day_of_week')
            # Allocation Type (dropdown)
            settings['allocation_type'] = safe_find_select(By.ID, 'form.allocation_type')
            # Contract Quantity (number input)
            settings['contract_quantity'] = safe_find_value(By.ID, 'form.allocation_quantity')
            # Leverage Amount
            settings['leverage_amount'] = safe_find_value(By.ID, 'form.allocation_leverage')
            # Allocation Percent 
            settings['percent_of_portfolio'] = safe_find_value(By.ID, 'form.allocation_percent')

            # --- Strike Selection Section ---
            # DTEs
            settings['minimum_days_to_expiration'] = safe_find_value(By.ID, 'form.minimum_days_to_expiration')
            settings['target_days_to_expiration'] = safe_find_value(By.ID, 'form.target_days_to_expiration')
            settings['maximum_days_to_expiration'] = safe_find_value(By.ID, 'form.maximum_days_to_expiration')

            # Put Short Strike Target Type (dropdown)
            settings['put_short_strike_type'] = safe_find_select(By.ID, 'form.put_short_strike_target_type')
            # Put Short Strike Delta fields
            settings['put_short_strike_minimum_delta'] = safe_find_value(By.ID, 'form.put_short_strike_delta_minimum')
            settings['put_short_strike_target_delta'] = safe_find_value(By.ID, 'form.put_short_strike_delta')
            settings['put_short_strike_maximum_delta'] = safe_find_value(By.ID, 'form.put_short_strike_delta_maximum')
            # Put Short Strike Premium fields
            settings['put_short_strike_minimum_premium'] = safe_find_value(By.ID, 'form.put_short_strike_premium_minimum')
            settings['put_short_strike_target_premium'] = safe_find_value(By.ID, 'form.put_short_strike_premium')
            settings['put_short_strike_maximum_premium'] = safe_find_value(By.ID, 'form.put_short_strike_premium_maximum')
            # Put Short Strike Percent OTM fields
            settings['put_short_strike_percent_otm_minimum'] = safe_find_value(By.ID, 'form.put_short_strike_percent_otm_minimum')
            settings['put_short_strike_target_percent_otm'] = safe_find_value(By.ID, 'form.put_short_strike_percent_otm')
            settings['put_short_strike_percent_otm_maximum'] = safe_find_value(By.ID, 'form.put_short_strike_percent_otm_maximum')

            # Put Spread Target Type (dropdown)
            settings['put_long_strike_type'] = safe_find_select(By.ID, 'form.put_spread_strike_target_type')
            # Put Spread Target Delta
            settings['put_long_strike_target_delta'] = safe_find_value(By.ID, 'form.put_spread_strike_target_delta')
            ### Restrict Spread Width By (dropdown)
            settings['restrict_put_spread_width_by'] = safe_find_select(By.ID, 'form.restrict_put_spread_width_by')
            ### Points
            settings['put_spread_minimum_width_points'] = safe_find_value(By.ID, 'form.put_spread_minimum_width')
            settings['put_spread_maximum_width_points'] = safe_find_value(By.ID, 'form.put_spread_maximum_width')
            ### Percent
            settings['put_spread_minimum_width_percent'] = safe_find_value(By.ID, 'form.put_spread_minimum_width_percent')
            settings['put_spread_maximum_width_percent'] = safe_find_value(By.ID, 'form.put_spread_maximum_width_percent')
            # Put Spread Target Points
            settings['put_spread_target_width_points'] = safe_find_value(By.ID, 'form.put_spread_width')
            # Put Spread Target Premium
            settings['put_spread_strike_target_premium'] = safe_find_value(By.ID, 'form.put_spread_strike_target_price')
            ### Uses same Restrict Spread Width By dropdown as above
            # Put Spread Target Percent
            settings['put_spread_target_width_percent'] = safe_find_value(By.ID, 'form.put_spread_strike_percent_from_main_strike')
            # Smart Spread Width (toggle)
            settings['put_spread_smart_width'] = safe_find_checkbox(By.ID, 'form.put_spread_smart_width')

            # Call Short Strike Target Type (dropdown)
            settings['call_short_strike_type'] = safe_find_select(By.ID, 'form.call_short_strike_target_type')
            # Call Short Strike Delta fields
            settings['call_short_strike_minimum_delta'] = safe_find_value(By.ID, 'form.call_short_strike_delta_minimum')
            settings['call_short_strike_target_delta'] = safe_find_value(By.ID, 'form.call_short_strike_delta')
            settings['call_short_strike_maximum_delta'] = safe_find_value(By.ID, 'form.call_short_strike_delta_maximum')
            # Call Short Strike Premium fields
            settings['call_short_strike_minimum_premium'] = safe_find_value(By.ID, 'form.call_short_strike_premium_minimum')
            settings['call_short_strike_target_premium'] = safe_find_value(By.ID, 'form.call_short_strike_premium')
            settings['call_short_strike_maximum_premium'] = safe_find_value(By.ID, 'form.call_short_strike_premium_maximum')
            # Call Short Strike Percent OTM fields
            settings['call_short_strike_percent_otm_minimum'] = safe_find_value(By.ID, 'form.call_short_strike_percent_otm_minimum')
            settings['call_short_strike_target_percent_otm'] = safe_find_value(By.ID, 'form.call_short_strike_percent_otm')
            settings['call_short_strike_percent_otm_maximum'] = safe_find_value(By.ID, 'form.call_short_strike_percent_otm_maximum')

            # Call Spread Target Type (dropdown)
            settings['call_long_strike_type'] = safe_find_select(By.ID, 'form.call_spread_strike_target_type')
            # Call Spread Target Delta
            settings['call_long_strike_target_delta'] = safe_find_value(By.ID, 'form.call_spread_strike_target_delta')
            ### Restrict Spread Width By (dropdown)
            settings['restrict_call_spread_width_by'] = safe_find_select(By.ID, 'form.restrict_call_spread_width_by')
            ### Points
            settings['call_spread_minimum_width_points'] = safe_find_value(By.ID, 'form.call_spread_minimum_width')
            settings['call_spread_maximum_width_points'] = safe_find_value(By.ID, 'form.call_spread_maximum_width')
            ### Percent
            settings['call_spread_minimum_width_percent'] = safe_find_value(By.ID, 'form.call_spread_minimum_width_percent')
            settings['call_spread_maximum_width_percent'] = safe_find_value(By.ID, 'form.call_spread_maximum_width_percent')
            # Call Spread Target Points
            settings['call_spread_target_width_points'] = safe_find_value(By.ID, 'form.call_spread_width')
            # Call Spread Target Premium
            settings['call_spread_strike_target_premium'] = safe_find_value(By.ID, 'form.call_spread_strike_target_price')
            ### Uses same Restrict Spread Width By dropdown as above
            # Call Spread Target Percent
            settings['call_spread_target_width_percent'] = safe_find_value(By.ID, 'form.call_spread_strike_percent_from_main_strike')
            # Smart Spread Width (toggle)
            settings['call_spread_smart_width'] = safe_find_checkbox(By.ID, 'form.call_spread_smart_width')

            # Entry Filters (expanded to all possible fields from examples.txt)
            settings['minimum_starting_premium'] = safe_find_value(By.ID, 'form.minimum_premium')
            settings['maximum_starting_premium'] = safe_find_value(By.ID, 'form.maximum_premium')
            settings['minimum_iv'] = safe_find_value(By.ID, 'form.minimum_iv')
            settings['maximum_iv'] = safe_find_value(By.ID, 'form.maximum_iv')
            settings['minimum_vix'] = safe_find_value(By.ID, 'form.minimum_vix')
            settings['maximum_vix'] = safe_find_value(By.ID, 'form.maximum_vix')
            settings['minimum_underlying_percent_move_from_close'] = safe_find_value(By.ID, 'form.minimum_underlying_percent_move_from_close')
            settings['maximum_underlying_percent_move_from_close'] = safe_find_value(By.ID, 'form.maximum_underlying_percent_move_from_close')
            settings['minimum_underlying_percent_move_from_open'] = safe_find_value(By.ID, 'form.minimum_underlying_percent_move_from_open')
            settings['maximum_underlying_percent_move_from_open'] = safe_find_value(By.ID, 'form.maximum_underlying_percent_move_from_open')
            settings['entry_percent_from_today_high_toggle'] = safe_find_checkbox(By.ID, 'form.entry_percent_from_today_high_toggle')
            settings['minimum_underlying_percent_move_from_today_high'] = safe_find_value(By.ID, 'form.entry_minimum_percent_move_from_today_high')
            settings['maximum_underlying_percent_move_from_today_high'] = safe_find_value(By.ID, 'form.entry_maximum_percent_move_from_today_high')
            settings['underlying_percent_from_today_high_start_time'] = safe_find_select(By.ID, 'form.entry_percent_from_today_high_start_time')
            settings['underlying_percent_from_today_high_end_time'] = safe_find_select(By.ID, 'form.entry_percent_from_today_high_end_time')
            settings['entry_percent_from_today_low_toggle'] = safe_find_checkbox(By.ID, 'form.entry_percent_from_today_low_toggle')
            settings['minimum_underlying_percent_move_from_today_low'] = safe_find_value(By.ID, 'form.entry_minimum_percent_move_from_today_low')
            settings['maximum_underlying_percent_move_from_today_low'] = safe_find_value(By.ID, 'form.entry_maximum_percent_move_from_today_low')
            settings['underlying_percent_from_today_low_start_time'] = safe_find_select(By.ID, 'form.entry_percent_from_today_low_start_time')
            settings['underlying_percent_from_today_low_end_time'] = safe_find_select(By.ID, 'form.entry_percent_from_today_low_end_time')
            settings['entry_percent_from_prior_high_toggle'] = safe_find_checkbox(By.ID, 'form.entry_percent_from_prior_high_toggle')
            settings['minimum_underlying_percent_move_from_prior_high'] = safe_find_value(By.ID, 'form.entry_minimum_percent_move_from_prior_high')
            settings['maximum_underlying_percent_move_from_prior_high'] = safe_find_value(By.ID, 'form.entry_maximum_percent_move_from_prior_high')
            settings['underlying_percent_from_prior_high_start_time'] = safe_find_select(By.ID, 'form.entry_percent_from_prior_high_start_time')
            settings['underlying_percent_from_prior_high_end_time'] = safe_find_select(By.ID, 'form.entry_percent_from_prior_high_end_time')
            settings['entry_percent_from_prior_low_toggle'] = safe_find_checkbox(By.ID, 'form.entry_percent_from_prior_low_toggle')
            settings['minimum_underlying_percent_move_from_prior_low'] = safe_find_value(By.ID, 'form.entry_minimum_percent_move_from_prior_low')
            settings['maximum_underlying_percent_move_from_prior_low'] = safe_find_value(By.ID, 'form.entry_maximum_percent_move_from_prior_low')
            settings['underlying_percent_from_prior_low_start_time'] = safe_find_select(By.ID, 'form.entry_percent_from_prior_low_start_time')
            settings['underlying_percent_from_prior_low_end_time'] = safe_find_select(By.ID, 'form.entry_percent_from_prior_low_end_time')
            settings['entry_ma_crossover_toggle'] = safe_find_checkbox(By.ID, 'form.entry_ma_crossover_toggle')
            settings['ma_crossover_one'] = safe_find_select(By.ID, 'form.entry_ma_crossover_one')
            settings['ma_crossover_percent'] = safe_find_value(By.ID, 'form.entry_ma_crossover_percent')
            settings['ma_crossover_type'] = safe_find_select(By.ID, 'form.entry_ma_crossover_type')
            settings['ma_crossover_two'] = safe_find_select(By.ID, 'form.entry_ma_crossover_two')
            settings['entry_ma_value_toggle'] = safe_find_checkbox(By.ID, 'form.entry_ma_value_toggle')
            settings['ma_value_percent'] = safe_find_value(By.ID, 'form.entry_ma_value_percent')
            settings['ma_value_type'] = safe_find_select(By.ID, 'form.entry_ma_value_type')
            settings['ma_value_ma'] = safe_find_select(By.ID, 'form.entry_ma_value_ma')
            settings['avoid_fomc'] = safe_find_checkbox(By.ID, 'form.avoid_fomc')
            settings['avoid_fomc_days_before'] = safe_find_value(By.ID, 'form.avoid_fomc_days_before')
            settings['avoid_fomc_days_after'] = safe_find_value(By.ID, 'form.avoid_fomc_days_after')
            settings['min_underlying_price'] = safe_find_value(By.ID, 'form.minimum_underlying_price')
            settings['max_underlying_price'] = safe_find_value(By.ID, 'form.maximum_underlying_price')
            settings['min_underlying_iv'] = safe_find_value(By.ID, 'form.minimum_underlying_iv')
            settings['max_underlying_iv'] = safe_find_value(By.ID, 'form.maximum_underlying_iv')
            settings['min_underlying_iv_rank'] = safe_find_value(By.ID, 'form.minimum_underlying_iv_rank')
            settings['max_underlying_iv_rank'] = safe_find_value(By.ID, 'form.maximum_underlying_iv_rank')
            settings['min_underlying_iv_percentile'] = safe_find_value(By.ID, 'form.minimum_underlying_iv_percentile')
            settings['max_underlying_iv_percentile'] = safe_find_value(By.ID, 'form.maximum_underlying_iv_percentile')
            settings['skip_earnings'] = safe_find_checkbox(By.ID, 'form.skip_earnings')
            settings['exclude_tickers'] = safe_find_value(By.ID, 'form.exclude_tickers')
            settings['only_tickers'] = safe_find_value(By.ID, 'form.only_tickers')
            settings['min_underlying_price_change'] = safe_find_value(By.ID, 'form.minimum_underlying_price_change')
            settings['max_underlying_price_change'] = safe_find_value(By.ID, 'form.maximum_underlying_price_change')
            settings['min_underlying_volume'] = safe_find_value(By.ID, 'form.minimum_underlying_volume')
            settings['min_underlying_open_interest'] = safe_find_value(By.ID, 'form.minimum_underlying_open_interest')
            settings['min_underlying_market_cap'] = safe_find_value(By.ID, 'form.minimum_underlying_market_cap')
            settings['underlying_sector'] = safe_find_select(By.ID, 'form.underlying_sector')
            settings['underlying_industry'] = safe_find_select(By.ID, 'form.underlying_industry')
            settings['only_etfs'] = safe_find_checkbox(By.ID, 'form.only_etfs')
            settings['only_stocks'] = safe_find_checkbox(By.ID, 'form.only_stocks')
            settings['only_index'] = safe_find_checkbox(By.ID, 'form.only_index')
            settings['only_liquid_options'] = safe_find_checkbox(By.ID, 'form.only_liquid_options')
            settings['only_marginable'] = safe_find_checkbox(By.ID, 'form.only_marginable')
            settings['only_shortable'] = safe_find_checkbox(By.ID, 'form.only_shortable')
            settings['only_easy_to_borrow'] = safe_find_checkbox(By.ID, 'form.only_easy_to_borrow')
            settings['only_hard_to_borrow'] = safe_find_checkbox(By.ID, 'form.only_hard_to_borrow')
            settings['custom_filter'] = safe_find_value(By.ID, 'form.custom_filter')

            # --- Miscellaneous Section ---
            # Entry Speed (dropdown)
            settings['entry_speed'] = safe_find_select(By.ID, 'form.entry_speed')
            # Move Strike Selection With Conflict (toggle)
            settings['move_strike_selection_with_conflict'] = safe_find_checkbox(By.ID, 'form.move_strike_selection_with_conflict')

            # Scrape all entryVariables repeater fields (bot_variable_id, condition, value)
            entry_variables = []
            try:
                idx = 0
                while True:
                    prefix = f'form.entryVariables.{idx}.'
                    bot_variable_id = safe_find_select(By.ID, prefix + 'bot_variable_id')
                    condition = safe_find_select(By.ID, prefix + 'condition')
                    value = safe_find_value(By.ID, prefix + 'value')
                    if bot_variable_id is None and condition is None and value is None:
                        break
                    entry_variables.append({
                        'bot_variable_id': bot_variable_id,
                        'condition': condition,
                        'value': value
                    })
                    idx += 1
            except Exception:
                pass
            settings['variables'] = entry_variables

            # Entry time window (dropdowns) -- updated to match actual HTML
            try:
                earliest_entry_el = self.webdriver.find_element(By.ID, 'form.earliest_entry_time')
                latest_entry_el = self.webdriver.find_element(By.ID, 'form.latest_entry_time')
                earliest_entry = Select(earliest_entry_el).first_selected_option.text.strip()
                latest_entry = Select(latest_entry_el).first_selected_option.text.strip()
                settings['earliest_entry_time'] = earliest_entry if earliest_entry else None
                settings['latest_entry_time'] = latest_entry if latest_entry else None
            except Exception:
                settings['earliest_entry_time'] = None
                settings['latest_entry_time'] = None

            # Entry days of week (checkboxes) -- updated to match actual HTML
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            checked_days = []
            try:
                els = self.webdriver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][wire\\:model='data.days_of_week']")
                if not els:
                    print('[DEBUG] No checkboxes found for days_of_week')
                for el in els:
                    val = el.get_attribute('value')
                    if val in days and el.is_selected():
                        checked_days.append(val)
            except Exception as e:
                print(f'[DEBUG] Exception in days_of_week scraping: {e}')
            # Always return a list, never None
            settings['days_of_week'] = checked_days



            # --- Build API-compatible output dict ---
            def yesno(val):
                if val is True:
                    return 'Yes'
                if val is False:
                    return 'No'
                return None

            # Convert days_of_week to API format
            api_days_of_week = None
            if 'days_of_week' in settings:
                if isinstance(settings['days_of_week'], list):
                    if len(settings['days_of_week']) == 5:
                        api_days_of_week = 'All'
                    elif len(settings['days_of_week']) > 0:
                        api_days_of_week = settings['days_of_week']
                        
            # Build API-compatible output dict with all available settings
            api_settings = {}
            for k, v in settings.items():
                # Convert booleans to 'Yes'/'No' for API where appropriate
                if isinstance(v, bool):
                    api_settings[k] = yesno(v)
                else:
                    api_settings[k] = v
            # Preserve days_of_week API format
            api_settings['days_of_week'] = api_days_of_week

            return api_settings


    @_require_enabled
    def update_entry_settings(self, bot_num: str, entry_settings_dict: dict) -> dict:
        """
        Update WT Bot Entry Settings for the specified bot number using a dictionary of values.
        Updates all entry fields present in the UI, including checkboxes, selects, text fields, and repeaters.
        :param bot_num: WhisperTrades bot Number
        :param entry_settings_dict: Dictionary with the same format as returned by get_entry_settings
        :return: Dictionary of changed settings
        :rtype: dict
        """
        # Get current settings and merge with new values
        settings = self.get_entry_settings(bot_num)
        initial_settings = copy.deepcopy(settings)
        settings.update(entry_settings_dict)

        if initial_settings == settings:
            if self.verbose:
                print(f'No changes required for ENTRY settings of bot: {bot_num}')
            return settings

        wt_entry_edit_url = f'https://whispertrades.com/bots/{bot_num}/entry/edit'
        self.__get_url_and_wait(wt_entry_edit_url)
        save_btn = self.webdriver.find_element(by=By.CLASS_NAME, value='bg-green-600')

        from selenium.webdriver.common.keys import Keys
        def safe_update_field(field_id, value, input_type='text'):
            try:
                el = self.webdriver.find_element(By.ID, field_id)
                if input_type == 'checkbox':
                    if bool(el.is_selected()) != bool(value):
                        el.click()
                elif input_type == 'select':
                    sel = Select(el)
                    try:
                        sel.select_by_value(str(value))
                    except Exception:
                        for option in sel.options:
                            if option.text.strip() == str(value).strip():
                                option.click()
                                break
                else:
                    # Use the known working __update_field for text fields, which now uses BACKSPACE
                    if value is None:
                        self.__update_field(el, "")
                    else:
                        self.__update_field(el, str(value))
                time.sleep(0.1)
            except Exception:
                pass

        # Map of dependent fields: {dependent_key: controller_key}
        dependent_fields = {
            'allocation_percent': 'allocation_type',
            'leverage_amount': 'allocation_type',
            'put_spread_minimum_width_percent': 'restrict_put_spread_width_by',
            'put_spread_maximum_width_percent': 'restrict_put_spread_width_by',
            'put_spread_minimum_width_points': 'restrict_put_spread_width_by',
            'put_spread_maximum_width_points': 'restrict_put_spread_width_by',
            'put_spread_smart_width': 'restrict_put_spread_width_by',
            'call_spread_minimum_width_percent': 'restrict_call_spread_width_by',
            'call_spread_maximum_width_percent': 'restrict_call_spread_width_by',
            'call_spread_minimum_width_points': 'restrict_call_spread_width_by',
            'call_spread_maximum_width_points': 'restrict_call_spread_width_by',
            'call_spread_smart_width': 'restrict_call_spread_width_by',
        }

        # Field map: key -> (element_id, type)
        field_map = {
            'frequency': ('form.frequency', 'select'),
            'maximum_entries_per_day': ('form.maximum_entries_per_day', 'select'),
            'maximum_concurrent_positions': ('form.maximum_concurrent_positions', 'select'),
            'day_of_week': ('form.day_of_week', 'select'),
            'allocation_type': ('form.allocation_type', 'select'),
            'contract_quantity': ('form.allocation_quantity', 'text'),
            'leverage_amount': ('form.allocation_leverage', 'text'),
            'percent_of_portfolio': ('form.allocation_percent', 'text'),
            'minimum_days_to_expiration': ('form.minimum_days_to_expiration', 'text'),
            'target_days_to_expiration': ('form.target_days_to_expiration', 'text'),
            'maximum_days_to_expiration': ('form.maximum_days_to_expiration', 'text'),
            'put_short_strike_type': ('form.put_short_strike_target_type', 'select'),
            'put_short_strike_minimum_delta': ('form.put_short_strike_delta_minimum', 'text'),
            'put_short_strike_target_delta': ('form.put_short_strike_delta', 'text'),
            'put_short_strike_maximum_delta': ('form.put_short_strike_delta_maximum', 'text'),
            'put_short_strike_minimum_premium': ('form.put_short_strike_premium_minimum', 'text'),
            'put_short_strike_target_premium': ('form.put_short_strike_premium', 'text'),
            'put_short_strike_maximum_premium': ('form.put_short_strike_premium_maximum', 'text'),
            'put_short_strike_percent_otm_minimum': ('form.put_short_strike_percent_otm_minimum', 'text'),
            'put_short_strike_target_percent_otm': ('form.put_short_strike_percent_otm', 'text'),
            'put_short_strike_percent_otm_maximum': ('form.put_short_strike_percent_otm_maximum', 'text'),
            'put_long_strike_type': ('form.put_spread_strike_target_type', 'select'),
            'put_long_strike_target_delta': ('form.put_spread_strike_target_delta', 'text'),
            'restrict_put_spread_width_by': ('form.restrict_put_spread_width_by', 'select'),
            'put_spread_minimum_width_points': ('form.put_spread_minimum_width', 'text'),
            'put_spread_maximum_width_points': ('form.put_spread_maximum_width', 'text'),
            'put_spread_minimum_width_percent': ('form.put_spread_minimum_width_percent', 'text'),
            'put_spread_maximum_width_percent': ('form.put_spread_maximum_width_percent', 'text'),
            'put_spread_target_width_points': ('form.put_spread_width', 'text'),
            'put_spread_strike_target_premium': ('form.put_spread_strike_target_price', 'text'),
            'put_spread_target_width_percent': ('form.put_spread_strike_percent_from_main_strike', 'text'),
            'put_spread_smart_width': ('form.put_spread_smart_width', 'checkbox'),
            'call_short_strike_type': ('form.call_short_strike_target_type', 'select'),
            'call_short_strike_minimum_delta': ('form.call_short_strike_delta_minimum', 'text'),
            'call_short_strike_target_delta': ('form.call_short_strike_delta', 'text'),
            'call_short_strike_maximum_delta': ('form.call_short_strike_delta_maximum', 'text'),
            'call_short_strike_minimum_premium': ('form.call_short_strike_premium_minimum', 'text'),
            'call_short_strike_target_premium': ('form.call_short_strike_premium', 'text'),
            'call_short_strike_maximum_premium': ('form.call_short_strike_premium_maximum', 'text'),
            'call_short_strike_percent_otm_minimum': ('form.call_short_strike_percent_otm_minimum', 'text'),
            'call_short_strike_target_percent_otm': ('form.call_short_strike_percent_otm', 'text'),
            'call_short_strike_percent_otm_maximum': ('form.call_short_strike_percent_otm_maximum', 'text'),
            'call_long_strike_type': ('form.call_spread_strike_target_type', 'select'),
            'call_long_strike_target_delta': ('form.call_spread_strike_target_delta', 'text'),
            'restrict_call_spread_width_by': ('form.restrict_call_spread_width_by', 'select'),
            'call_spread_minimum_width_points': ('form.call_spread_minimum_width', 'text'),
            'call_spread_maximum_width_points': ('form.call_spread_maximum_width', 'text'),
            'call_spread_minimum_width_percent': ('form.call_spread_minimum_width_percent', 'text'),
            'call_spread_maximum_width_percent': ('form.call_spread_maximum_width_percent', 'text'),
            'call_spread_target_width_points': ('form.call_spread_width', 'text'),
            'call_spread_strike_target_premium': ('form.call_spread_strike_target_price', 'text'),
            'call_spread_target_width_percent': ('form.call_spread_strike_percent_from_main_strike', 'text'),
            'call_spread_smart_width': ('form.call_spread_smart_width', 'checkbox'),
            # Entry Filters and Miscellaneous
            'minimum_starting_premium': ('form.minimum_premium', 'text'),
            'maximum_starting_premium': ('form.maximum_premium', 'text'),
            'minimum_iv': ('form.minimum_iv', 'text'),
            'maximum_iv': ('form.maximum_iv', 'text'),
            'minimum_vix': ('form.minimum_vix', 'text'),
            'maximum_vix': ('form.maximum_vix', 'text'),
            'minimum_underlying_percent_move_from_close': ('form.minimum_underlying_percent_move_from_close', 'text'),
            'maximum_underlying_percent_move_from_close': ('form.maximum_underlying_percent_move_from_close', 'text'),
            'minimum_underlying_percent_move_from_open': ('form.minimum_underlying_percent_move_from_open', 'text'),
            'maximum_underlying_percent_move_from_open': ('form.maximum_underlying_percent_move_from_open', 'text'),
            'entry_percent_from_today_high_toggle': ('form.entry_percent_from_today_high_toggle', 'checkbox'),
            'minimum_underlying_percent_move_from_today_high': ('form.entry_minimum_percent_move_from_today_high', 'text'),
            'maximum_underlying_percent_move_from_today_high': ('form.entry_maximum_percent_move_from_today_high', 'text'),
            'underlying_percent_from_today_high_start_time': ('form.entry_percent_from_today_high_start_time', 'select'),
            'underlying_percent_from_today_high_end_time': ('form.entry_percent_from_today_high_end_time', 'select'),
            'entry_percent_from_today_low_toggle': ('form.entry_percent_from_today_low_toggle', 'checkbox'),
            'minimum_underlying_percent_move_from_today_low': ('form.entry_minimum_percent_move_from_today_low', 'text'),
            'maximum_underlying_percent_move_from_today_low': ('form.entry_maximum_percent_move_from_today_low', 'text'),
            'underlying_percent_from_today_low_start_time': ('form.entry_percent_from_today_low_start_time', 'select'),
            'underlying_percent_from_today_low_end_time': ('form.entry_percent_from_today_low_end_time', 'select'),
            'entry_percent_from_prior_high_toggle': ('form.entry_percent_from_prior_high_toggle', 'checkbox'),
            'minimum_underlying_percent_move_from_prior_high': ('form.entry_minimum_percent_move_from_prior_high', 'text'),
            'maximum_underlying_percent_move_from_prior_high': ('form.entry_maximum_percent_move_from_prior_high', 'text'),
            'underlying_percent_from_prior_high_start_time': ('form.entry_percent_from_prior_high_start_time', 'select'),
            'underlying_percent_from_prior_high_end_time': ('form.entry_percent_from_prior_high_end_time', 'select'),
            'entry_percent_from_prior_low_toggle': ('form.entry_percent_from_prior_low_toggle', 'checkbox'),
            'minimum_underlying_percent_move_from_prior_low': ('form.entry_minimum_percent_move_from_prior_low', 'text'),
            'maximum_underlying_percent_move_from_prior_low': ('form.entry_maximum_percent_move_from_prior_low', 'text'),
            'underlying_percent_from_prior_low_start_time': ('form.entry_percent_from_prior_low_start_time', 'select'),
            'underlying_percent_from_prior_low_end_time': ('form.entry_percent_from_prior_low_end_time', 'select'),
            'entry_ma_crossover_toggle': ('form.entry_ma_crossover_toggle', 'checkbox'),
            'ma_crossover_one': ('form.entry_ma_crossover_one', 'select'),
            'ma_crossover_percent': ('form.entry_ma_crossover_percent', 'text'),
            'ma_crossover_type': ('form.entry_ma_crossover_type', 'select'),
            'ma_crossover_two': ('form.entry_ma_crossover_two', 'select'),
            'entry_ma_value_toggle': ('form.entry_ma_value_toggle', 'checkbox'),
            'ma_value_percent': ('form.entry_ma_value_percent', 'text'),
            'ma_value_type': ('form.entry_ma_value_type', 'select'),
            'ma_value_ma': ('form.entry_ma_value_ma', 'select'),
            'avoid_fomc': ('form.avoid_fomc', 'checkbox'),
            'avoid_fomc_days_before': ('form.avoid_fomc_days_before', 'text'),
            'avoid_fomc_days_after': ('form.avoid_fomc_days_after', 'text'),
            'min_underlying_price': ('form.minimum_underlying_price', 'text'),
            'max_underlying_price': ('form.maximum_underlying_price', 'text'),
            'min_underlying_iv': ('form.minimum_underlying_iv', 'text'),
            'max_underlying_iv': ('form.maximum_underlying_iv', 'text'),
            'min_underlying_iv_rank': ('form.minimum_underlying_iv_rank', 'text'),
            'max_underlying_iv_rank': ('form.maximum_underlying_iv_rank', 'text'),
            'min_underlying_iv_percentile': ('form.minimum_underlying_iv_percentile', 'text'),
            'max_underlying_iv_percentile': ('form.maximum_underlying_iv_percentile', 'text'),
            'skip_earnings': ('form.skip_earnings', 'checkbox'),
            'exclude_tickers': ('form.exclude_tickers', 'text'),
            'only_tickers': ('form.only_tickers', 'text'),
            'min_underlying_price_change': ('form.minimum_underlying_price_change', 'text'),
            'max_underlying_price_change': ('form.maximum_underlying_price_change', 'text'),
            'min_underlying_volume': ('form.minimum_underlying_volume', 'text'),
            'min_underlying_open_interest': ('form.minimum_underlying_open_interest', 'text'),
            'min_underlying_market_cap': ('form.minimum_underlying_market_cap', 'text'),
            'underlying_sector': ('form.underlying_sector', 'select'),
            'underlying_industry': ('form.underlying_industry', 'select'),
            'only_etfs': ('form.only_etfs', 'checkbox'),
            'only_stocks': ('form.only_stocks', 'checkbox'),
            'only_index': ('form.only_index', 'checkbox'),
            'only_liquid_options': ('form.only_liquid_options', 'checkbox'),
            'only_marginable': ('form.only_marginable', 'checkbox'),
            'only_shortable': ('form.only_shortable', 'checkbox'),
            'only_easy_to_borrow': ('form.only_easy_to_borrow', 'checkbox'),
            'only_hard_to_borrow': ('form.only_hard_to_borrow', 'checkbox'),
            'custom_filter': ('form.custom_filter', 'text'),
            # Miscellaneous
            'entry_speed': ('form.entry_speed', 'select'),
            'move_strike_selection_with_conflict': ('form.move_strike_selection_with_conflict', 'checkbox'),
        }

        # First, set all controller fields that are present in the input
        controllers_set = set()
        for dep, ctrl in dependent_fields.items():
            if ctrl in entry_settings_dict and ctrl not in controllers_set:
                val = entry_settings_dict[ctrl]
                if ctrl in field_map and val is not None:
                    safe_update_field(field_map[ctrl][0], val, field_map[ctrl][1])
                    controllers_set.add(ctrl)
                    time.sleep(0.2)  # allow UI to update

        # Now update all other fields present in the input dict
        # Map toggles to their dependent fields
        toggle_dependents = {
            'entry_percent_from_today_high_toggle': [
                'minimum_underlying_percent_move_from_today_high',
                'maximum_underlying_percent_move_from_today_high',
                'underlying_percent_from_today_high_start_time',
                'underlying_percent_from_today_high_end_time',
            ],
            'entry_percent_from_today_low_toggle': [
                'minimum_underlying_percent_move_from_today_low',
                'maximum_underlying_percent_move_from_today_low',
                'underlying_percent_from_today_low_start_time',
                'underlying_percent_from_today_low_end_time',
            ],
            'entry_percent_from_prior_high_toggle': [
                'minimum_underlying_percent_move_from_prior_high',
                'maximum_underlying_percent_move_from_prior_high',
                'underlying_percent_from_prior_high_start_time',
                'underlying_percent_from_prior_high_end_time',
            ],
            'entry_percent_from_prior_low_toggle': [
                'minimum_underlying_percent_move_from_prior_low',
                'maximum_underlying_percent_move_from_prior_low',
                'underlying_percent_from_prior_low_start_time',
                'underlying_percent_from_prior_low_end_time',
            ],
            'entry_ma_crossover_toggle': [
                'ma_crossover_one', 'ma_crossover_percent', 'ma_crossover_type', 'ma_crossover_two'
            ],
            'entry_ma_value_toggle': [
                'ma_value_percent', 'ma_value_type', 'ma_value_ma'
            ],
        }

        # First, check toggles: if enabled but all dependents are blank/missing, turn off toggle
        for toggle, dependents in toggle_dependents.items():
            if toggle in entry_settings_dict and entry_settings_dict[toggle]:
                all_blank = True
                for dep in dependents:
                    val = entry_settings_dict.get(dep)
                    if val not in (None, ''):
                        all_blank = False
                        break
                if all_blank:
                    # Turn off toggle in UI and dict
                    safe_update_field(field_map[toggle][0], False, field_map[toggle][1])
                    entry_settings_dict[toggle] = False

        # Now update all toggles and immediately set their dependents if toggle is True
        for toggle, dependents in toggle_dependents.items():
            if toggle in entry_settings_dict and entry_settings_dict[toggle]:
                # Set the toggle
                safe_update_field(field_map[toggle][0], True, field_map[toggle][1])
                # For each dependent, set from input or use a safe default
                for dep in dependents:
                    val = entry_settings_dict.get(dep)
                    if val is None or val == '':
                        # Use a safe default: '' for text, first option for select
                        field_type = field_map[dep][1]
                        if field_type == 'select':
                            try:
                                el = self.webdriver.find_element(By.ID, field_map[dep][0])
                                sel = Select(el)
                                if sel.options:
                                    sel.options[0].click()
                            except Exception:
                                pass
                        else:
                            safe_update_field(field_map[dep][0], '', field_type)
                    else:
                        safe_update_field(field_map[dep][0], val, field_map[dep][1])

        # Now update all other fields present in the input dict (skip those handled above)
        toggled_fields = set()
        for dependents in toggle_dependents.values():
            toggled_fields.update(dependents)
        toggled_fields.update(toggle_dependents.keys())
        for k, v in entry_settings_dict.items():
            if k in field_map and k not in toggled_fields:
                # If this is a dependent field, ensure its controller is set first
                if k in dependent_fields:
                    ctrl = dependent_fields[k]
                    if ctrl in entry_settings_dict and ctrl not in controllers_set:
                        safe_update_field(field_map[ctrl][0], entry_settings_dict[ctrl], field_map[ctrl][1])
                        controllers_set.add(ctrl)
                        time.sleep(0.2)
                safe_update_field(field_map[k][0], v, field_map[k][1])

        # Handle days_of_week checkboxes if present
        if 'days_of_week' in entry_settings_dict and entry_settings_dict['days_of_week'] is not None:
            try:
                days = entry_settings_dict['days_of_week']
                els = self.webdriver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][wire\\:model='data.days_of_week']")
                for el in els:
                    val = el.get_attribute('value')
                    if val in days and not el.is_selected():
                        el.click()
                    elif val not in days and el.is_selected():
                        el.click()
            except Exception as e:
                if self.verbose:
                    print(f"[DEBUG] Exception updating days_of_week: {e}")

        # Handle earliest/latest entry time dropdowns if present
        for time_field, dom_id in [('earliest_entry_time', 'form.earliest_entry_time'), ('latest_entry_time', 'form.latest_entry_time')]:
            if time_field in entry_settings_dict and entry_settings_dict[time_field] is not None:
                try:
                    el = self.webdriver.find_element(By.ID, dom_id)
                    sel = Select(el)
                    for option in sel.options:
                        if option.text.strip() == str(entry_settings_dict[time_field]).strip():
                            option.click()
                            break
                except Exception as e:
                    if self.verbose:
                        print(f"[DEBUG] Exception updating {time_field}: {e}")

        # Handle entry variables (repeater)
        if 'variables' in entry_settings_dict and isinstance(entry_settings_dict['variables'], list):
            for idx, var in enumerate(entry_settings_dict['variables']):
                prefix = f'form.entryVariables.{idx}.'
                if 'bot_variable_id' in var and var['bot_variable_id'] is not None:
                    try:
                        el = self.webdriver.find_element(By.ID, prefix + 'bot_variable_id')
                        sel = Select(el)
                        sel.select_by_value(str(var['bot_variable_id']))
                    except Exception:
                        pass
                if 'condition' in var and var['condition'] is not None:
                    try:
                        el = self.webdriver.find_element(By.ID, prefix + 'condition')
                        sel = Select(el)
                        sel.select_by_value(str(var['condition']))
                    except Exception:
                        pass
                if 'value' in var:
                    try:
                        el = self.webdriver.find_element(By.ID, prefix + 'value')
                        if var['value'] is None:
                            self.__update_field(el, "")
                        else:
                            self.__update_field(el, str(var['value']))
                    except Exception:
                        pass

        save_btn.click()
        time.sleep(1)
        new_settings = self.get_entry_settings(bot_num)
        if self.verbose:
            print(f'Updated ENTRY settings for bot: {bot_num}')
        return new_settings

    @_require_enabled
    def get_exit_settings(self, bot_num: str) -> dict:
        """
        Get current WT Bot Exit Settings of specified bot number
        Scrapes all exit fields from the WhisperTrades bot exit form, including all standing profit targets, monitored stops, trailing stops, sensitivities, toggles, market conditions, and advanced variables.
        Handles missing/optional fields robustly.
        :param bot_num: WhisperTrades bot Number
        :type bot_num: string
        :return: Dictionary of settings
        :rtype: dict
        """
        wt_exit_edit_url = f'https://whispertrades.com/bots/{bot_num}/exit/edit'
        self.__get_url_and_wait(wt_exit_edit_url)

        def safe_find_value(by, value, attr='value', default=None):
            try:
                el = self.webdriver.find_element(by=by, value=value)
                return el.get_attribute(attr) if el.get_attribute(attr) != '' else default
            except Exception:
                return default

        def safe_find_checkbox(by, value, default=False):
            try:
                el = self.webdriver.find_element(by=by, value=value)
                return el.is_selected()
            except Exception:
                return default

        def safe_find_select(by, value, default=None):
            try:
                el = self.webdriver.find_element(by=by, value=value)
                return el.get_attribute('value')
            except Exception:
                return default

        settings = {}
        # --- Profit (Standing) Section ---
        settings['profit_target_percent'] = safe_find_value(By.ID, 'form.profit_target_percent')
        settings['profit_premium_value'] = safe_find_value(By.ID, 'form.premium_value_profit')

        # --- Monitored Stops Section ---
        settings['stop_loss_percent'] = safe_find_value(By.ID, 'form.stop_loss_percent')
        settings['loss_premium_value'] = safe_find_value(By.ID, 'form.premium_value_loss')
        settings['itm_percent_stop'] = safe_find_value(By.ID, 'form.itm_percent')
        settings['otm_percent_stop'] = safe_find_value(By.ID, 'form.otm_percent')
        settings['delta_stop'] = safe_find_value(By.ID, 'form.delta_value')
        settings['monitored_stop_sensitivity'] = safe_find_select(By.ID, 'form.monitored_stop_sensitivity')

        # --- Exit Variables (Advanced) repeater ---
        exit_vars = []
        idx = 0
        while True:
            var_prefix = f'form.exitVariables.{idx}.'
            bot_variable_id = safe_find_select(By.ID, var_prefix + 'bot_variable_id')
            condition = safe_find_select(By.ID, var_prefix + 'condition')
            value = safe_find_value(By.ID, var_prefix + 'value')
            if bot_variable_id is None and condition is None and value is None:
                break
            exit_vars.append({
                'bot_variable_id': bot_variable_id,
                'condition': condition,
                'value': value
            })
            idx += 1
        settings['variables'] = exit_vars

        # --- Trailing Stops Section ---
        settings['trail_profit_percent_trigger'] = safe_find_value(By.ID, 'form.trail_profit_target_percent_trigger')
        settings['trail_profit_percent_amount'] = safe_find_value(By.ID, 'form.trail_profit_target_percent_amount')
        settings['trail_profit_premium_trigger'] = safe_find_value(By.ID, 'form.trail_premium_value_profit_trigger')
        settings['trail_profit_premium_amount'] = safe_find_value(By.ID, 'form.trail_premium_value_profit_amount')
        settings['trailing_stop_sensitivity'] = safe_find_select(By.ID, 'form.trailing_stop_sensitivity')

        # --- Market Conditions Section ---
        settings['ma_crossover_toggle'] = safe_find_checkbox(By.ID, 'form.exit_ma_crossover_toggle')
        settings['ma_crossover_one'] = safe_find_select(By.ID, 'form.exit_ma_crossover_one')
        settings['ma_crossover_percent'] = safe_find_value(By.ID, 'form.exit_ma_crossover_percent')
        settings['ma_crossover_type'] = safe_find_select(By.ID, 'form.exit_ma_crossover_type')
        settings['ma_crossover_two'] = safe_find_select(By.ID, 'form.exit_ma_crossover_two')
        settings['exit_ma_value_toggle'] = safe_find_checkbox(By.ID, 'form.exit_ma_value_toggle')
        settings['ma_value_percent'] = safe_find_value(By.ID, 'form.exit_ma_value_percent')
        settings['ma_value_type'] = safe_find_select(By.ID, 'form.exit_ma_value_type')
        settings['ma_value_ma'] = safe_find_select(By.ID, 'form.exit_ma_value_ma')

        # --- Miscellaneous Section ---
        settings['exit_speed'] = safe_find_select(By.ID, 'form.exit_speed')
        settings['close_short_strike_only'] = safe_find_checkbox(By.ID, 'form.close_short_strike_only')

        return settings

    @_require_enabled
    def update_exit_settings(self, bot_num: str, exit_settings_dict: dict) -> dict:
        """
        Update WT Bot Exit Settings for the specified bot number using a dictionary of values.
        Updates all exit fields present in the UI, including checkboxes, selects, text fields, and repeaters.
        :param bot_num: WhisperTrades bot Number
        :param exit_settings_dict: Dictionary with the same format as returned by get_exit_settings
        :return: Dictionary of changed settings
        :rtype: dict
        """

        settings_keys = [
            # --- Profit (Standing) Section ---
            'profit_target_percent',
            'profit_premium_value',
            # --- Monitored Stops Section ---
            'stop_loss_percent',
            'loss_premium_value',
            'itm_percent_stop',
            'otm_percent_stop',
            'delta_stop',
            'monitored_stop_sensitivity',
            # --- Trailing Stops Section ---
            'trail_profit_percent_trigger',
            'trail_profit_percent_amount',
            'trail_profit_premium_trigger',
            'trail_profit_premium_amount',
            'trailing_stop_sensitivity',
            # --- Market Conditions Section ---
            'ma_crossover_toggle',
            'ma_crossover_one',
            'ma_crossover_percent',
            'ma_crossover_type',
            'ma_crossover_two',
            'exit_ma_value_toggle',
            'ma_value_percent',
            'ma_value_type',
            'ma_value_ma',
            # --- Miscellaneous Section ---
            'exit_speed',
            'close_short_strike_only',
        ]
        field_map = {
            # --- Profit (Standing) Section ---
            'profit_target_percent': ('form.profit_target_percent', 'text'),
            'profit_premium_value': ('form.premium_value_profit', 'text'),
            # --- Monitored Stops Section ---
            'stop_loss_percent': ('form.stop_loss_percent', 'text'),
            'loss_premium_value': ('form.premium_value_loss', 'text'),
            'itm_percent_stop': ('form.itm_percent', 'text'),
            'otm_percent_stop': ('form.otm_percent', 'text'),
            'delta_stop': ('form.delta_value', 'text'),
            'monitored_stop_sensitivity': ('form.monitored_stop_sensitivity', 'select'),
            # --- Trailing Stops Section ---
            'trail_profit_percent_trigger': ('form.trail_profit_target_percent_trigger', 'text'),
            'trail_profit_percent_amount': ('form.trail_profit_target_percent_amount', 'text'),
            'trail_profit_premium_trigger': ('form.trail_premium_value_profit_trigger', 'text'),
            'trail_profit_premium_amount': ('form.trail_premium_value_profit_amount', 'text'),
            'trailing_stop_sensitivity': ('form.trailing_stop_sensitivity', 'select'),
            # --- Market Conditions Section ---
            'ma_crossover_toggle': ('form.exit_ma_crossover_toggle', 'checkbox'),
            'ma_crossover_one': ('form.exit_ma_crossover_one', 'select'),
            'ma_crossover_percent': ('form.exit_ma_crossover_percent', 'text'),
            'ma_crossover_type': ('form.exit_ma_crossover_type', 'select'),
            'ma_crossover_two': ('form.exit_ma_crossover_two', 'select'),
            'exit_ma_value_toggle': ('form.exit_ma_value_toggle', 'checkbox'),
            'ma_value_percent': ('form.exit_ma_value_percent', 'text'),
            'ma_value_type': ('form.exit_ma_value_type', 'select'),
            'ma_value_ma': ('form.exit_ma_value_ma', 'select'),
            # --- Miscellaneous Section ---
            'exit_speed': ('form.exit_speed', 'select'),
            'close_short_strike_only': ('form.close_short_strike_only', 'checkbox'),
        }

        wt_exit_edit_url = f'https://whispertrades.com/bots/{bot_num}/exit/edit'
        self.__get_url_and_wait(wt_exit_edit_url)
        save_btn = self.webdriver.find_element(by=By.CLASS_NAME, value='bg-green-600')

        def safe_update_field(field_id, value, input_type='text'):
            try:
                el = WebDriverWait(self.webdriver, 2).until(EC.presence_of_element_located((By.ID, field_id)))
                if input_type == 'checkbox':
                    if bool(el.is_selected()) != bool(value):
                        el.click()
                elif input_type == 'select':
                    sel = Select(el)
                    try:
                        sel.select_by_value(str(value))
                    except Exception:
                        for option in sel.options:
                            if option.text.strip() == str(value).strip():
                                option.click()
                                break
                else:
                    # Use the known working __update_field for text fields, which now uses BACKSPACE
                    if value is None:
                        self.__update_field(el, "")
                    else:
                        self.__update_field(el, str(value))
                time.sleep(0.1)
            except Exception:
                pass


        # Update all fields in order, skip if value is None and field does not exist
        for k in settings_keys:
            v = exit_settings_dict.get(k, None)
            if v is None:
                # Only skip if field does not exist
                try:
                    self.webdriver.find_element(By.ID, field_map[k][0])
                except Exception:
                    continue
            safe_update_field(field_map[k][0], v, field_map[k][1])

        # Handle variables (repeater)
        if 'variables' in exit_settings_dict and isinstance(exit_settings_dict['variables'], list):
            for idx, var in enumerate(exit_settings_dict['variables']):
                prefix = f'form.exitVariables.{idx}.'
                if isinstance(var, dict):
                    if 'bot_variable_id' in var and var['bot_variable_id'] is not None:
                        try:
                            el = WebDriverWait(self.webdriver, 2).until(EC.presence_of_element_located((By.ID, prefix + 'bot_variable_id')))
                            sel = Select(el)
                            sel.select_by_value(str(var['bot_variable_id']))
                        except Exception as e:
                            if self.verbose:
                                print(f"[DEBUG] Exception updating exit variable bot_variable_id: {e}")
                    if 'condition' in var and var['condition'] is not None:
                        try:
                            el = WebDriverWait(self.webdriver, 2).until(EC.presence_of_element_located((By.ID, prefix + 'condition')))
                            sel = Select(el)
                            sel.select_by_value(str(var['condition']))
                        except Exception as e:
                            if self.verbose:
                                print(f"[DEBUG] Exception updating exit variable condition: {e}")
                    if 'value' in var and var['value'] is not None:
                        try:
                            el = WebDriverWait(self.webdriver, 2).until(EC.presence_of_element_located((By.ID, prefix + 'value')))
                            el.clear()
                            el.send_keys(str(var['value']))
                        except Exception as e:
                            if self.verbose:
                                print(f"[DEBUG] Exception updating exit variable value: {e}")

        save_btn.click()
        time.sleep(1)
        new_settings = self.get_exit_settings(bot_num)
        if self.verbose:
            print(f'Updated EXIT settings for bot: {bot_num}')
        if exit_settings_dict == new_settings:
            warnings.warn(f'Exit settings are unchanged for bot: {bot_num}')
        return new_settings

    @_require_enabled
    def enable_by_bot_num(self, bot_num: str) -> bool:
        """Enable bot by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """
        url = f"https://whispertrades.com/bots/{bot_num}/enable"
        if self.verbose:
            print(f'Enabling bot: {bot_num}')
        return self.__get_url_and_wait(url)

    @_require_enabled
    def force_disable_by_bot_num(self, bot_num: str) -> bool:
        """Disable bot by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """

        url = f"https://whispertrades.com/bots/{bot_num}/force_disable?redirectUrl=https%253A%252F%252Fwhispertrades.com%252Fbots"
        if self.verbose:
            print(f'Disabling bot: {bot_num}')
        return self.__get_url_and_wait(url)

    @_require_enabled
    def disable_on_close_by_bot_num(self, bot_num: str) -> bool:
        """Soft disable bot by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """
        url = f"https://whispertrades.com/bots/{bot_num}/soft_disable?redirectUrl=https%253A%252F%252Fwhispertrades.com%252Fbots"
        if self.verbose:
            print(f'Disabling on close bot: {bot_num}')
        return self.__get_url_and_wait(url)

    @_require_enabled
    def enabled_to_soft_disabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: 'Enabled' to 'Disabled on Close'
        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.disable_on_close_by_bot_num(b):
                warnings.warn(f'UNABLE TO "DISABLE ON CLOSE" BOT_NUM {b}')
        return

    @_require_enabled
    def enabled_to_forced_disabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: 'Enabled' to 'Disabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.force_disable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "DISABLE" BOT_NUM {b}')
        return

    @_require_enabled
    def disabled_to_enabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: 'Disabled' to 'Enabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.enable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "ENABLE" BOT_NUM {b}')
        return

    @_require_enabled
    def force_enabled_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: to 'Enabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.enable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "ENABLE" BOT_NUM {b}')
        return

    @_require_enabled
    def force_disable_by_list(self, bot_num_lst: list[str]) -> None:
        """
        Bot status change: Any state to 'Disabled'

        :param bot_num_lst: List of WhisperTrades bot Numbers
        :type url: list
        """
        for b in bot_num_lst:
            if not self.force_disable_by_bot_num(b):
                warnings.warn(f'UNABLE TO "DISABLE" BOT_NUM {b}')
        return
    
    @_require_enabled
    def enter_new_position_by_bot_num(self, bot_num: str) -> bool:
        """Enter new position by bot num

        :param bot_num: WhisperTrades bot Number
        :return: Bool value of successful url load
        :rtype: bool
        """
        url = f"https://whispertrades.com/bots/{bot_num}/enter_position"
        if self.verbose:
            print(f'Entering new position on bot: {bot_num}')
        return self.__get_url_and_wait(url)

