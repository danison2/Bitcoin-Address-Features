import requests
import networkx as nx
import itertools
import pandas as pd
from tqdm import tqdm
import time
from selenium import webdriver
import time
import json
from bs4 import BeautifulSoup


def get_address_features():
    # Set up the webdriver
    driver = webdriver.Chrome()

    output_path = 'data/addresses/address_features2.txt'

    header = ['address', 'n_tx', 'total_amount_sent', 'total_amount_received', 
                'final_balance', 'n_unredeemed', 'recent_n_tx', 
                'recent_sent_count', 'recent_receive_count', 'recent_sent_unique_count', 
                'recent_receive_unique_count', 'recent_avg_inputs', 'recent_avg_outputs', 'total_fee',
                'recent_avg_tx_fee', 'reported', 'report_count', 'addr_pagerank', 'avg_clustering']

    f = open(output_path, 'w+')
    for h in header:
        f.write(h + '\t')
    f.write("\n")
    f.close()

    #check if the address was not processed before
    # print("getting processed addresses...")
    processed_addresses = []
    # with open(output_path, 'r') as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         address = line.split('\t')[0].strip()
    #         processed_addresses.append(address)
    # print("Found {} processed addresses".format(len(processed_addresses)))

    df = pd.read_csv("data/addresses/filtered_records.csv", low_memory=False)

    for index, row in tqdm(df.iterrows()):
        address = row['Addresses'].strip()
        report_status = row['Reported']
        report_count = row['ReportCount']

        n_tx = 0
        total_received = 0
        total_sent = 0
        n_unredeemed = 0
        final_balance = 0
        recent_n_tx = 0

        total_fee = 0
        sent_count = 0
        rec_count = 0
        total_input = 0
        total_output = 0
        addr_pagerank = 0
        avg_clustering = 0

        G = nx.DiGraph()
        
        if address not in processed_addresses:
            try:
                url = f"https://blockchain.info/rawaddr/{address}"
                driver.get(url)

                # Wait for the page to load and the data to be rendered
                time.sleep(10)

                # Get the page source
                page_source = driver.page_source

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                pre = soup.find('pre')
                transactions = json.loads(pre.text)

                n_tx = transactions['n_tx']
                total_received = transactions['total_received']
                total_sent = transactions['total_sent']
                n_unredeemed = transactions['n_unredeemed']
                final_balance = transactions['final_balance']
                txs = transactions['txs']
                recent_n_tx = len(txs)

                if recent_n_tx > 0:
                    for i, tx in enumerate(txs):
                        # Extract the input addresses
                        input_addresses = [tx_input["prev_out"]["addr"] for tx_input in tx["inputs"] if "addr" in tx_input["prev_out"]]
                        # Extract the output addresses
                        output_addresses = [output["addr"] for output in tx["out"] if "addr" in output]

                        # Add the input and output addresses as nodes
                        G.add_nodes_from(input_addresses)
                        G.add_nodes_from(output_addresses)

                        tx_edges = list(itertools.product(input_addresses, output_addresses))
                        G.add_edges_from(tx_edges)

                        if 'fee' in tx:
                            total_fee += tx['fee']
                        if address in input_addresses:
                            sent_count += 1
                        if address in output_addresses:
                            rec_count += 1

                        total_input += len(input_addresses)
                        total_output += len(output_addresses)

                    addr_pagerank = nx.pagerank(G, alpha=0.9)[address]
                    avg_clustering = nx.average_clustering(G)

                else:
                    print(f"Address {address} has no transactions")
            except:
                print(f"Server error for address: {address}")
                pass
            
        else:
            pass

        result = {}
        result['address'] = address
        result['n_tx'] = n_tx
        result['total_received'] = total_received
        result['total_sent'] = total_sent
        result['n_unredeemed'] = n_unredeemed
        result['final_balance'] = final_balance
        result['recent_n_tx'] = recent_n_tx
        result['recent_sent_count'] = sent_count
        result['recent_receive_count'] = rec_count
        result['recent_sent_unique_count'] = G.out_degree(address) if recent_n_tx > 0 else 0
        result['recent_receive_unique_count'] = G.in_degree(address) if recent_n_tx > 0 else 0
        result['recent_avg_inputs'] = total_input/recent_n_tx if recent_n_tx > 0 else 0
        result['recent_avg_outputs'] = total_output/recent_n_tx if recent_n_tx > 0 else 0
        result['total_fee'] = total_fee
        result['recent_avg_tx_fee'] = total_fee/recent_n_tx if recent_n_tx > 0 else 0
        result['addr_pagerank'] = addr_pagerank
        result['avg_clustering'] = avg_clustering

        row = [address, result['n_tx'], result['total_sent'], result['total_received'],
                            result['final_balance'], result['n_unredeemed'], result['recent_n_tx'],
                            result['recent_sent_count'], result['recent_receive_count'],result['recent_sent_unique_count'], 
                            result['recent_receive_unique_count'], result['recent_avg_inputs'], result['recent_avg_outputs'],
                            result['total_fee'], result['recent_avg_tx_fee'], report_status, report_count,
                            result['addr_pagerank'],result['avg_clustering']
                            ]
        with open(output_path, 'a') as f:
            for r in row:
                f.write(str(r) + '\t')
            f.write('\n')
            f.close()



def get_address_features_api():

    output_path = 'data/addresses/address_features.txt'

    # header = ['address', 'n_tx', 'total_amount_sent', 'total_amount_received', 
    #             'final_balance', 'n_unredeemed', 'recent_n_tx', 
    #             'recent_sent_count', 'recent_receive_count', 'recent_sent_unique_count', 
    #             'recent_receive_unique_count', 'recent_avg_inputs', 'recent_avg_outputs', 'total_fee',
    #             'recent_avg_tx_fee', 'reported', 'report_count', 'addr_pagerank', 'avg_clustering']
    f = open(output_path, 'a')
    # for h in header:
    #     f.write(h + '\t')
    f.write("\n\n")
    f.close()

    #check if the address was not processed before
    print("getting processed addresses...")
    processed_addresses = []
    with open(output_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line_array = line.split('\t')
            if len(line_array) > 2:
                address = line.split('\t')[0].strip()
                report_count = line.split('\t')[16].strip()
                processed_addresses.append(address + ":" + str(report_count))
    print("Found {} processed addresses".format(len(processed_addresses)))

    df = pd.read_csv("data/addresses/filtered_records.csv", low_memory=False)

    for index, row in tqdm(df.iterrows()):
        address = row['Addresses'].strip()
        report_status = row['Reported']
        report_count = row['ReportCount']

        n_tx = 0
        total_received = 0
        total_sent = 0
        n_unredeemed = 0
        final_balance = 0
        recent_n_tx = 0

        total_fee = 0
        sent_count = 0
        rec_count = 0
        total_input = 0
        total_output = 0
        addr_pagerank = 0
        avg_clustering = 0

        G = nx.DiGraph()
        address_with_report = address + ":" + str(report_count)
        
        if address_with_report not in processed_addresses:
            try:
                url = f"https://blockchain.info/rawaddr/{address}"
                response = requests.get(url)

                # Wait for the page to load and the data to be rendered
                time.sleep(10)

                transactions = response.json()

                n_tx = transactions['n_tx']
                total_received = transactions['total_received']
                total_sent = transactions['total_sent']
                n_unredeemed = transactions['n_unredeemed']
                final_balance = transactions['final_balance']
                txs = transactions['txs']
                recent_n_tx = len(txs)

                if recent_n_tx > 0:
                    for i, tx in enumerate(txs):
                        # Extract the input addresses
                        input_addresses = [tx_input["prev_out"]["addr"] for tx_input in tx["inputs"] if "addr" in tx_input["prev_out"]]
                        # Extract the output addresses
                        output_addresses = [output["addr"] for output in tx["out"] if "addr" in output]

                        # Add the input and output addresses as nodes
                        G.add_nodes_from(input_addresses)
                        G.add_nodes_from(output_addresses)

                        tx_edges = list(itertools.product(input_addresses, output_addresses))
                        G.add_edges_from(tx_edges)

                        if 'fee' in tx:
                            total_fee += tx['fee']
                        if address in input_addresses:
                            sent_count += 1
                        if address in output_addresses:
                            rec_count += 1

                        total_input += len(input_addresses)
                        total_output += len(output_addresses)

                    addr_pagerank = nx.pagerank(G, alpha=0.9)[address]
                    avg_clustering = nx.average_clustering(G)

                else:
                    print(f"Address {address} has no transactions")
            except:
                print(f"Server error for address: {address}")
                pass
            
        else:
            pass

        result = {}
        result['address'] = address
        result['n_tx'] = n_tx
        result['total_received'] = total_received
        result['total_sent'] = total_sent
        result['n_unredeemed'] = n_unredeemed
        result['final_balance'] = final_balance
        result['recent_n_tx'] = recent_n_tx
        result['recent_sent_count'] = sent_count
        result['recent_receive_count'] = rec_count
        result['recent_sent_unique_count'] = G.out_degree(address) if recent_n_tx > 0 else 0
        result['recent_receive_unique_count'] = G.in_degree(address) if recent_n_tx > 0 else 0
        result['recent_avg_inputs'] = total_input/recent_n_tx if recent_n_tx > 0 else 0
        result['recent_avg_outputs'] = total_output/recent_n_tx if recent_n_tx > 0 else 0
        result['total_fee'] = total_fee
        result['recent_avg_tx_fee'] = total_fee/recent_n_tx if recent_n_tx > 0 else 0
        result['addr_pagerank'] = addr_pagerank
        result['avg_clustering'] = avg_clustering

        row = [address, result['n_tx'], result['total_sent'], result['total_received'],
                            result['final_balance'], result['n_unredeemed'], result['recent_n_tx'],
                            result['recent_sent_count'], result['recent_receive_count'],result['recent_sent_unique_count'], 
                            result['recent_receive_unique_count'], result['recent_avg_inputs'], result['recent_avg_outputs'],
                            result['total_fee'], result['recent_avg_tx_fee'], report_status, report_count,
                            result['addr_pagerank'],result['avg_clustering']
                            ]
        with open(output_path, 'a') as f:
            for r in row:
                f.write(str(r) + '\t')
            f.write('\n')
            f.close()



def get_address_transaction_stats(address):
    n_tx = 0
    total_received = 0
    total_sent = 0
    n_unredeemed = 0
    final_balance = 0
    recent_n_tx = 0

    total_fee = 0
    sent_count = 0
    rec_count = 0
    total_input = 0
    total_output = 0
    addr_pagerank = 0
    avg_clustering = 0

    G = nx.DiGraph()

    response = requests.get(f"https://blockchain.info/rawaddr/{address}")

    time.sleep(5)
   
    if response.status_code == 200 and response.content:
        transactions = response.json()
        n_tx = transactions['n_tx']
        total_received = transactions['total_received']
        total_sent = transactions['total_sent']
        n_unredeemed = transactions['n_unredeemed']
        final_balance = transactions['final_balance']
        txs = transactions['txs']
        recent_n_tx = len(txs)

        if recent_n_tx > 0:
            for i, tx in enumerate(txs):
                # Extract the input addresses
                input_addresses = [tx_input["prev_out"]["addr"] for tx_input in tx["inputs"] if "addr" in tx_input["prev_out"]]
                # Extract the output addresses
                output_addresses = [output["addr"] for output in tx["out"] if "addr" in output]

                # Add the input and output addresses as nodes
                G.add_nodes_from(input_addresses)
                G.add_nodes_from(output_addresses)

                tx_edges = list(itertools.product(input_addresses, output_addresses))
                G.add_edges_from(tx_edges)

                if 'fee' in tx:
                    total_fee += tx['fee']
                if address in input_addresses:
                    sent_count += 1
                if address in output_addresses:
                    rec_count += 1

                total_input += len(input_addresses)
                total_output += len(output_addresses)

            addr_pagerank = nx.pagerank(G, alpha=0.9)[address]
            avg_clustering = nx.average_clustering(G)

        else:
            print(f"Address {address} has no transactions")

    
    else:
        print(f"Request to {address} returned a non-200 status code or empty content")
    
    result = {}
    result['address'] = address
    result['n_tx'] = n_tx
    result['total_received'] = total_received
    result['total_sent'] = total_sent
    result['n_unredeemed'] = n_unredeemed
    result['final_balance'] = final_balance
    result['recent_n_tx'] = recent_n_tx
    result['recent_sent_count'] = sent_count
    result['recent_receive_count'] = rec_count
    result['recent_sent_unique_count'] = G.out_degree(address) if recent_n_tx > 0 else 0
    result['recent_receive_unique_count'] = G.in_degree(address) if recent_n_tx > 0 else 0
    result['recent_avg_inputs'] = total_input/recent_n_tx if recent_n_tx > 0 else 0
    result['recent_avg_outputs'] = total_output/recent_n_tx if recent_n_tx > 0 else 0
    result['recent_avg_tx_fee'] = total_fee/recent_n_tx if recent_n_tx > 0 else 0
    result['addr_pagerank'] = addr_pagerank
    result['avg_clustering'] = avg_clustering

    return result



def main():
 
    # Define the header row as a list
    header = ['address', 'n_tx', 'total_amount_sent', 'total_amount_received', 
            'final_balance', 'n_unredeemed', 'recent_n_tx', 
            'recent_sent_count', 'recent_receive_count', 'recent_sent_unique_count', 
            'recent_receive_unique_count', 'recent_avg_inputs', 'recent_avg_outputs',
            'recent_avg_tx_fee', 'reported', 'report_count', 'addr_pagerank', 'avg_clustering']
    # Append the header row to the worksheet
    output_path = 'data/addresses/address_features.txt'
    f = open(output_path, 'w+')
    for h in header:
        f.write(h + '\t')
    f.write("\n")
    f.close()

    #check if the address was not processed before
    print("getting processed addresses...")
    processed_addresses = []
    with open(output_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            address = line.split('\t')[0].strip()
            processed_addresses.append(address)


    df = pd.read_csv("data/addresses/filtered_records.csv", low_memory=False)

    for index, row in df.iterrows():
        address = row['Addresses'].strip()
        report_status = row['Reported']
        report_count = row['ReportCount']
        # do something with the values
        if address not in processed_addresses:
            result = get_address_transaction_stats(address)
            if index < 2:
                print(result)
            row = [address, result['n_tx'], result['total_sent'], result['total_received'],
                            result['final_balance'], result['n_unredeemed'], result['recent_n_tx'],
                            result['recent_sent_count'], result['recent_receive_count'],result['recent_sent_unique_count'], 
                            result['recent_receive_unique_count'], result['recent_avg_inputs'], result['recent_avg_outputs'],
                            result['recent_avg_tx_fee'], report_status, report_count,
                            result['addr_pagerank'],result['avg_clustering']
                            ]
            with open(output_path, 'a') as f:
                for r in row:
                    f.write(str(r) + '\t')
                f.write('\n')
                f.close()
            time.sleep(5)
        else:
            pass
   
# get_address_features()
get_address_features_api()







