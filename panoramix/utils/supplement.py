import json
import logging
import lzma
import os
import sys
import time
import pickle
from pathlib import Path
from zipfile import ZipFile
from typing import Optional
import shelve
import dbm
from panoramix.utils.helpers import (
    cache_dir,
    cached,
)

"""
    a module for management of bytes4 signatures from the database

     db schema:

     hash - 0x12345678
     name - transferFrom
     folded_name - transferFrom(address,address,uint256)
     cooccurs - comma-dellimeted list of hashes: `0x12312312,0xabababab...`
     params - json: `[
            {
              "type": "address",
              "name": "_from"
            },
            {
              "type": "address",
              "name": "_to"
            },
            {
              "type": "uint256",
              "name": "_value"
            }
          ]`

"""

logger = logging.getLogger(__name__)


def abi_path():
    return cache_dir() / "abi_db.pkl"


def check_supplements():
    if not abi_path().exists():
        compressed_supplements = Path(__file__).parent.parent / "data" / "abi_dump.xz"
        logger.info("Loading %s into %s...", compressed_supplements, abi_path())
        # Use pickle instead of shelve/dbm to avoid DBM compatibility issues on macOS
        abi_dict = {}
        with lzma.open(compressed_supplements) as inf:
            for line in inf:
                line = json.loads(line)
                selector, abi = line["selector"], line["abi"]
                abi_dict[selector] = abi
        
        # Write the dictionary to a pickle file
        with open(str(abi_path()), 'wb') as f:
            pickle.dump(abi_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

        assert abi_path().exists()

        logger.info("%s is ready.", abi_path())


@cached
def fetch_sig(hash) -> Optional[dict]:
    check_supplements()

    if type(hash) == str:
        hash = int(hash, 16)
    hash = "{:#010x}".format(hash)

    # Load from pickle file instead of shelve
    with open(str(abi_path()), 'rb') as f:
        abi_dict = pickle.load(f)
        return abi_dict.get(hash)
