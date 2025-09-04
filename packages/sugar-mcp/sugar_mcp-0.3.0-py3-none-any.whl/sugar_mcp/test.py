
from sugar.chains import  BaseChain

limit = 500
skip = 0
with BaseChain() as chain:
    with chain.web3.batch_requests() as batcher:
        for i in range(0, 3):
            batcher.add(chain.sugar.functions.all(limit, skip))

        result = batcher.execute()
        print(result)
        skip += limit