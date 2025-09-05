import logging
import time
from dataclasses import asdict
from pprint import pformat

from substrate_telemetry_client import ChainGenesis, TelemetryClient

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    with TelemetryClient(chain=ChainGenesis.POLKADOT) as client:
        logger.info("Connection established. Waiting 5 seconds for initial data...")
        time.sleep(5)

        nodes = client.get_nodes()
        logger.info(f"Found {len(nodes)} nodes. Printing node details as dicts.")

        for idx, node_data in enumerate(nodes[:3], 1):
            node_dict = asdict(node_data)
            logger.info(
                f"Node {idx} details:\n{pformat(node_dict)}"
            )
            logger.info("-" * 20)

        stats = client.get_chain_stats()
        logger.info("Printing chain stats as dataclasses.")
        if stats:
            logger.info(pformat(stats))

    logger.info("Finished.")


if __name__ == "__main__":
    main()
