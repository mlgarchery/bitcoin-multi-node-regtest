#! /usr/bin/python3

from ast import arg
import json
from os import rename
import pprint
import argparse
from readline import redisplay
import subprocess

from utils.filter import filter_dict

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--command")
parser.add_argument("-l", "--params", nargs="*", help="Space separated command list of params")
parser.add_argument("-p", "--port", default=18400, help="Target node port")
# General Options
parser.add_argument("-d", "--depth", default=None, type=int, help="Response json depth")
parser.add_argument("-f", "--filter", nargs="*", help="Filter the JSON response with multiple keyword.")
parser.add_argument("-s", "--showcurl", action="store_true", help="Show the curl request")

args = parser.parse_args()

if not args.params:
    args.params= []


if __name__ == '__main__':
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": "1",
        "method": args.command,
        "params": args.params
    })
    
    curl = ["curl", "-d", data, "-u", "bitcoin:bitcoin", f"localhost:{args.port}"]

    if args.showcurl: 
        print("CURL request: ", ' '.join(curl))
    
    print("---")

    captured = subprocess.run(curl, capture_output=True)
    
    if captured.returncode != 0:
        print("Error connecting with the bitcoin nodes (are they running ?):")
        print(captured.stderr)
        exit()

    response_json = json.loads(captured.stdout)

    print("Response:")

    if 'error' in response_json and response_json['error']:
        print(response_json['error']['message'])
        exit()

    if args.filter:
        results = []
        filter_dict(response_json, args.filter, results)
        for d in results:
            pprint.pprint(d, indent=2, depth=args.depth)
    else:
        pprint.pprint(response_json, indent=2, depth=args.depth)
