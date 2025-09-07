"""Token generation functionality for Zerodha API authentication."""

import os
import sys
import logging
import json
from typing import Dict, Union, List, Any, Optional

import pyotp
from requests import Session, Response
from dotenv import load_dotenv

from ..utils.exceptions import AuthenticationError

load_dotenv()
logger = logging.getLogger(__name__)


class ZerodhaTokenGenerator:
    """Handles generation of Zerodha authentication tokens."""
    
    def __init__(self, config):
        """Initialize the token generator with configuration."""
        from ..utils.config import Config
        
        self.config = config or Config()
        
        # Validate required configuration
        if not self.config.validate_config():
            missing_vars = self.config.get_missing_config()
            logger.error(f"Missing required configuration: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required configuration: {', '.join(missing_vars)}")

    def get_totp(self, key: str = "") -> str:
        """
        Generates a Time-based One-Time Password (TOTP) value using the provided secret key.

        Args:
            key (str, optional): The TOTP secret key. If None, uses ZERODHA_TOTP_SECRET from env.

        Returns:
            str: The current TOTP value.

        Raises:
            AuthenticationError: If there is any error generating the TOTP value.
        """
        logger.debug("Starting TOTP generation")
        
        try:
            totp_secret = key or self.config.ZERODHA_TOTP_SECRET
            logger.debug("Retrieved TOTP secret")
            
            if totp_secret is None:
                raise AuthenticationError("TOTP secret not available")
                
            totp = pyotp.TOTP(totp_secret, interval=30)
            logger.debug("TOTP object created successfully")
            
            current_otp = totp.now()
            logger.info(f"Generated TOTP value: {current_otp}")
            
            return current_otp
            
        except Exception as e:
            logger.error(f"Failed to generate TOTP: {str(e)}")
            raise AuthenticationError(f"TOTP generation failed: {str(e)}")

    def generate_auth_token(self) -> str:
        """
        Generates an encrypted authentication token for accessing the Zerodha API.
        
        This function performs the following steps:
        1. Generates a TOTP (Time-based One-Time Password) value
        2. Starts an initial session with the Zerodha base URL
        3. Sends a login request with credentials
        4. Sends a 2FA (Two-Factor Authentication) request with the TOTP value
        5. Retrieves the encrypted authentication token (enctoken) from response cookies
        
        Returns:
            str: The encrypted authentication token (enctoken) for accessing the Zerodha API.
        
        Raises:
            AuthenticationError: If authentication fails at any step
        """
        logger.info("Starting authentication token generation process")
        
        try:
            # Get credentials from validated environment variables
            # Get credentials from configuration
            userid = self.config.ZERODHA_USER_ID
            password = self.config.ZERODHA_PASSWORD
            user_type = self.config.ZERODHA_TYPE
            totp_secret = self.config.ZERODHA_TOTP_SECRET
            base_url = self.config.ZERODHA_BASE_URL
            login_url = self.config.ZERODHA_LOGIN_URL
            two_factor_url = self.config.ZERODHA_2FA_URL

            logger.debug("Environment variables validated successfully")

            # Generate TOTP
            totp_value = self.get_totp(totp_secret)
            logger.debug("Generated TOTP successfully")
            
            # Start session
            session = Session()
            start_session_response = session.get(base_url)
            start_session_response.raise_for_status()
            logger.debug("Initial session started successfully")

            # Prepare headers
            generic_headers: Dict[str, str] = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            }
            
            # Login request
            login_payload = {
                "user_id": userid,
                "password": password,
                "type": user_type
            }
            logger.debug("Prepared login payload")

            login_response = session.post(login_url, data=login_payload, headers=generic_headers)
            login_response.raise_for_status()
            logger.info("Login request successful")
            
            logger.debug(f"Login response Text: {login_response.text}")
            logger.debug(f"Login response Headers: {login_response.headers}")
            logger.debug(f"Login response Content: {login_response.content}")
            logger.debug(f"Login response Status Code: {login_response.status_code}")
            
            # Parse login response
            login_data = json.loads(login_response.content)

            if not login_data.get('data') or not login_data['data'].get('request_id'):
                error_msg = login_data.get('message', 'Unknown error')
                logger.error(f"Login failed: {error_msg}")
                raise AuthenticationError(f"Login failed: {error_msg}")

            request_id = login_data['data']['request_id']
            logger.debug(f"Retrieved request ID: {request_id}")

            # 2FA request
            two_factor_payload = {    
                "user_id": userid, 
                "request_id": request_id, 
                "twofa_value": totp_value,
                "twofatype": "totp"
            }
            logger.debug("Prepared 2FA payload")

            two_factor_response = session.post(two_factor_url, data=two_factor_payload, headers=generic_headers)
            two_factor_response.raise_for_status()
            logger.info("2FA authentication successful")
            
            # Extract enctoken from cookies
            if 'enctoken' not in session.cookies:
                logger.error("No enctoken received in response cookies")
                raise AuthenticationError("Authentication failed: No enctoken received")
                
            logger.info("Successfully retrieved authentication token")
            return session.cookies['enctoken']
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            raise AuthenticationError(f"JSON parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError(f"Token generation failed: {str(e)}")


# Backward compatibility function
def getEncAuthToken() -> str:
    """
    Backward compatibility function for existing code.
    
    Returns:
        str: Authentication token
    """
    from ..utils.config import Config
    generator = ZerodhaTokenGenerator(config=Config())
    return generator.generate_auth_token()

def get_TOTP(key: str = 'ZERODHA_TOTP_SECRET') -> str:
    """
    Backward compatibility function for TOTP generation.
    
    Args:
        key: Environment variable name or TOTP secret
        
    Returns:
        str: TOTP value
    """
    from ..utils.config import Config
    generator = ZerodhaTokenGenerator(config=Config())
    # If key looks like an env var name, get it from environment
    if key.isupper() and '_' in key:
        secret = os.getenv(key, "")
    else:
        secret = key
    return generator.get_totp(secret)
