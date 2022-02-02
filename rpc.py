

import json
import pprint
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--command")
parser.add_argument("-l", "--params", nargs="*")
parser.add_argument("-p", '--port', default=18400)
parser.add_argument("-d", '--depth', default=None, type=int)
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
    print("CURL request:", " ".join(curl))
    print("-----")
    captured = subprocess.run(curl, capture_output=True)
    response_json = json.loads(captured.stdout)
    if 'error' in response_json and response_json['error']:
        print(response_json['error']['message'])
    else:
        pprint.pprint(response_json, indent=2, depth=args.depth)
