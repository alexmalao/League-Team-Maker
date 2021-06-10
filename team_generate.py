"""
This project is for balancing teams of champions and obtaining their objective rank.
This file will use the MMR manually determined or obtained from the WhatIsMyMMR API.
Teams will be determined by average MMR, balancing regardless of role preference.

Duo queue partners are currently not supported, however players may be manually swapped around with similar MMR.

Created and Maintained by Alex Malao.
"""
import copy
import csv
import numpy as np
import random
import itertools

# Global Constants - Update as necessary
TOTAL_PERM = 1000000  # the amount of randomized teams for generally obtaining the best team
TOTAL_SWAP = 250000  # the amount of swapped player checks after permutations are calculated

# Global Constants - Do not update unless you know what you are doing
DATA_DIR = 'data/'
DATA_MMR = 'data_mmr'
BEST_TEAMS = 'best_teams'
COL_MMR = 'Best MMR'
COL_TEAM = 'Team Number'
COL_TEAM_MMR = 'Team MMR'
COL_ROLE = 'Assigned Role'
# middle2 is better than jungle
ROLE_LIST = ['top', 'jungle', 'middle', 'bottom', 'support', 'middle2']
TEAM_SIZE = 5
ROLE_PREF_MAX = 5


# read in data from data_mmr
summoners = np.genfromtxt(f'{DATA_DIR}{DATA_MMR}.csv', delimiter=',', dtype=str)
if len(summoners) < 1:
    raise ValueError('Input data should be populated with column names.')
# set the final columns for team number and assigned role
summoners = np.c_[summoners, np.zeros(len(summoners)), np.zeros(len(summoners)), np.zeros(len(summoners))]
summoners[0][len(summoners[0]) - 1] = COL_ROLE
summoners[0][len(summoners[0]) - 2] = COL_TEAM_MMR
summoners[0][len(summoners[0]) - 3] = COL_TEAM

# obtain the column names, stored by index
column_dict = {}
for i in range(len(summoners[0])):
    column_dict[summoners[0][i]] = i


# ensure the amount of players are divisible by TEAM_SIZE
if len(summoners) % TEAM_SIZE != 1 or len(summoners) <= TEAM_SIZE:
    raise ValueError(f'There are not enough players to form teams of {TEAM_SIZE}.')

# find average mmr from total mmr
total_players = len(summoners) - 1
total_mmr = 0
# ensure all MMR values are populated
for i in range(1, len(summoners)):
    try:
        total_mmr += int(summoners[i][column_dict[COL_MMR]])
    except ValueError:
        raise ValueError(f'MMR for row {i} does not have an integer value. Did you forget to look at the data?')

avg_mmr = int(total_mmr / total_players)
print(f'Average MMR: {avg_mmr}')

# step 1: try random permutations and store the best possible one
# uses least squared error
player_indices = range(1, len(summoners))
# smallest value is best here
best_sq_avg = float('inf')
best_order = []
print(f'Trying {TOTAL_PERM} permutations...', flush=True)
for x in range(TOTAL_PERM):
    rand_team = random.sample(player_indices, total_players)

    # keep track of the team
    squared_avg = 0
    team_mmr = 0
    for i in range(total_players):
        team_mmr += int(summoners[rand_team[i]][column_dict[COL_MMR]])
        if i % TEAM_SIZE == TEAM_SIZE - 1:
            squared_avg += (int(team_mmr / 5) - avg_mmr) ** 2
            team_mmr = 0

    # replace with the best teams
    if squared_avg < best_sq_avg:
        best_sq_avg = squared_avg
        best_order = rand_team
        print(f'A new team set has been formed with squared average: {best_sq_avg}', flush=True)

# step 2: try random player swapping and save the best changes
# also calculates using least squared error
# print(f'Trying {TOTAL_SWAP} player swaps...', flush=True)
# for x in range(TOTAL_SWAP):
#     # randomly swap two elements in the list
#     rand_team = copy.deepcopy(best_order)
#     i1, i2 = random.sample(range(len(rand_team)), 2)
#     rand_team[i1], rand_team[i2] = rand_team[i2], rand_team[i1]
#
#     # keep track of the team
#     squared_avg = 0
#     team_mmr = 0
#     for i in range(total_players):
#         team_mmr += int(summoners[rand_team[i]][column_dict[COL_MMR]])
#         if i % TEAM_SIZE == TEAM_SIZE - 1:
#             squared_avg += (int(team_mmr / 5) - avg_mmr) ** 2
#             team_mmr = 0
#
#     # replace with the best teams
#     if squared_avg < best_sq_avg:
#         best_sq_avg = squared_avg
#         best_order = rand_team
#         print(f'A new team set has been formed with squared average: {best_sq_avg}', flush=True)


# step 3: add the team numbers, average mmr for their team
team_mmr = 0
for i in range(len(best_order)):
    summoners[best_order[i]][column_dict[COL_TEAM]] = int(i / 5)
    team_mmr += int(summoners[best_order[i]][column_dict[COL_MMR]])
    if i % TEAM_SIZE == TEAM_SIZE - 1:
        team_mmr_avg = int(team_mmr / TEAM_SIZE)
        for j in range(i-TEAM_SIZE+1, i+1):
            summoners[best_order[j]][column_dict[COL_TEAM_MMR]] = team_mmr_avg
        team_mmr = 0


# step 4: assign the roles to each players
for team_num in range(int(len(best_order) / TEAM_SIZE)):
    ind_offset = team_num * TEAM_SIZE
    team_players = best_order[ind_offset: ind_offset + TEAM_SIZE]

    best_sq_role_avg = float('inf')
    best_team_roles = team_players
    for team_perm in list(itertools.permutations(team_players)):
        role_sq_avg = 0
        for role_ind, player_ind in enumerate(team_perm):
            role_sq_avg += (ROLE_PREF_MAX - int(summoners[player_ind][column_dict[ROLE_LIST[role_ind]]])) ** 2
        # better role setup
        if role_sq_avg < best_sq_role_avg:
            best_sq_role_avg = role_sq_avg
            best_team_roles = team_perm

    # assign the roles to the players
    for role_ind, player_ind in enumerate(best_team_roles):
        summoners[player_ind][column_dict[COL_ROLE]] = ROLE_LIST[role_ind]


no_column = summoners[1:]
summoners[1:] = no_column[no_column[:, column_dict[COL_TEAM]].argsort()]

# write to output file
print(f'Writing final teams file to {DATA_DIR}{BEST_TEAMS}.csv')
np.savetxt(f'{DATA_DIR}{BEST_TEAMS}.csv', summoners, fmt='%s', delimiter=',')



