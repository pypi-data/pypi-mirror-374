"""Tests for the placeholder functionality of the mlfastflow package."""

import unittest
from mlfastflow.core import Flow


class TestFlow(unittest.TestCase):
    """Test cases for the placeholder Flow class."""

    def test_flow_initialization(self):
        """Test that a Flow can be initialized."""
        flow = Flow()
        self.assertEqual(flow.name, "placeholder_flow")
        
        # Test with arguments that should be ignored
        flow_with_args = Flow(name="test_flow", some_arg=123)
        self.assertEqual(flow_with_args.name, "placeholder_flow")
    
    def test_string_representation(self):
        """Test string representation of Flow."""
        flow = Flow()
        self.assertEqual(str(flow), "Flow(name='placeholder_flow')")
        self.assertEqual(repr(flow), "Flow(name='placeholder_flow')")


if __name__ == "__main__":
    unittest.main()
