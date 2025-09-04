import os
import unittest
import logging
from dotenv import load_dotenv
from langsmith import traceable
from BlaskAPIAgentManager import BlaskAPIAgent
from BlaskAPIAgentManager import PlannerTool
from BlaskAPIAgentManager import BlaskPipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Ensure LangSmith environment variables are set for tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "BlaskAPIAgentManager-Tests"


class TestBlaskAPIAgentManager(unittest.TestCase):
    """Tests for the BlaskAPIAgentManager package."""

    def setUp(self):
        """Set up test environment."""
        self.test_query = (
            # "Show YoY growth rates for all countries now, sorted by performance"
            # "Compare the performance of top 7 brands in South Africa for the first quarter of 2023 and in the frist quater 2025?"
            # "How many countries are supported by the Blask application?"
            # "Describe the changes in the Argentinian market over the past year."
            # "What's the top 10 brands sorting by MoM now in the Brazilian market."
            # "What's the players age distribution in the Brazilian market now."
            # "Give me the total list of Brands in the Togolese market."
            # "Give me overview of the all countries for the last 3 months."
            # "What is the top 7 Asian brands by ggr now?"
            # "What is the top 17 brands by ggr in India 2023-2024?"
            # "Research 1xBet in the last quarter of 2024."
            "Compare the performance of top 5 brands in the first quarter of 2025."
            # "Compare and make deep analysis of the performance of Bet365 in Brazilian and Indian markets in the first quarter of 2025."
            # "What is the total blask index for the last 3 months in Bangladesh market for the top 5 brands?"
            # "What is Betway GGR in June-September 2024?"
        )
        self.sample_rag_answer = """
        The US iGaming market has shown significant growth over the past few years. 
        According to research reports, several states have legalized online gambling, 
        including New Jersey, Pennsylvania, Michigan, and West Virginia.
        
        Key trends include:
        1. Mobile betting expansion
        2. Increasing merger and acquisition activity
        3. Integration of cryptocurrency payment options
        
        Revenue projections suggest continued growth through 2025.
        """

    @traceable(run_type="llm")
    def test_api_agent(self):
        """Test the basic API agent functionality."""

        if not os.getenv("BLASK_USERNAME") or not os.getenv("BLASK_PASSWORD"):
            self.skipTest("API credentials not available, skipping test")

        logger.info("Testing BlaskAPIAgent...")
        agent = BlaskAPIAgent(
            username=os.getenv("BLASK_USERNAME"), password=os.getenv("BLASK_PASSWORD")
        )

        auth_result = agent.authenticate()
        logger.info(f"Authentication result: {auth_result}")

        if not auth_result:
            self.skipTest("Authentication failed, skipping further tests")

        swagger_data = agent.load_swagger_spec()
        logger.info(f"Swagger spec loaded: {bool(swagger_data)}")
        self.assertTrue(bool(swagger_data), "Should load swagger specification")

        summary = agent.get_endpoint_summary()
        logger.info(
            f"Retrieved {sum(len(endpoints) for endpoints in summary.values())} endpoints across {len(summary)} categories"
        )
        self.assertTrue(len(summary) > 0, "Should retrieve endpoint summary")

    @traceable(run_type="llm")
    def test_planner_tool(self):
        """Test the planner tool."""

        if not os.getenv("BLASK_USERNAME") or not os.getenv("BLASK_PASSWORD"):
            self.skipTest("API credentials not available, skipping test")

        logger.info("Testing PlannerTool...")
        agent = BlaskAPIAgent(
            username=os.getenv("BLASK_USERNAME"), password=os.getenv("BLASK_PASSWORD")
        )

        if not agent.authenticate():
            self.skipTest("Authentication failed, skipping further tests")

        planner = PlannerTool(api_agent=agent)
        actions, explanation = planner.get_api_plan(self.test_query)

        self.assertIsNotNone(explanation, "Should provide a plan explanation")
        self.assertIsInstance(actions, list, "Actions should be a list")

    @traceable(run_type="llm")
    def test_get_api_data(self):
        """Test the get_api_data method."""

        if not os.getenv("BLASK_USERNAME") or not os.getenv("BLASK_PASSWORD"):
            self.skipTest("API credentials not available, skipping test")

        logger.info("Testing BlaskPipeline process_query...")
        pipeline = BlaskPipeline(
            username=os.getenv("BLASK_USERNAME"), password=os.getenv("BLASK_PASSWORD")
        )

        if not pipeline.api_agent.authenticate():
            self.skipTest("Authentication failed, skipping further tests")

        result = pipeline.process_query(self.test_query)
        logger.info(f"API Data Result: {result.get('summary')}")

        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIsInstance(result.get("summary"), str, "Summary should be a string")
        self.assertTrue(
            len(result.get("summary", "")) > 0, "Summary should not be empty"
        )


if __name__ == "__main__":
    unittest.main()
