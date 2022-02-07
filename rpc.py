#! /usr/bin/python3

import json
import argparse
import subprocess

from utils.filter import filter
from utils.printing import prettyprint
from utils.convert import find_type_and_convert

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--command")
parser.add_argument("-l", "--params", nargs="*", default=[] ,help="Space separated command list of params")
parser.add_argument("-p", "--port", default=18400, help="Target node port")
# General Options
parser.add_argument("-d", "--depth", default=None, type=int, help="Response json depth")
parser.add_argument("-f", "--filter", nargs="*", default=[], help="Filter the JSON response with multiple keyword.")
parser.add_argument("-s", "--showcurl", action="store_true", help="Show the curl request")

args = parser.parse_args()

args.params = list(map(find_type_and_convert, args.params))


if __name__ == '__main__':
    sent_data = json.dumps({
        "jsonrpc": "2.0",
        "id": "1",
        "method": args.command,
        "params": args.params
    })

    curl = ["curl", "-d", sent_data, "-u", "bitcoin:bitcoin", f"localhost:{args.port}"]

    if args.showcurl: 
        print("CURL request: ", ' '.join(curl))
    
    print("---")

    captured = subprocess.run(curl, capture_output=True)
    
    if captured.returncode != 0:
        print("Error connecting with the bitcoin nodes (are they running ?):")
        prettyprint(captured.stderr, depth=args.depth)
        exit()

    response_json = json.loads(captured.stdout)

    if 'error' in response_json and response_json['error']:
        result = response_json["error"]["message"]
        prettyprint(result, depth=args.depth)
        exit()

    if args.filter:
        result = filter(response_json["result"], args.filter)
        prettyprint(result, depth=args.depth)
    else:
        prettyprint(response_json["result"], depth=args.depth)
    