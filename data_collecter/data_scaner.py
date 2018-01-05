import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_collecter.lol_info import region as region_info
from elasticsearch import Elasticsearch
import certifi

es = Elasticsearch(['https://0ba6135ae8b7ed9a9b63c138a33b86c7.us-west-2.aws.found.io'],
                   port=9243,
                   http_auth=('scanner', 'Aa123456123'),
                   use_ssl=True,
                   ca_certs=certifi.where())

def scan_match_id(region):
    result_array = []
    res = es.search(index = 'lol_match_data', body = {
                    "query": {
                        "match":{
                            "region": region_info.get_region_str_in_elasticsearch(region)
                        }
                    }},
                    scroll='1m',
                    filter_path=['_scroll_id', 'hits.hits._source.match_id'],
                    size='1000')
    print("starting scan match id of {0}".format(region))
    print("--- BATCH 0 -------------------------------------------------")
    if not 'hits' in res:
        print("no {0} data !".format(region))
        es.clear_scroll(scroll_id=res['_scroll_id'])
        return

    count = 0
    for data in res['hits']['hits']:
        result_array.append(data['_source']['match_id'])
        count += 1

    batch = 1
    while res['hits']['hits']:
        res = es.scroll(scroll_id=res['_scroll_id'], scroll='1m')
        print("--- BATCH {0} -------------------------------------------------".format(batch))
        batch += 1
        for data in res['hits']['hits']:
            result_array.append(data['_source']['match_id'])
            count += 1

    es.clear_scroll(scroll_id=res['_scroll_id'])

    path = os.path.join(os.path.abspath(os.curdir), "./history/pulled_match_ids_" + region + ".txt")
    file = open(path, "w+")
    for id in result_array:
        file.write(str(id) + '\n')
    print("{0} Total match numbers: {1}".format(region, count))

if __name__ == "__main__":
    # print(sys.path)
    scan_match_id("JP")
    scan_match_id("KR")
    scan_match_id("NA")
    scan_match_id("EUW")

