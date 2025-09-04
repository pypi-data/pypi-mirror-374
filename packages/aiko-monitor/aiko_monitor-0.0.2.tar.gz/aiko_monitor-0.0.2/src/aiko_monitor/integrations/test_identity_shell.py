from ..identity import extract_user_id_sync, extract_user_id


# testing complete identity extract here
clerk_request1 = {
    "method": "GET",
    "url": "http://localhost:3001/api/hello",
    "headers": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "connection": "keep-alive",
        "cookie": "__clerk_db_jwt_1wkV3YZn=dvb_2zdWOjCAfqNAPVom0qWvwVbqjaL; __clerk_db_jwt=dvb_2zdWOjCAfqNAPVom0qWvwVbqjaL; clerk_active_context=sess_2zdWUYq4tHkrRvHCyNm6kSnUrOd:; __session=eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18yeW9DaUNvaHFhdGp5Z2Y4NlhpWGhueU84U1oiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDEiLCJleHAiOjE3NTIwNjE1MDgsImZ2YSI6WzAsLTFdLCJpYXQiOjE3NTIwNjE0NDgsImlzcyI6Imh0dHBzOi8vZGVlcC1za3Vuay02Mi5jbGVyay5hY2NvdW50cy5kZXYiLCJuYmYiOjE3NTIwNjE0MzgsInNpZCI6InNlc3NfMnpkV1VZcTR0SGtyUnZIQ3lObTZrU25Vck9kIiwic3ViIjoidXNlcl8yemRWaHROYmxzMW1PQzZyWGNyaW5LZWp2YUciLCJ2IjoyfQ.C1Bm4CYYVKaMysT0uWhSpLeDw5S2hC1Yc-GHah8JwslfD2tUIh73-ZSGVLZWxzMrQSmbYxTvjVlTUJQIKMmPv3M9H1T6LtypvndnCRTcgSFeN-xDFim1S5Elu3ZXHOClWBF-F4UuzpKw3lei5BVWcIIjdbI59zefFziDoZ3rQTqqrzN8554Vl89VUY5-E5KEv_AK6Feb3t6qUXxA8YunONliklEmRVGUHLvn02Bq86nF7oQ9s1MkJRFxn5yREkpnNLZcq6XFFFo6MI82mOv6tB6j06gR7Ge8TO41wupvxgOoC8Z47V3XUZHu-AYg5rb9zxaXI49EFPtNtszOA0Z-7g",
        "host": "localhost:3001",
        "referer": "http://localhost:3001/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    },
}

bearer_jwt= {
    "method": "GET",
    "url": "http://localhost:3003/api/hello",
    "headers": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwMDAwMDAwMDAsImlhdCI6MTUxNjIzOTAyMiwibmFtZSI6IkpvaG4gRG9lIiwic3ViIjoidXNlcjEyM0BleGFtcGxlLmNvbSJ9.2cQhQR0OT8rcDVIMcRWCHbc0t38KiGUNwTC8xwOzCAA",
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


mock_request_header = clerk_request1["headers"]
mock_request_cookie = clerk_request1["headers"]["cookie"]


id = extract_user_id(request_headers=bearer_jwt["headers"])

print(id)

hello = 5