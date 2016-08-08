import unittest
import logging
from queue import Queue
import time

try:
    from RPi import GPIO
except RuntimeError:
    # Use fake GPIO
    from GPIOSim.RPi import GPIO

from tuxeatpi.fake_components.wings import FakeWings


class WingsTest(unittest.TestCase):

    def setUp(self):
        """Method called before each test function"""
        GPIO.cleanup()
        GPIO.init()
        # Start GPIO eventer
        self.eventer = GPIO.Eventer()
        self.eventer.start()

    def tearDown(self):
        """Method called after each test function"""
        self.eventer.stop()

    def test_wings(self):
        """Testing basic moving functions"""
        # init wings
        pins = {"left_switch": 17, "right_switch": 4, "position": 25, "movement": 22}
        event_queue = Queue()
        logging.basicConfig()
        logger = logging.getLogger(name="TuxEatPi")
        logger.setLevel(logging.DEBUG)
        wings = FakeWings(pins, event_queue, logger)

        # Test calibrate
        time.sleep(5)
        self.assertEqual(wings.get_position(), "down")

        # Move up
        wings.move_to_position("up")
        time.sleep(2)
        self.assertEqual(wings.get_position(), "up")
        # Move down
        wings.move_to_position("down")
        time.sleep(2)
        self.assertEqual(wings.get_position(), "down")
        # Move 5 times
        wings.move_count(5)
        time.sleep(5)
        self.assertEqual(wings.get_position(), "up")

    def test_wings_moving(self):
        """Testing other moving functions"""
        # init wings
        pins = {"left_switch": 17, "right_switch": 4, "position": 25, "movement": 22}
        event_queue = Queue()
        logging.basicConfig()
        logger = logging.getLogger(name="TuxEatPi")
        logger.setLevel(logging.DEBUG)
        wings = FakeWings(pins, event_queue, logger)
        # Test calibrate
        time.sleep(5)
        self.assertEqual(wings.get_position(), "down")
        # Test count
        wings.move_count(3)
        time.sleep(3)
        self.assertEqual(wings.get_position(), "up")
        wings.move_count(2)
        time.sleep(2)
        self.assertEqual(wings.get_position(), "up")
        # Test moving by time
        wings.move_time(3)
        time.sleep(1)
        self.assertTrue(wings.is_moving)
        time.sleep(3)
        self.assertFalse(wings.is_moving)
        # Bad move
        self.assertRaises(Exception, lambda: wings.move_to_position("bottom"))

    def test_wings_push_switches(self):
        """Testing push switches"""
        # init wings
        pins = {"left_switch": 17, "right_switch": 4, "position": 25, "movement": 22}
        event_queue = Queue()
        logging.basicConfig()
        logger = logging.getLogger(name="TuxEatPi")
        logger.setLevel(logging.DEBUG)
        wings = FakeWings(pins, event_queue, logger)
        # Test calibrate
        time.sleep(5)
        self.assertEqual(wings.get_position(), "down")

        # test left switch event
        wings.push_wing('left')
        event = event_queue.get(timeout=5)
        self.assertEqual(event.component, 'FakeWings')
        self.assertEqual(event.pin_id, wings.pins.get('left_switch'))
        self.assertEqual(event.name, 'left_switch')

        # test left switch event
        wings.push_wing('right')
        event = event_queue.get(timeout=5)
        self.assertEqual(event.component, 'FakeWings')
        self.assertEqual(event.pin_id, wings.pins.get('right_switch'))
        self.assertEqual(event.name, 'right_switch')
