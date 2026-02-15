"""Core API client for DuckDuckGo AI"""

import json
import urllib.request
import urllib.error
import http.cookiejar
import uuid
import gzip
import zlib
from typing import Optional, List, Dict, Any, Generator, Tuple

# Optional Brotli support
try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False


class DuckAIClient:
    """HTTP Client for interacting with DuckDuckGo AI API"""

    BASE_URL = "https://duckduckgo.com"

    def __init__(self):
        # Initialize cookie jar to persist cookies across requests
        self.cookie_jar = http.cookiejar.CookieJar()
        self.cookie_processor = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib.request.build_opener(self.cookie_processor)

        # State
        self.vqd: Optional[str] = None
        self.vqd_hash: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.messages: List[Dict[str, str]] = []

    def _get_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get request headers mimicking Chrome browser"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "text/event-stream",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://duckduckgo.com/",
            "Origin": "https://duckduckgo.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        if extra:
            headers.update(extra)

        return headers

    def _decompress_response(self, response) -> bytes:
        """Decompress gzip/deflate/brotli response if needed"""
        encoding = response.headers.get("Content-Encoding", "").lower()
        data = response.read()

        if not data:
            return b""

        # Try Brotli first if available
        if encoding == "br" and HAS_BROTLI:
            try:
                return brotli.decompress(data)
            except:
                pass

        # If data starts with gzip magic numbers
        if data[:2] == b"\x1f\x8b":
            try:
                return gzip.decompress(data)
            except:
                pass

        if encoding == "gzip":
            try:
                return gzip.decompress(data)
            except:
                pass
        elif encoding == "deflate":
            try:
                return zlib.decompress(data, -zlib.MAX_WBITS)
            except:
                try:
                    return zlib.decompress(data)
                except:
                    pass

        return data

    def _request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        return_headers: bool = False,
    ) -> Tuple[bytes, Optional[Dict[str, str]]]:
        """Make HTTP request with cookie support"""
        url = f"{self.BASE_URL}{path}"

        # Build request
        req = urllib.request.Request(url, method=method)

        # Add headers
        default_headers = self._get_headers()
        if headers:
            default_headers.update(headers)

        for key, value in default_headers.items():
            req.add_header(key, value)

        # Add data if provided
        if data:
            req.data = data

        # Make request
        try:
            with self.opener.open(req) as response:
                body = self._decompress_response(response)
                if return_headers:
                    headers_dict = dict(response.headers)
                    return body, headers_dict
                return body, None
        except urllib.error.HTTPError as e:
            error_body = self._decompress_response(e)
            raise Exception(
                f"HTTP {e.code}: {error_body.decode('utf-8', errors='ignore')}"
            )
        except Exception as e:
            raise Exception(f"Request failed: {e}")

    def get_vqd(self) -> str:
        """
        Get VQD token from status endpoint.
        Note: This requires a normal residential IP. Data centers/VPNs may receive
        a JS challenge instead of the VQD token.

        Returns:
            VQD token string
        """
        headers = {
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "x-vqd-accept": "1",
        }

        body, resp_headers = self._request(
            "GET", "/duckchat/v1/status", headers=headers, return_headers=True
        )

        # Extract VQD from response headers
        if resp_headers:
            self.vqd = resp_headers.get("x-vqd-4")
            self.vqd_hash = resp_headers.get("x-vqd-hash-1")

        if not self.vqd:
            error_msg = "Failed to get VQD token from response headers"
            if self.vqd_hash:
                error_msg += (
                    "\n\nThe server returned a JS challenge (x-vqd-hash-1) instead of a VQD token. "
                    "This typically happens when the request comes from:\n"
                    "  - A data center or cloud server\n"
                    "  - A VPN or proxy\n"
                    "  - An automated/suspicious source\n\n"
                    "Try running from a normal residential IP address."
                )
            raise Exception(error_msg)

        return self.vqd

    def chat(self, message: str, model: str = "gpt-4o-mini") -> str:
        """
        Send a chat message and get full response

        Args:
            message: Message to send
            model: Model to use

        Returns:
            Complete response text
        """
        # Get VQD if not available
        if not self.vqd:
            self.get_vqd()

        # Add message to history
        self.messages.append({"role": "user", "content": message})

        # Build request
        payload = {"model": model, "messages": self.messages}

        headers = {"content-type": "application/json", "x-vqd-4": self.vqd}

        # Add hash if available
        if self.vqd_hash:
            headers["x-vqd-hash-1"] = self.vqd_hash

        data = json.dumps(payload).encode("utf-8")

        # Make request and stream response
        url = f"{self.BASE_URL}/duckchat/v1/chat"
        req = urllib.request.Request(url, method="POST")

        # Add headers
        default_headers = self._get_headers()
        for key, value in default_headers.items():
            req.add_header(key, value)
        for key, value in headers.items():
            req.add_header(key, value)

        req.data = data

        # Collect response
        response_chunks = []

        with self.opener.open(req) as response:
            # Get new VQD from response headers
            new_vqd = response.headers.get("x-vqd-4")
            if new_vqd:
                self.vqd = new_vqd

            # Read streaming response
            buffer = b""
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                buffer += chunk

                # Process complete lines
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line_str = line.decode("utf-8").strip()

                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break

                        try:
                            event_data = json.loads(data_str)
                            message_chunk = event_data.get("message", "")
                            if message_chunk:
                                response_chunks.append(message_chunk)
                        except json.JSONDecodeError:
                            continue

        # Add assistant response to history
        full_response = "".join(response_chunks)
        if full_response:
            self.messages.append({"role": "assistant", "content": full_response})

        return full_response

    def stream_chat(
        self, message: str, model: str = "gpt-4o-mini"
    ) -> Generator[str, None, None]:
        """
        Stream chat response

        Args:
            message: Message to send
            model: Model to use

        Yields:
            Response chunks as they arrive
        """
        # Get VQD if not available
        if not self.vqd:
            self.get_vqd()

        # Add message to history
        self.messages.append({"role": "user", "content": message})

        # Build request
        payload = {"model": model, "messages": self.messages}

        headers = {"content-type": "application/json", "x-vqd-4": self.vqd}

        # Add hash if available
        if self.vqd_hash:
            headers["x-vqd-hash-1"] = self.vqd_hash

        data = json.dumps(payload).encode("utf-8")

        # Make request
        url = f"{self.BASE_URL}/duckchat/v1/chat"
        req = urllib.request.Request(url, method="POST")

        # Add headers
        default_headers = self._get_headers()
        for key, value in default_headers.items():
            req.add_header(key, value)
        for key, value in headers.items():
            req.add_header(key, value)

        req.data = data

        # Stream response
        full_response = []

        with self.opener.open(req) as response:
            # Get new VQD from response headers
            new_vqd = response.headers.get("x-vqd-4")
            if new_vqd:
                self.vqd = new_vqd

            # Read streaming response
            buffer = b""
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                buffer += chunk

                # Process complete lines
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    line_str = line.decode("utf-8").strip()

                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            # Add full response to history
                            complete = "".join(full_response)
                            if complete:
                                self.messages.append(
                                    {"role": "assistant", "content": complete}
                                )
                            return

                        try:
                            event_data = json.loads(data_str)
                            message_chunk = event_data.get("message", "")
                            if message_chunk:
                                full_response.append(message_chunk)
                                yield message_chunk
                        except json.JSONDecodeError:
                            continue

    def clear_history(self):
        """Clear conversation history"""
        self.messages = []

    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        return [
            "gpt-4o-mini",
            "claude-3-haiku-20240307",
            "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "o3-mini",
            "mistralai/Mistral-Small-24B-Instruct-2501",
        ]
