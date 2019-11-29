import logging
import unittest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):

    def test_lcm_m(self):
        from src.utils.computing import lcm_m
        logger.info(lcm_m([3, 8, 6]))


if __name__ == '__main__':
    unittest.main()
