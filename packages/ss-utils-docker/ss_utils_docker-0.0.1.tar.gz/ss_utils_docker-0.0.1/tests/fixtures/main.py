import logging
import pandas as pd  # type: ignore


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.info(pd.DataFrame({"a": [1, 2, 3]}))
