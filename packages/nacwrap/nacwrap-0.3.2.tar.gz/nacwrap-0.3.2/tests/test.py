import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from nacwrap import *

res = nacwrap.get_instance_data(
    "Sales Calls", status="Running", from_datetime=datetime.now() - timedelta(days=100)
)

pass
