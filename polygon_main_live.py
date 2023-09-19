import datetime
import concurrent.futures
import logging
from polygon import RESTClient
import signal
import sys
import pickle
import lz4.frame  # type: ignore
import time  

client = RESTClient(api_key="ckMNs2R4pNVdYxS3aaLCLWnSnmAz8wYs", trace=True)  # Uses POLYGON_API_KEY environment variable
client.subscribe("BTC")
print("bam")