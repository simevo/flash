#!/bin/env python3

import datetime
import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
logging.getLogger("transformers").setLevel(logging.ERROR)

logger.info(f"========== Starting at: {datetime.datetime.now(tz=datetime.UTC)}")

model_paraphrase_multilingual_mpnet_base_v2 = SentenceTransformer(
    "paraphrase-multilingual-mpnet-base-v2",
)
logger.info(
    f"  Model name: {model_paraphrase_multilingual_mpnet_base_v2.model_card_data}",
)

model_use_cmlm_multilingual = SentenceTransformer(
    "sentence-transformers/use-cmlm-multilingual",
)
logger.info(f"  Model name: {model_use_cmlm_multilingual.model_card_data}")

logger.info(f"========== Completed at: {datetime.datetime.now(tz=datetime.UTC)}")
