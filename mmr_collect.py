"""
This project is for balancing teams of champions and obtaining their objective rank.
WhatIsMyMMR public API is used to obtaining MMR of each player.
MMR of each player is the better of Ranked and Normal Queue MMR.

Make sure to check for invalid MMRs and manually add an value.
Visit na.whatismymmr.com to manually calculate an invalid mmr.

Created and Maintained by Alex Malao.
"""
import csv
import numpy as np
import requests
import time
import json

# Global Constants - Update as necessary
INVALID = 'INVALID: UPDATE'  # the default value written for invalid summoners
REGION = 'na'
norm_ranked_offset = 300  # mmr range varies by queue, difference between ranked solo and normal

# Global Constants - Do Not Update
DATA_DIR = 'data/'
DATA = 'data'
DATA_MMR = 'data_mmr'
COL_SUMMONER = 'Summoner Name'
COL_MMR = 'Best MMR'
HEADERS = {'User-Agent': 'python-requests:neu.league-team-maker:v1.0.0'}
MMR_API = f'https://{REGION}.whatismymmr.com/api/v1/summoner?name='

print('change from main')

print("Reading in from data/data.csv.")


print('debug message')
print('adding extra lines and changes')


# read in the data from data
summoners = np.genfromtxt(f'{DATA_DIR}{DATA}.csv', delimiter=',', dtype=str)
if len(summoners) < 1:
    raise ValueError('Input data should be populated with column names.')
# set the final column for mmr
summoners = np.c_[summoners, np.zeros(len(summoners))]
summoners[0][len(summoners[0]) - 1] = COL_MMR

# obtain the column names, stored by index
column_dict = {}
for i in range(len(summoners[0])):
    column_dict[summoners[0][i]] = i

# checks the column name is in correctly
if COL_SUMMONER not in column_dict.keys():
    raise NameError(f'Input columns must have the name {COL_SUMMONER}')

# checks against WhatIsMyMMR API for summoner ranks
for i in range(1, len(summoners)):
    summoner_row = summoners[i]
    summoner_name = summoner_row[column_dict[COL_SUMMONER]]
    # clean out the row
    print('                                                                                     ', end='\r', flush=True)
    print(f'Looking for summoner {summoner_name} at index {i}...', end='\r', flush=True)
    format_name = summoner_name.replace(' ', '+')
    response = requests.get(MMR_API + format_name, headers=HEADERS)
    mmr_dict = response.json()

    mmr = 0
    # calculates highest mmr in normal/ranked
    if mmr_dict is None:
        raise ConnectionError(f'Request from API is not available.')
    elif mmr_dict.get('error'):
        print(f'WARN: Summoner {summoner_name}: {mmr_dict.get("error")}', flush=True)
        mmr = INVALID
    else:
        if mmr_dict.get('ranked', {}).get('avg'):
            mmr = mmr_dict.get('ranked').get('avg')
        if mmr_dict.get('normal', {}).get('avg'):
            mmr = max(mmr, mmr_dict.get('normal').get('avg') - norm_ranked_offset)
        if mmr == 0:
            mmr = INVALID

    summoner_row[len(summoner_row) - 1] = mmr

    time.sleep(1)

# write to output file
np.savetxt(f'{DATA_DIR}{DATA_MMR}.csv', summoners, fmt='%s', delimiter=',')
