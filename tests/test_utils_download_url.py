import unittest

from efb_qq_plugin_go_cqhttp.Utils import normalize_qq_download_url


class NormalizeQQDownloadURLTest(unittest.TestCase):
    def test_preserves_signed_group_file_endpoint(self):
        url = "http://1.71.18.206/ftn_handler/signed-token/?fname=encoded-name"

        self.assertEqual(normalize_qq_download_url(url), url)

    def test_normalizes_regular_ip_download_endpoint(self):
        url = "https://43.128.17.103/download?appid=1407"

        self.assertEqual(
            normalize_qq_download_url(url),
            "https://multimedia.nt.qq.com.cn/download?appid=1407",
        )


if __name__ == "__main__":
    unittest.main()
