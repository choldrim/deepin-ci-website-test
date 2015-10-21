#!/usr/bin/env python3

import unittest


from main import upload_result 


class TestMethods(unittest.TestCase):

    def test_upload_result(self):

        host = "10.0.255.1"
        r_id = "1234"
        ret = upload_result(r_id, host)

        self.assertTrue(ret)

if __name__ == "__main__":
    unittest.main()

