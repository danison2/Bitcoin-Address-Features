# Bitcoin-Address-Features
The dataset consists of 100000 addresses: 50000 addresses were reported by users while the remaining were not found in reported addresses on BitcoinAbuse.com (until  28-02-2023). Every row corresponds to features of one address. 

Address Features:

Total number of transactions

Number of transactions returned by the API
Total amount sent

Total amount received

Number of unredeemed outputs: number of transactions with unspent outputs

Current balance

Total number of addresses to which the address sent coins

Total number of addresses from which the address received coins

Number of unique addresses to which the address sent coins

Number of unique addresses from which the address received coins

Average number of addresses in the address’s transaction input

Average number of addresses in the address’s transaction output

Total transaction fee from all transactions
Average transaction fee

Address PageRank score in the transaction graph

Average clustering for the address transaction graph

The address column has been omitted, only their features are provided. Some reported addresses (with a 1 in the Reported column) have no transaction resulting in similar features. A version in which similar features have been removed is included.

If you use the dataset, cite: Kamuhanda, D., Vallarano, N., Cui, M., &amp; Tessone, C. J. (2023). Benchmarking Machine Learning Models for Illegal Bitcoin Address Detection. ChainScience 2023.
