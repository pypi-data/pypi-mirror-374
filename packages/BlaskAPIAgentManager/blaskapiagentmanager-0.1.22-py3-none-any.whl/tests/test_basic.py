import unittest


class TestBasicImports(unittest.TestCase):
    """Basic tests to verify package imports work correctly."""

    def test_imports(self):
        """Test that the main classes can be imported."""
        try:
            from BlaskAPIAgentManager import BlaskAPIAgentManager
            from BlaskAPIAgentManager import BlaskAPIAgent
            from BlaskAPIAgentManager import PlannerTool
            from BlaskAPIAgentManager import ControllerTool

            self.assertTrue(True)  # If we got here, imports worked
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_version(self):
        """Test that the package has a version."""
        from BlaskAPIAgentManager import __version__

        self.assertIsNotNone(__version__)
        self.assertIsInstance(__version__, str)


if __name__ == "__main__":
    unittest.main()
