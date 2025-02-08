import logging

from dotenv import load_dotenv

from lumyn.llm_backends.get_default_backend import get_llm_backend_for_tools
from lumyn.tools.graph_traversal.nl2_check_connected import NL2GraphCheckConnectedCustomTool
from lumyn.tools.graph_traversal.nl2_get_node_info import NL2GraphGetNodeInfoCustomTool

# Load environment variables from the .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_nl2graph_check_connected():
    # Instantiate tool 1
    tool_1 = NL2GraphGetNodeInfoCustomTool(llm_backend=get_llm_backend_for_tools())

    node_1 = tool_1._run("Id of front-service given the topology file at ../../../outputs/k8s_topology.json", "../../../outputs/k8s_taxonomy.json", "../../../outputs/k8s_topology.json")
    node_2 = tool_1._run("Id of back-service given the topology file at ../../../outputs/k8s_topology.json", "../../../outputs/k8s_taxonomy.json", "../../../outputs/k8s_topology.json")

    # Instantiate tool 2
    tool_2 = NL2GraphCheckConnectedCustomTool(llm_backend=get_llm_backend_for_tools())

    # Define a natural language query
    nl_query = f"are {node_1[0]["id"]} and {node_2[0]["id"]} connected given the topology file at ../../../outputs/k8s_topology.json"

    # Call the tool's _run method to test it
    result = tool_2._run(nl_query, "../../../outputs/k8s_taxonomy.json", "../../../outputs/k8s_topology.json")
    logger.info(f"Result from the tool: \n{result}")
    print(result)


if __name__ == "__main__":
    test_nl2graph_check_connected()
