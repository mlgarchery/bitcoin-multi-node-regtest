Those exploration exercice should be done on a network of node running bitcoind with default config
(bitcoin.conf empty, or so).

Solution with

# After how many blocks is a mined coin considered mature ?

After 100 more block then the block it was mined.
Test it with the commands:
- `createwallet <mywallet>`
- `loadwallet <mywallet>` (if not alrdy loaded)
- `./bitcoin-cli -generate 100`

(-generate = getnewaddress + generatetoaddress)
it will generate 100 block and consider the fund to be the property of the new
address.

- `getbalances`
you ll see the fund as immature.
- `./bitcoin-cli -generate 1` 
generates one more block then recheck with gebalances: you now have 50BTC trusted.


# How is choosen the transactions order

## Guess: 
Given two transactions A and B where B spends an output of A:
- Both A and B may be included in the same block.
- A must precede B in the transaction list.

--- 
I am curious about unrelated transactions - how are they ordered? Surely a timestamp is insufficient? If it is a UUID, how is it ordered? – Angad

They don't need to be in a specific order, but some miners seem to keep them in the same order they selected them into the block, i.e. ordered by the transactions' fee rates paid. – Murch

see https://bitcoin.stackexchange.com/questions/23035/order-of-transactions-within-a-block

---
TODO: try to reproduce dependant transactions.

Create a wallet on node1:
- `./bitcoin-cli --rpcport=18401 createwallet nodewallet`

And a new addr in $ADDRTO:
- `getnewaddress`

it return the transaction id (txid), hexadecimal.
- `./bitcoin-cli -named sendtoaddress address=$ADDRTO amount=0.1 fee_rate=1`
4de5b666931d2fcb32a43275fb3484f03995c9fb331aba20b367000022bc1d8f

```
root@laptop:~# ./bitcoin-cli -named sendtoaddress address=$ADDRTO amount=25 fee_rate=1
5f2652bc87d40e451118fa3773976fa4852a2dc377b78c721c1d257f1ae837d3
```
- `getmempoolentry 5f2652bc87d40e451118fa3773976fa4852a2dc377b78c721c1d257f1ae837d3`

```
getmempooldescendants 5f2652bc87d40e451118fa3773976fa4852a2dc377b78c721c1d257f1ae837d3

[
]
```
getmempoolancestors also doesn't returns anything as the txs are not linked.

Mine a few block to be sure node1 as mature found.
Then
```
./bitcoin-cli --rpcport=18401 -named sendtoaddress address=$MINERADDR amount=3 fee_rate=1 
34bcee6c420d33c2ded063e0ccb585470d2fe0ce457c8405dbe46c7bec59dd1e
```

`getrawmempool`, 

- then send back some btc.

# What is the mempool max size
- `getmempoolinfo` on any node:
```
{
  "loaded": true,
  "size": 1,
  "bytes": 141,
  "usage": 1168,
  "total_fee": 0.00000141,
  "maxmempool": 300000000,
  "mempoolminfee": 0.00001000,
  "minrelaytxfee": 0.00001000,
  "unbroadcastcount": 0
}
```

300 millions transactions

# What about the mempool overflow risk ? how is it mitigated.

# J'ai deux transactions, qui ne peuvent pas être résolues dans le même bloc (deux transferts de coins). Comment leur validité est elle evaluée?

TODO

So Block 1 generate 50BTC and Block 2 generates 50BTC

Test this with `-generate` or `generatetoaddress`

# Je suis miner, et je veux pousser une transaction à moi avant celle d'une autre transaction présente dans la mempool, est ce que je peux le faire?

## GUESS: Yes. Of course supposing you mine before the other nodes.

TODO

# Peut on vérifier a posteriori que les transactions dans un bloc ont maximisé la quantité de fees? (une transaction porte elle la date à laquelle elle a été soumise à la mempool?)

```
root@laptop:~# ./bitcoin-cli getmempoolentry 34bcee6c420d33c2ded063e0ccb585470d2fe0ce457c8405dbe46c7bec59dd1e
{
  "fees": {
    "base": 0.00000141,
    "modified": 0.00000141,
    "ancestor": 0.00000141,
    "descendant": 0.00000141
  },
  "vsize": 141,
  "weight": 561,
  "fee": 0.00000141,
  "modifiedfee": 0.00000141,
  "time": 1644449305,
  "height": 203,
  "descendantcount": 1,
  "descendantsize": 141,
  "descendantfees": 141,
  "ancestorcount": 1,
  "ancestorsize": 141,
  "ancestorfees": 141,
  "wtxid": "6cc315d5b931ca5b4edd114d2fbad55e8967d1162eec2cdef59cb7cbe2203d63",
  "depends": [
  ],
  "spentby": [
  ],
  "bip125-replaceable": true,
  "unbroadcast": false
}
```

 **"time": 1644449305,** = 2/10/2022, 12:28:25 AM

`listtransactions` contains a timereceived field.
```
root@laptop:~# ./bitcoin-cli listtransactions
[
  {
    "address": "bcrt1q8xu6wkuw9mfx4rahfwpfp6vnp0axd6agv588zw",
    "category": "immature",
    "amount": 25.00000000,
    "label": "",
    "vout": 0,
    "confirmations": 9,
    "generated": true,
    "blockhash": "029c570d27d6e788b9ee0aab933b02a8a1d2a1106daff9524c046473791fcd93",
    "blockheight": 195,
    "blockindex": 0,
    "blocktime": 1644449303,
    "txid": "46fa6446981ef006a5598a3a14bb84eaa677d4c2526205dc716fc9108579cd87",
    "walletconflicts": [
    ],
    "time": 1644449288,
    "timereceived": 1644449288,
    "bip125-replaceable": "no"
  },
  ...
]
```

 --> so YES.

# Est ce que je peux écrire un texte arbitraire dans une transaction? J'ai un espace prévu pour un commentaire? Si oui, est il limité en taille?

TODO

Follow this article to better understand the transactions
https://developer.bitcoin.org/examples/transactions.html

# Quelles sont les attaques connues du protocol Bitcoin?