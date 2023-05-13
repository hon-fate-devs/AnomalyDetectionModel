import json
import os
import string
import logging
from random import random, choices
from time import time, sleep
from kafka import KafkaProducer
from dataclasses import dataclass, asdict
from gen.generate import gen_time_series
from gen.System import System
import numpy as np


@dataclass
class DataPoint:
    tag_id: str
    timestamp: int
    value: float

data_freq = 1  # Hz

# tag list generation
tag_length = 7
num_tags = 10
tag_list = [''.join(choices(string.ascii_uppercase + string.digits, k=tag_length)) for _ in range(num_tags)]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info("establishing connection to kafka")
producer = KafkaProducer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'],
                         value_serializer=lambda x: json.dumps(asdict(x)).encode('utf-8'))
logging.info("connected to kafka, start publishing")

# generate params
dim = num_tags
noise = 0.3
# other params by default
# generate matrices
a = np.random.uniform(-5, 12, size=(dim, dim))
b = np.random.uniform(-5, 5, size=a.shape) + 5 * np.ones(a.shape)
sys = System(a, b)
# end section of params 

while True:
    cycle = gen_time_series(dim, 1, noise, sys=sys)
    for vector_observ in cycle:
        for tag_id, value in zip(tag_list, vector_observ):
            dp = DataPoint(tag_id, int(time()), value)
            producer.send('raw_data', dp)
            logging.debug(f"sent datapoint {dp}")
        # producer.flush()
        sleep(1/data_freq)

