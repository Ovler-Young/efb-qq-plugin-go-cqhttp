import unittest
from unittest.mock import patch

import httpx

from efb_qq_plugin_go_cqhttp import Utils


class NormalizeQQDownloadURLTest(unittest.TestCase):
    def test_preserves_signed_group_file_endpoint(self):
        url = "http://1.71.18.206/ftn_handler/signed-token/?fname=encoded-name"

        self.assertEqual(Utils.normalize_qq_download_url(url), url)

    def test_normalizes_regular_ip_download_endpoint(self):
        url = "https://43.128.17.103/download?appid=1407"

        self.assertEqual(
            Utils.normalize_qq_download_url(url),
            "https://multimedia.nt.qq.com.cn/download?appid=1407",
        )

    def test_retries_original_url_after_normalized_request_fails(self):
        original_url = "http://43.128.17.103/download?appid=1407"
        normalized_url = "https://multimedia.nt.qq.com.cn/download?appid=1407"
        requested_urls = []

        class Stream:
            def __init__(self, url):
                self.url = url

            async def __aenter__(self):
                requested_urls.append(self.url)
                return self

            async def __aexit__(self, *args):
                return None

            def raise_for_status(self):
                if self.url == normalized_url:
                    request = httpx.Request("GET", self.url)
                    response = httpx.Response(502, request=request)
                    raise httpx.HTTPStatusError("normalized URL failed", request=request, response=response)

            @property
            def headers(self):
                return {"Content-Length": "4"}

            async def aiter_bytes(self, chunk_size):
                yield b"file"

        class Client:
            def __init__(self, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return None

            def stream(self, method, url):
                return Stream(url)

        with patch.object(Utils.httpx, "AsyncClient", Client):
            result = self.run_async(Utils.async_get_file_with_limit(original_url, max_bytes=10))

        self.assertEqual(requested_urls, [normalized_url, original_url])
        self.assertEqual(result.read(), b"file")
        result.close()

    def run_async(self, coroutine):
        return __import__("asyncio").run(coroutine)


if __name__ == "__main__":
    unittest.main()
