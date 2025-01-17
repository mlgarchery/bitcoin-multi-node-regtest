## Requirements

You need `docker` and `docker-compose` to be installed on your machine.

# Multinode / Multiwallet Bitcoin regtest network

This repository allows you run a full bitcoin network in an isolated environment. It uses bitcoin's regtest capability to setup an isolated bitcoin network, and then uses docker to setup a network with 3 nodes.

This is useful because normally in regtest mode you would generate all coins in the same wallet as where you'd send the coins. With this setup, you can use one node to generate the coins and then send it to one of the other nodes, which can then again send it to another node to simulate more real-life bitcoin usage.

## Usage

Simple run

`docker-compose up`

to start all the containers. This will start the bitcoin nodes, and expose RPC on all of them. The nodes will run on the following ports:

| Node | P2P port  | **RPC port** |
| --- | --- | --- |
| miner1_bitcoin | 18500 | **18400**| 
| node1_bitcoin | 18501 | **18401** | 
| node2_bitcoin | 18502 | **18402** | 

\* Port as exposed on the host running docker.

## Use bitcoin-cli

Exec any [rpc command](https://developer.bitcoin.org/reference/rpc/index.html)

Do:
```
docker-compose up
```
then connect to the client
```
docker run --net=host -it client_bitcoin
```

From there you can exec command, examples:
```
./bitcoin-cli getblockchaininfo
```

```
root@laptop:/# ./bitcoin-cli getpeerinfo | jq ".[]|{addr, addrbind}"
```
the "jq .." part is just a easy way to filter the json response see https://jqplay.org/.

If you want to request the node1 on port 18401 (by default its the miner node on 18400).
```
./bitcoin-cli --rpcport=18401 getblockchaininfo 
```

With an argument:
```
./bitcoin-cli sendtoaddress $ADDR 1
```
With named arguments:
```
./bitcoin-cli -named sendtoaddress address=$ADDR amount=1 fee_rate=1
```


## Transactions

### Initial block count

Check that the initial block count is 0.

```
getblockcount

{'error': None, 'id': '1', 'result': 0}
```

### Check connected nodes

Check the "miner" node is connected to other nodes.

```
getpeerinfo | jq ".[]|{addr, inbound}"

{'addr': '172.18.0.3:42586', 'inbound': True}
{'addr': 'node2:18444', 'inbound': False}
{'addr': '172.18.0.4:54714', 'inbound': True}
{'addr': 'node1:18444', 'inbound': False}
```

### Mine some blocks and see other nodes are updating their block count

```
# create a wallet
createwallet newwallet

{'mine': {'immature': 0.0, 'trusted': 0.0, 'untrusted_pending': 0.0}}
```

```
# check wallet balances
 getbalance

0.0
```

```
# get a new address
 getnewaddress

bcrt1qvg0g3guc9ljxl7fg2w4sgl08kupk2nrrlrz9dv

$ NEW_ADDRESS=bcrt1qvg0g3guc9ljxl7fg2w4sgl08kupk2nrrlrz9dv
```

Use the `generatetoaddress` cmd to mine a block and send the BTC to the specified address
```
generatetoaddress nblocks "address" ( maxtries )

Mine blocks immediately to a specified address (before the RPC call returns)

Arguments:
1. nblocks     (numeric, required) How many blocks are generated immediately.
2. address     (string, required) The address to send the newly generated bitcoin to.
3. maxtries    (numeric, optional, default=1000000) How many iterations to try.

Result:
[           (json array) hashes of blocks generated
  "hex",    (string) blockhash
  ...
]
```
```
generatetoaddress 1 $NEW_ADDRESS 

721beabd06276757967d00bf4d2f7fac3d82bd0005ff0c37a6e14d11d394d91d
```
Check if the other nodes synced the new block:
```
getblockcount -p 18401

1
```

```
getbalances

{
  "mine": {
    "trusted": 0.00000000,
    "untrusted_pending": 0.00000000,
    "immature": 50.00000000
  }
}
```
Our fund is *immature* cause not enough blocks are after it (the current length of the blockchain known by the node is not sufficiently long) 


Create a new wallet on node1, and a new address. Save its public key in a variable.
```
root@laptop:/# ./bitcoin-cli --rpcport=18401 createwallet node1wallet
{
  "name": "node1wallet",
  "warning": ""
}
```
```
root@laptop:/# ./bitcoin-cli --rpcport=18401 getnewaddress
bcrt1qjvrh5vkqnlplndualacu4jtl7fm7dc7sc6p0ta
root@laptop:/# NODE1_ADDRESS=bcrt1qjvrh5vkqnlplndualacu4jtl7fm7dc7sc6p0ta
```

Don't forget the *-named* parameter:
```
root@laptop:/# ./bitcoin-cli -named sendtoaddress address=$NODE1_ADDRESS amount=0.5 fee_rate=25
error code: -6
error message:
Insufficient funds
```

See TD.md for more.


## OLD (to refactor)

### Send bitcoin from miner to another node

Now we're going to generate an address in another node. Note that we use port **18401** (node1) instead of 18400:
```
# Mine blocks first
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"generate","params":[101]}' -u bitcoin:bitcoin -s localhost:18400
{"result":["2929287f219fda71445219269081364373b4bdec73187da92126150feac39cd6",
... <snip> ..., 
"2b1ffc0528fac9e759097a9213198b1c8540545b67ea1dc4c0ca68b76f02f8f1"],"error":null,"id":"1"}

# Check balance
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getbalance","params":[]}' -u bitcoin:bitcoin -s localhost:18400
{"result":50.00000000,"error":null,"id":"1"}

# Generate address on node1
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getnewaddress","params":[]}' -u bitcoin:bitcoin -s localhost:18401
{"result":"2N444M93zqwyhhFSDJxgzPL5h9XMdwLUibz","error":null,"id":"1"}

# Send from miner to node1
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"sendtoaddress","params":["2N444M93zqwyhhFSDJxgzPL5h9XMdwLUibz", "3.14"]}' -u bitcoin:bitcoin -s localhost:18400
{"result":"008f138f10e80aaae2a5211bf2891ad522a1dd7b85d3f26cbbdabfa63c60ced0","error":null,"id":"1"}

# Now, since the block was not yet mined, we usually don't see the balance yet, unless  we specify 0 confirmations.
# First with the default (1) confirmation:
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getbalance","params":[]}' -u bitcoin:bitcoin -s localhost:18401
{"result":0.00000000,"error":null,"id":"1"}

# No coins, so let's try 0 confirmations (the first parameter "" means default account)
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getbalance","params":["", 0]}' -u bitcoin:bitcoin -s localhost:18401
{"result":3.14000000,"error":null,"id":"1"}

# This also means that node1 has it in the mempool, which shows there is exactly one transaction in it
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getmempoolinfo","params":[]}' -u bitcoin:bitcoin -s localhost:18401 | jq .
{
  "result": {
    "size": 1,
    "bytes": 187,
    "usage": 1024,
    "maxmempool": 300000000,
    "mempoolminfee": 1e-05,
    "minrelaytxfee": 1e-05
  },
  "error": null,
  "id": "1"
}

# Finally, let's mine the block and see that getbalance will show the balance by default.
# node1:
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getbalance","params":[]}' -u bitcoin:bitcoin -s localhost:18401
{"result":3.14000000,"error":null,"id":"1"}

# miner
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getbalance","params":[]}' -u bitcoin:bitcoin -s localhost:18400
{"result":96.85996240,"error":null,"id":"1"}

# Some extras

# List wallet affecting transactions:
# miner
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"listtransactions","params":["", 150]}' -u bitcoin:bitcoin -s localhost:18400 | jq '.result [] | {amount, confirmations, txid, category}'
{
  "amount": 50,
  "confirmations": 102,
  "txid": "7bd5b1c805dc1ec6eab533242f56c0685c713c709e7f3e7cec858773163c7d48",
  "category": "generate"
}
{
  "amount": 50,
  "confirmations": 101,
  "txid": "d32be1fce3dd33cb46701cfcaf9de1ddfde9e18dcbe35984799b6341e38a9c53",
  "category": "generate"
}
<snip>
{
  "amount": 50,
  "confirmations": 3,
  "txid": "2e3922018911136f8474f741956e45f24fd1d100908bee059aacaaf5d815d4b6",
  "category": "immature"
}
{
  "amount": 50,
  "confirmations": 2,
  "txid": "e328e32106d04121ab32300c5e35b3880a21ab3ebecd6c7af34417278bf2da49",
  "category": "immature"
}
{
  "amount": -3.14,
  "confirmations": 1,
  "txid": "008f138f10e80aaae2a5211bf2891ad522a1dd7b85d3f26cbbdabfa63c60ced0",
  "category": "send"
}
{
  "amount": 50.0000376,
  "confirmations": 1,
  "txid": "dafe13b91d80fd899e627fb481c22bdd10f9d2da13c55ec0b7af7f30175ce96c",
  "category": "immature"
}

# node1
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"listtransactions","params":["", 150]}' -u bitcoin:bitcoin -s localhost:18401 | jq '.result [] | {amount, confirmations, txid, category}'
{
  "amount": 3.14,
  "confirmations": 1,
  "txid": "008f138f10e80aaae2a5211bf2891ad522a1dd7b85d3f26cbbdabfa63c60ced0",
  "category": "receive"
}

# node2
root@ubuntu-xenial:/home/vag
importaddress "address" ( "label" rescan p2sh )
importdescriptors "requests"
importmulti "requests" ( "options" )
importprivkey "privkey" ( "label" rescan )
importprunedfunds "rawtransaction" "txoutproof"
importpubkey "pubkey" ( "label" rescan )
importwallet "filename"
keypoolrefill ( newsize )
listaddressgroupings
listdescriptors
listlabels ( "purpose" )
listlockunspent
listreceivedbyaddress ( minconf include_empty include_watchonly "address_filter" )
listreceivedbylabel ( minconf include_empty include_watchonly )
listsinceblock ( "blockhash" target_confirmations include_watchonly include_removed )
listtransactions ( "label" count skip include_watchonly )
listunspent ( minconf maxconf ["address",...] include_unsafe query_options )
listwalletdir
listwallets
loadwallet "filename" ( load_on_startup )
lockunspent unlock ( [{"txid":"hex","vout":n},...] )
psbtbumpfee "txid" ( options )
removeprunedfunds "txid"
rescanblockchain ( start_height stop_height )
send [{"address":amount,...},{"data":"hex"},...] ( conf_target "estimate_mode" fee_rate options )
sendmany "" {"address":amount,...} ( minconf "comment" ["address",...] replaceable conf_target "estimate_mode" fee_rate verbose )
sendtoaddress "address" amount ( "comment" "comment_to" subtractfeefromamount replaceable conf_target "estimate_mode" avoid_reuse fee_rate verbose )
sethdseed ( newkeypool "seed" )
setlabel "address" "label"
settxfee amount
setwalletflag "flag" ( value )
signmessage "address" "message"
signrawtransactionwithwallet "hexstring" ( [{"txid":"hex","vout":n,"scriptPubKey":"hex","redeemScript":"hex","witnessScript":"hex","amount":amount},...] "sighashtype" )
unloadwallet ( "wallet_name" load_on_startup )
upgradewallet ( version )
walletcreatefundedpsbt ( [{"txid":"hex","vout":n,"sequence":n},...] ) [{"address":amount,...},{"data":"hex"},...] ( locktime options bip32derivs )
walletdisplayaddress bitcoin address to display
walletlock
walletpassphrase "passphrase" timeout
walletpassphrasechange "oldpassphrase" "newpassphrase"
walletprocesspsbt "psbt" ( sign "sighashtype" bip32derivs )

== Zmq ==
getzmqnotifications
d":"1"}

# Try getting the transaction
# node1:
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"gettransaction","params":["008f138f10e80aaae2a5211bf2891ad522a1dd7b85d3f26cbbdabfa63c60ced0"]}' -u bitcoin:bitcoin -s localhost:18401 | jq .
{
  "result": {
    "amount": 3.14,
    "confirmations": 1,
    "blockhash": "00f3b3923a14a69a78a419660e20d63a4f91370d6099c3bbbdc5daad953e2985",
    "blockindex": 1,
    "blocktime": 1523421980,
    "txid": "008f138f10e80aaae2a5211bf2891ad522a1dd7b85d3f26cbbdabfa63c60ced0",
    "walletconflicts": [],
    "time": 1523421666,
    "timereceived": 1523421666,
    "bip125-replaceable": "no",
    "details": [
      {
        "account": "",
        "address": "2N444M93zqwyhhFSDJxgzPL5h9XMdwLUibz",
        "category": "receive",
        "amount": 3.14,
        "label": "",
        "vout": 0
      }
    ],
    "hex": "0200000001487d3c16738785ec7c3e7f9e703c715c68c0562f2433b5eac61edc05c8b1d57b0000000048473044022065b2d5c649bb6882f73654398ebaa9bf29281088493ad56f1ee0400bfcbeb8b30220402fea8148de73c14ba332693f7d5c9e2f2bf4332299a2df87115fdabaf1607b01feffffff028042b7120000000017a914768cc2b85515737b398e2613fd7fe9c3d44f73f187d0a04e170100000017a9146a82eef49043551afd83cb286d801c0725ba24318765000000"
  },
  "error": null,
  "id": "1"
}

# node2, here it fails because that transaction is not in the wallet.
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"gettransaction","params":["008f138f10e80aaae2a5211bf2891ad522a1dd7b85d3f26cbbdabfa63c60ced0"]}' -u bitcoin:bitcoin -s localhost:18402 | jq .
{
  "result": null,
  "error": {
    "code": -5,
    "message": "Invalid or non-wallet transaction id"
  },
  "id": "1"
}

# however, using `getrawtransaction` on node2 does actually return it
root@ubuntu-xenial:/home/vagrant/bitcoin-docker# curl -d '{"jsonrpc":"2.0","id":"1","method":"getrawtransaction","params":["0c0bd722bc5534ec715e31c70e913e887dcdf6cf15438ed890c1a5b56a631d65", true]}' -u bitcoin:bitcoin -s localhost:18402
{"result":{"txid":"0c0bd722bc5534ec715e31c70e913e887dcdf6cf15438ed890c1a5b56a631d65","hash":"0c0bd722bc5534ec715e31c70e913e887dcdf6cf15438ed890c1a5b56a631d65","version":2,"size":188,"vsize":188,"locktime":101,"vin":[{"txid":"75aa43e3c1f2e4094190339b1d7aa605e06cd5a6fe68db1fcc23ff2f1b54d57d","vout":0,"scriptSig":{"asm":"304502210093f7c7b47eff76fc0e4926bb10942bfb90c8d9f5dc430dd0cb0a191908191cb10220522bcc869bd8fa44e5f8d865c8988da53ae875a05ae3fa3cabe2cf5fe1aa0310[ALL]","hex":"48304502210093f7c7b47eff76fc0e4926bb10942bfb90c8d9f5dc430dd0cb0a191908191cb10220522bcc869bd8fa44e5f8d865c8988da53ae875a05ae3fa3cabe2cf5fe1aa031001"},"sequence":4294967294}],"vout":[{"value":3.14000000,"n":0,"scriptPubKey":{"asm":"OP_HASH160 d5044b6ca6c83a0d0f182dc1f939285d7650bae4 OP_EQUAL","hex":"a914d5044b6ca6c83a0d0f182dc1f939285d7650bae487","reqSigs":1,"type":"scripthash","addresses":["2NCfZ4YFssjjGp5xQjnDMKLFRy8XP4W4TYo"]}},{"value":46.85996240,"n":1,"scriptPubKey":{"asm":"OP_HASH160 b11e110167018be58797913289c0747e1b916879 OP_EQUAL","hex":"a914b11e110167018be58797913289c0747e1b91687987","reqSigs":1,"type":"scripthash","addresses":["2N9PjcHmezjNzi4KAuj1ajKVACYmM7CWw3m"]}}],"hex":"02000000017dd5541b2fff23cc1fdb68fea6d56ce005a67a1d9b33904109e4f2c1e343aa75000000004948304502210093f7c7b47eff76fc0e4926bb10942bfb90c8d9f5dc430dd0cb0a191908191cb10220522bcc869bd8fa44e5f8d865c8988da53ae875a05ae3fa3cabe2cf5fe1aa031001feffffff028042b7120000000017a914d5044b6ca6c83a0d0f182dc1f939285d7650bae487d0a04e170100000017a914b11e110167018be58797913289c0747e1b9168798765000000","blockhash":"1d5df158d1aecf18b893a0f5cd91fe782a0f8b53b028fff3b5892ff9beaf7134","confirmations":101,"time":1523422840,"blocktime":1523422840},"error":null,"id":"1"}
```