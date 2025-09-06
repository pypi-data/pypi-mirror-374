import unittest
from sudarshan.crypto import create_engine, generate_kem_keypair, cleanup_engine

class TestSudarshanCrypto(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine()

    def tearDown(self):
        if self.engine:
            cleanup_engine(self.engine)

    def test_create_engine(self):
        self.assertIsNotNone(self.engine)

    def test_generate_kem_keypair(self):
        pub, sec = generate_kem_keypair(self.engine)
        self.assertIsInstance(pub, bytes)
        self.assertIsInstance(sec, bytes)
        self.assertEqual(len(pub), 1632)  # Kyber768 public key size
        self.assertEqual(len(sec), 2400)  # Kyber768 secret key size

if __name__ == '__main__':
    unittest.main()