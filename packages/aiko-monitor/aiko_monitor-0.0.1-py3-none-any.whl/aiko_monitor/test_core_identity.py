#!/usr/bin/env python3
"""Test file for core_identity.py following the same structure as the Node.js tests."""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from aiko_monitor.core_identity import (
    parse_headers, is_clerk, detect_provider, is_bearer_jwt, 
    is_supabase, is_authjs, is_better_auth
)

# JWT tokens from the original test file
JWT_SUB = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkpvaG4gRG9lIiwic3ViIjoidXNlcjEyM0BleGFtcGxlLmNvbSJ9.2cQhQR0OT8rcDVIMcRWCHbc0t38KiGUNwTC8xwOzCAA"
JWT_USER_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkphbmUgU21pdGgiLCJ1c2VyX2lkIjoidXNlcjQ1NkBleGFtcGxlLmNvbSJ9.DHR3IwfEyhn4rlhIIsthYmDEfE0nE-dlzwn3QDQZWAk"
JWT_UID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkJvYiBKb2huc29uIiwidWlkIjoidXNlcjc4OUBleGFtcGxlLmNvbSJ9.bXXnNuehkoGcm1dacT7bsP0ZElqWLlOc07o20o64FYc"
JWT_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwiaWQiOiJ1c2VyOTk5QGV4YW1wbGUuY29tIiwibmFtZSI6IkFsaWNlIEJyb3duIn0.bClZFzSNPOEx6qh66DCbhOX4xKEVdH1SPN77dqM-u7o"
JWT_USERID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkNoYXJsaWUgV2lsc29uIiwidXNlcmlkIjoidXNlcjExMUBleGFtcGxlLmNvbSJ9.mcaJUp-Os1rgHHJ0aB1YUw5tuTgIwvgRhDQu88WOutA"
JWT_EMAIL = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InVzZXIyMjJAZXhhbXBsZS5jb20iLCJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkRpYW5hIERhdmlzIn0._GSrQE8uyvrZBPiACERoAIsGZDNyVaG25N3uUnaBO6I"
JWT_USERNAME = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkV2ZSBNaWxsZXIiLCJ1c2VybmFtZSI6InVzZXIzMzNAZXhhbXBsZS5jb20ifQ.Ir7n0oOD2MD-zXxQecqsq5OKXQKw9rjruafj5-0X3wM"
JWT_NESTED_USER_EMAIL = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkZyYW5rIEdhcmNpYSIsInVzZXIiOnsiZW1haWwiOiJuZXN0ZWQxQGV4YW1wbGUuY29tIiwiaWQiOiJuZXN0ZWQtMTIzIn19.psEuVaqai_LE7R3MP-gUmQdt9I9oTlGFvbGuKq53oCI"
JWT_NESTED_PROFILE_USER_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkdyYWNlIExlZSIsInByb2ZpbGUiOnsidXNlcl9pZCI6Im5lc3RlZDJAZXhhbXBsZS5jb20ifX0.YPtC-q0FADljKlP2DTRYTRO-fqBmXW4f0qtj65Bf-ZM"
JWT_PREFERRED_USERNAME = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkhlbnJ5IFRheWxvciIsInByZWZlcnJlZF91c2VybmFtZSI6InByZWZlcnJlZEBleGFtcGxlLmNvbSJ9.-FK5dto6Ug-afrvzQtMG6g1DOBtD_r50DMjCQxo_jto"
JWT_UPN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImZhbWlseV9uYW1lIjoiQW5kZXJzb24iLCJnaXZlbl9uYW1lIjoiSXNhYmVsbGEiLCJpYXQiOjE1MTYyMzkwMjIsInVwbiI6InVwbkBleGFtcGxlLmNvbSJ9.WMJDqbwoBxNMIE160T1C1mMkZYqiSis3n6QngQ936a4"
JWT_UNIQUE_NAME = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhenAiOiJjbGllbnQxMjMiLCJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkphY2sgV2lsc29uIiwidW5pcXVlX25hbWUiOiJ1bmlxdWVAZXhhbXBsZS5jb20ifQ.7k-jOYiqwyKV5BePGeM9BUUfEJgT294_V7zuNY5kvYg"
JWT_CUSTOM_NESTED = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjdXN0b21fY2xhaW1zIjp7InVzZXJfaWRlbnRpZmllciI6ImN1c3RvbUBleGFtcGxlLmNvbSJ9LCJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IktlbGx5IEJyb3duIn0.77mLbJ0PpDQMCw1THGkduiiHT-57SiFMo-VuykmCPAc"


def make_jwt_request(jwt):
    """Create a mock JWT request."""
    return {
        "method": "GET",
        "url": "http://localhost:3003/api/hello",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {jwt}",
            "connection": "keep-alive",
            "cookie": "",
            "host": "localhost:3003",
            "referer": "http://localhost:3003/",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        },
    }


clerkRequest1 = {
  "method": "GET",
  "url": "http://localhost:3001/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "cookie":
      "__clerk_db_jwt_1wkV3YZn=dvb_2zdWOjCAfqNAPVom0qWvwVbqjaL; __clerk_db_jwt=dvb_2zdWOjCAfqNAPVom0qWvwVbqjaL; clerk_active_context=sess_2zdWUYq4tHkrRvHCyNm6kSnUrOd:; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yeW9DaUNvaHFhdGp5Z2Y4NlhpWGhueU84U1oiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDEiLCJleHAiOjE3NTIwNjE1MDgsImZ2YSI6WzAsLTFdLCJpYXQiOjE3NTIwNjE0NDgsImlzcyI6Imh0dHBzOi8vZGVlcC1za3Vuay02Mi5jbGVyay5hY2NvdW50cy5kZXYiLCJuYmYiOjE3NTIwNjE0MzgsInNpZCI6InNlc3NfMnpkV1VZcTR0SGtyUnZIQ3lObTZrU25Vck9kIiwic3ViIjoidXNlcl8yemRWaHROYmxzMW1PQzZyWGNyaW5LZWp2YUciLCJ2IjoyfQ.C1Bm4CYYVKaMysT0uWhSpLeDw5S2hC1Yc-GHah8JwslfD2tUIh73-ZSGVLZWxzMrQSmbYxTvjVlTUJQIKMmPv3M9H1T6LtypvndnCRTcgSFeN-xDFim1S5Elu3ZXHOClWBF-F4UuzpKw3lei5BVWcIIjdbI59zefFziDoZ3rQTqqrzN8554Vl89VUY5-E5KEv_AK6Feb3t6qUXxA8YunONliklEmRVGUHLvn02Bq86nF7oQ9s1MkJRFxn5yREkpnNLZcq6XFFFo6MI82mOv6tB6j06gR7Ge8TO41wupvxgOoC8Z47V3XUZHu-AYg5rb9zxaXI49EFPtNtszOA0Z-7g; __session_1wkV3YZn=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yeW9DaUNvaHFhdGp5Z2Y4NlhpWGhueU84U1oiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDEiLCJleHAiOjE3NTIwNjE1MDgsImZ2YSI6WzAsLTFdLCJpYXQiOjE3NTIwNjE0NDgsImlzcyI6Imh0dHBzOi8vZGVlcC1za3Vuay02Mi5jbGVyay5hY2NvdW50cy5kZXYiLCJuYmYiOjE3NTIwNjE0MzgsInNpZCI6InNlc3NfMnpkV1VZcTR0SGtyUnZIQ3lObTZrU25Vck9kIiwic3ViIjoidXNlcl8yemRWaHROYmxzMW1PQzZyWGNyaW5LZWp2YUciLCJ2IjoyfQ.C1Bm4CYYVKaMysT0uWhSpLeDw5S2hC1Yc-GHah8JwslfD2tUIh73-ZSGVLZWxzMrQSmbYxTvjVlTUJQIKMmPv3M9H1T6LtypvndnCRTcgSFeN-xDFim1S5Elu3ZXHOClWBF-F4UuzpKw3lei5BVWcIIjdbI59zefFziDoZ3rQTqqrzN8554Vl89VUY5-E5KEv_AK6Feb3t6qUXxA8YunONliklEmRVGUHLvn02Bq86nF7oQ9s1MkJRFxn5yREkpnNLZcq6XFFFo6MI82mOv6tB6j06gR7Ge8TO41wupvxgOoC8Z47V3XUZHu-AYg5rb9zxaXI49EFPtNtszOA0Z-7g; __client_uat_1wkV3YZn=1752061446; __client_uat=1752061446",
    "host": "localhost:3001",
    "referer": "http://localhost:3001/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}


clerkRequest2 = {
  "method": "PUT",
  "url": "http://localhost:3001/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "content-length": "0",
    "cookie":
      "__clerk_db_jwt_1wkV3YZn=dvb_2zdWOjCAfqNAPVom0qWvwVbqjaL; __clerk_db_jwt=dvb_2zdWOjCAfqNAPVom0qWvwVbqjaL; clerk_active_context=sess_2zdWUYq4tHkrRvHCyNm6kSnUrOd:; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yeW9DaUNvaHFhdGp5Z2Y4NlhpWGhueU84U1oiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDEiLCJleHAiOjE3NTIwNjE1MDgsImZ2YSI6WzAsLTFdLCJpYXQiOjE3NTIwNjE0NDgsImlzcyI6Imh0dHBzOi8vZGVlcC1za3Vuay02Mi5jbGVyay5hY2NvdW50cy5kZXYiLCJuYmYiOjE3NTIwNjE0MzgsInNpZCI6InNlc3NfMnpkV1VZcTR0SGtyUnZIQ3lObTZrU25Vck9kIiwic3ViIjoidXNlcl8yemRWaHROYmxzMW1PQzZyWGNyaW5LZWp2YUciLCJ2IjoyfQ.C1Bm4CYYVKaMysT0uWhSpLeDw5S2hC1Yc-GHah8JwslfD2tUIh73-ZSGVLZWxzMrQSmbYxTvjVlTUJQIKMmPv3M9H1T6LtypvndnCRTcgSFeN-xDFim1S5Elu3ZXHOClWBF-F4UuzpKw3lei5BVWcIIjdbI59zefFziDoZ3rQTqqrzN8554Vl89VUY5-E5KEv_AK6Feb3t6qUXxA8YunONliklEmRVGUHLvn02Bq86nF7oQ9s1MkJRFxn5yREkpnNLZcq6XFFFo6MI82mOv6tB6j06gR7Ge8TO41wupvxgOoC8Z47V3XUZHu-AYg5rb9zxaXI49EFPtNtszOA0Z-7g; __session_1wkV3YZn=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yeW9DaUNvaHFhdGp5Z2Y4NlhpWGhueU84U1oiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDEiLCJleHAiOjE3NTIwNjE1MDgsImZ2YSI6WzAsLTFdLCJpYXQiOjE3NTIwNjE0NDgsImlzcyI6Imh0dHBzOi8vZGVlcC1za3Vuay02Mi5jbGVyay5hY2NvdW50cy5kZXYiLCJuYmYiOjE3NTIwNjE0MzgsInNpZCI6InNlc3NfMnpkV1VZcTR0SGtyUnZIQ3lObTZrU25Vck9kIiwic3ViIjoidXNlcl8yemRWaHROYmxzMW1PQzZyWGNyaW5LZWp2YUciLCJ2IjoyfQ.C1Bm4CYYVKaMysT0uWhSpLeDw5S2hC1Yc-GHah8JwslfD2tUIh73-ZSGVLZWxzMrQSmbYxTvjVlTUJQIKMmPv3M9H1T6LtypvndnCRTcgSFeN-xDFim1S5Elu3ZXHOClWBF-F4UuzpKw3lei5BVWcIIjdbI59zefFziDoZ3rQTqqrzN8554Vl89VUY5-E5KEv_AK6Feb3t6qUXxA8YunONliklEmRVGUHLvn02Bq86nF7oQ9s1MkJRFxn5yREkpnNLZcq6XFFFo6MI82mOv6tB6j06gR7Ge8TO41wupvxgOoC8Z47V3XUZHu-AYg5rb9zxaXI49EFPtNtszOA0Z-7g; __client_uat_1wkV3YZn=1752061446; __client_uat=1752061446",
    "host": "localhost:3001",
    "origin": "http://localhost:3001",
    "referer": "http://localhost:3001/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}


supabaseRequest1 = {
  "method": "GET",
  "url": "http://localhost:3001/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9",
    "authorization":
      "Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IldWM1ozdjYrdkdsMys5NUYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2h2Y3loYXV0Z3FtdWdtamNrY3JvLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1ZTg4ZTZjZS0zYWQ5LTQ5ZTYtODhjMC03ZDBiMjc5ZGY5ZjkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzUyNDM3NTc1LCJpYXQiOjE3NTI0MzM5NzUsImVtYWlsIjoicGl4cWMxMTU5QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJwaXhxYzExNTlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiNWU4OGU2Y2UtM2FkOS00OWU2LTg4YzAtN2QwYjI3OWRmOWY5In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib3RwIiwidGltZXN0YW1wIjoxNzUyNDMzOTc1fV0sInNlc3Npb25faWQiOiI2MWVhMDlhZS0yNWZhLTQ3NjItOGNmMS1iZTRhZDRmZTdiNDAiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.RUkLr_BQAdUjdy0BbjxuC_gaUZNg631bYaLpkjHAM4w",
    "connection": "keep-alive",
    "host": "localhost:3001",
    "priority": "u=3, i",
    "referer": "http://localhost:3001/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
  },
}

supabaseRequest2 = {
  "method": "PUT",
  "url": "http://localhost:3001/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9",
    "authorization":
      "Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IldWM1ozdjYrdkdsMys5NUYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2h2Y3loYXV0Z3FtdWdtamNrY3JvLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1ZTg4ZTZjZS0zYWQ5LTQ5ZTYtODhjMC03ZDBiMjc5ZGY5ZjkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzUyNDM3NTc1LCJpYXQiOjE3NTI0MzM5NzUsImVtYWlsIjoicGl4cWMxMTU5QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJwaXhxYzExNTlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiNWU4OGU2Y2UtM2FkOS00OWU2LTg4YzAtN2QwYjI3OWRmOWY5In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib3RwIiwidGltZXN0YW1wIjoxNzUyNDMzOTc1fV0sInNlc3Npb25faWQiOiI2MWVhMDlhZS0yNWZhLTQ3NjItOGNmMS1iZTRhZDRmZTdiNDAiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.RUkLr_BQAdUjdy0BbjxuC_gaUZNg631bYaLpkjHAM4w",
    "connection": "keep-alive",
    "content-length": "0",
    "host": "localhost:3001",
    "origin": "http://localhost:3001",
    "priority": "u=3, i",
    "referer": "http://localhost:3001/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
  },
}


authjsRequest1 = {
  "method": "GET",
  "url": "http://localhost:3002/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "cookie":
      "authjs.csrf-token=ac8984db7d5cfb39bbb078ad61677d05aa30a35ea2daa29339b89e1a5e0c3c08%7C67838f80dbbfbd181d8979299da97a14668b509eedbe8a2ac751057471719562; authjs.callback-url=http%3A%2F%2Flocalhost%3A3002%2F; authjs.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiT18yRkwxdWNUZXBJYmJMME5TWTFTVDdMNlBGb20wQkNfYTRvZlFJTk5RS0RkMzVGN0stMjZBZmFJTmFsMlFodGFoamxNTkNGUUNNcHJDMjZOdzU0d3cifQ..FaY3GOlu2TO3QwY6ynLrhw.p5cvof6R4xScmCVUkTFmbnbr_4gk-0z3TG2uOK8tR4_C942Wz_BVq60qI-VIElUlK1b4JTSGJO_q3n_IMOvfh0A4q4Mw2jcL3IYU1u37hIEAxhuIhv6pXI7-XwzZtaDMJ2Vcizrz3UhFgaxE1FXu7DMTpWjrNGpGrMB1GRBBzwZJlq0oPEFtliOq-0xc1Dnb.TfgiiqHTS7hGNa3X6hZKCLN48iB7DO1ahKJznxruLgY",
    "host": "localhost:3002",
    "referer": "http://localhost:3002/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}

authjsRequest2 = {
  "method": "PUT",
  "url": "http://localhost:3002/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "content-length": "0",
    "cookie":
      "authjs.csrf-token=ac8984db7d5cfb39bbb078ad61677d05aa30a35ea2daa29339b89e1a5e0c3c08%7C67838f80dbbfbd181d8979299da97a14668b509eedbe8a2ac751057471719562; authjs.callback-url=http%3A%2F%2Flocalhost%3A3002%2F; authjs.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwia2lkIjoiT18yRkwxdWNUZXBJYmJMME5TWTFTVDdMNlBGb20wQkNfYTRvZlFJTk5RS0RkMzVGN0stMjZBZmFJTmFsMlFodGFoamxNTkNGUUNNcHJDMjZOdzU0d3cifQ..nNYsW-T9GJiHmQYtyuLIBw.W6wQvajnupYM1_4fDrgqXQuzU85KzjUJP170wFW06B8jIKJpdMDkwPwQI0TAe0CC7Eh8FYgOGvFtAFNLeRBN525I9922mc0fNhLoOaS48eaBDX0X-xAYKVps8GcDAEnIuEGj_V4LFZQv_M8F2KQrXOhZBanok_6T1NeE3u0VUA82-438Q2Ur3rNszbfXs5w7.zpr7InBU4XwFm7JUhcjFV3Hcx0s-EaDMs0SI_exKcI4",
    "host": "localhost:3002",
    "origin": "http://localhost:3002",
    "referer": "http://localhost:3002/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}

betterAuthRequest1 = {
  "method": "GET",
  "url": "http://localhost:3000/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "cookie":
      "better-auth.session_token=jXImZhJ9f1J0cb97vyZUoiLGmrjwftNv.h428fmH6la9%2BjsohnMilqUrmzj0mgyDkYKeTTVohf6c%3D",
    "host": "localhost:3000",
    "referer": "http://localhost:3000/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}

betterAuthRequest2 = {
  "method": "PUT",
  "url": "http://localhost:3000/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "content-length": "0",
    "cookie":
      "better-auth.session_token=jXImZhJ9f1J0cb97vyZUoiLGmrjwftNv.h428fmH6la9%2BjsohnMilqUrmzj0mgyDkYKeTTVohf6c%3D",
    "host": "localhost:3000",
    "origin": "http://localhost:3000",
    "referer": "http://localhost:3000/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}

auth0Request1 = {
  "method": "GET",
  "url": "http://localhost:3001/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "cookie":
      "_legacy_auth0.GUlD6yxK8FSKYFkpwcrMd2zKkEpF9GqI.is.authenticated=True; auth0.GUlD6yxK8FSKYFkpwcrMd2zKkEpF9GqI.is.authenticated=True",
    "host": "localhost:3001",
    "referer": "http://localhost:3001/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}

auth0Request2 = {
  "method": "PUT",
  "url": "http://localhost:3001/api/hello",
  "headers": {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "connection": "keep-alive",
    "content-length": "0",
    "cookie":
      "_legacy_auth0.GUlD6yxK8FSKYFkpwcrMd2zKkEpF9GqI.is.authenticated=True; auth0.GUlD6yxK8FSKYFkpwcrMd2zKkEpF9GqI.is.authenticated=True",
    "host": "localhost:3001",
    "origin": "http://localhost:3001",
    "referer": "http://localhost:3001/",
    "sec-ch-ua":
      '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
  },
}



class TestBearerJWTAuthentication:
    """Test bearer JWT authentication detection."""
    
    @pytest.mark.parametrize("description,token", [
        ("sub claim", JWT_SUB),
        ("user_id claim", JWT_USER_ID),
        ("uid claim", JWT_UID),
        ("id claim", JWT_ID),
        ("userid claim", JWT_USERID),
        ("email claim", JWT_EMAIL),
        ("username claim", JWT_USERNAME),
        ("nested user.email", JWT_NESTED_USER_EMAIL),
        ("nested profile.user_id", JWT_NESTED_PROFILE_USER_ID),
        ("preferred_username", JWT_PREFERRED_USERNAME),
        ("upn claim", JWT_UPN),
        ("unique_name", JWT_UNIQUE_NAME),
        ("custom nested", JWT_CUSTOM_NESTED),
    ])
    def test_handles_bearer_jwt_with_various_claims(self, description, token):
        """Test bearer JWT with various claim types."""
        request = make_jwt_request(token)
        normalized = parse_headers(request["headers"])
        
        assert normalized.headers["authorization"] == f"Bearer {token}"
        assert is_bearer_jwt(normalized) == True
        assert detect_provider(normalized).provider == "bearer-jwt"
        assert detect_provider(normalized).type == "jwt"

    @pytest.mark.parametrize("description,token", [
        ("x-bearer-jwt header sub", JWT_SUB),
        ("x-bearer-jwt header user_id", JWT_USER_ID),
        ("x-bearer-jwt header uid", JWT_UID),
    ])
    def test_handles_x_bearer_jwt_header(self, description, token):
        """Test x-bearer-jwt header detection."""
        request = make_jwt_request(token)
        request["headers"]["x-bearer-jwt"] = f"Bearer {token}"
        del request["headers"]["authorization"]
        
        normalized = parse_headers(request["headers"])
        assert normalized.headers["x-bearer-jwt"] == f"Bearer {token}"
        assert is_bearer_jwt(normalized) == True
        assert detect_provider(normalized).provider == "bearer-jwt"
        assert detect_provider(normalized).type == "jwt"


class TestClerkIdentityDetection:
    """Test Clerk identity detection."""

    @pytest.mark.parametrize("request_name,request_data", [
        ("GET request", clerkRequest1),
        ("PUT request", clerkRequest2),
    ])
    def test_handles_clerk_authentication(self, request_name, request_data):
        """Test Clerk authentication for different request types."""
        normalized = parse_headers(request_data["headers"])

        assert normalized.headers["cookie"] is not None
        assert "__session=" in normalized.headers["cookie"]
        assert "__client_uat=" in normalized.headers["cookie"]
        assert is_clerk(normalized) == True
        assert detect_provider(normalized).provider == "clerk"
        assert detect_provider(normalized).type == "jwt"


class TestSupabaseIdentityDetection:
    """Test Supabase identity detection."""

    @pytest.mark.parametrize("request_name,request_data", [
        ("GET request", supabaseRequest1),
        ("PUT request", supabaseRequest2),
    ])
    def test_handles_supabase_authentication(self, request_name, request_data):
        """Test Supabase authentication for different request types."""
        normalized = parse_headers(request_data["headers"])

        assert normalized.headers["authorization"] is not None
        assert "Bearer " in normalized.headers["authorization"]
        assert is_supabase(normalized) == True
        assert detect_provider(normalized).provider == "supabase"
        assert detect_provider(normalized).type == "jwt"

    def test_detects_supabase_by_iss_claim_containing_supabase_co(self):
        """Test Supabase detection by iss claim."""
        normalized = parse_headers(supabaseRequest1["headers"])
        assert is_supabase(normalized) == True

    def test_does_not_detect_non_supabase_jwt_as_supabase(self):
        """Test that non-Supabase JWT is not detected as Supabase."""
        regular_jwt_request = make_jwt_request(JWT_EMAIL)
        normalized = parse_headers(regular_jwt_request["headers"])
        assert is_supabase(normalized) == False




class TestAuthJSIdentityDetection:
    """Test AuthJS identity detection."""

    @pytest.mark.parametrize("request_name,request_data", [
        ("GET request", authjsRequest1),
        ("PUT request", authjsRequest2),
    ])
    def test_handles_authjs_authentication(self, request_name, request_data):
        """Test AuthJS authentication for different request types."""
        normalized = parse_headers(request_data["headers"])

        assert normalized.headers["cookie"] is not None
        assert "authjs.session-token=" in normalized.headers["cookie"]
        assert is_authjs(normalized) == True
        assert detect_provider(normalized).provider == "authjs"
        assert detect_provider(normalized).type == "cookie"

    def test_detects_authjs_by_session_token_cookie(self):
        """Test AuthJS detection by session token cookie."""
        normalized = parse_headers(authjsRequest1["headers"])
        assert is_authjs(normalized) == True

    def test_does_not_detect_request_without_authjs_cookie_as_authjs(self):
        """Test that request without AuthJS cookie is not detected as AuthJS."""
        regular_jwt_request = make_jwt_request(JWT_EMAIL)
        normalized = parse_headers(regular_jwt_request["headers"])
        assert is_authjs(normalized) == False



class TestBetterAuthIdentityDetection:
      """Test Better Auth identity detection."""

      @pytest.mark.parametrize("request_name,request_data", [
          ("GET request", betterAuthRequest1),
          ("PUT request", betterAuthRequest2),
      ])
      def test_handles_better_auth_authentication(self, request_name, request_data):
          """Test Better Auth authentication for different request types."""
          normalized = parse_headers(request_data["headers"])

          assert normalized.headers["cookie"] is not None
          assert "better-auth.session_token=" in normalized.headers["cookie"]
          assert is_better_auth(normalized) == True
          assert detect_provider(normalized).provider == "betterauth"
          assert detect_provider(normalized).type == "cookie"

      def test_detects_better_auth_by_session_token_cookie(self):
          """Test Better Auth detection by session token cookie."""
          normalized = parse_headers(betterAuthRequest1["headers"])
          assert is_better_auth(normalized) == True

      def test_does_not_detect_request_without_better_auth_cookie_as_better_auth(self):
          """Test that request without Better Auth cookie is not detected as Better Auth."""
          regular_jwt_request = make_jwt_request(JWT_EMAIL)
          normalized = parse_headers(regular_jwt_request["headers"])
          assert is_better_auth(normalized) == False



if __name__ == "__main__":
    pytest.main([__file__, "-v"])