# League of Legends Team Balancer

This repo offers two scripts that gives the ability to _very_ effectively balance League of Legends
players into teams and assign roles/lanes based on their preferences.

All that is required is a `csv` file (easily obtainable through a google form if organized locally) with
a few key identifier information that is necessary to balance. Check out `data/data.csv` for an example
input file (has extra columns as well, completely permissible). Note that all the role columns are a
measure from 1-5 with 5 being main role and 1 being abysmal skill at that role.

The key info is as available (named exactly as the column rows):
* `Summoner Name`
* `top`
* `jungle`
* `middle`
* `bottom`
* `support`

## Collecting MMR of players
Set your input data file to `data/data.csv` with the required columns above, and feel free to include extra
columns as well.

To run the script: ```python mmr_collect.py```

After running the script, view the `data/data_mmr.csv` file to update all the invalid mmr values. If the
summoner does not have recent games (ranked or norms), you will have to find their MMR yourself. Check out
this [api](https://na.whatismymmr.com) for getting a player's mmr, and [op.gg](https://na.op.gg/statistics/tier/)
for tier distribution.

#### Considerations
It is important to note that the ranked and normal average MMR and standard deviation differ by a fairly large
margin. To amend for the normal and ranked mmr differences, an mmr offset (calculated from the middle 50% of
each distribution) is used to decrement the normal mmr, set default to 300.

The default is set to `na` (North America) server.

This script uses this [WhatIsMyMMR API](https://dev.whatismymmr.com/) to get the the MMR of players.

## Generating Teams
To run the script: ```python team_generate.py```

The script reads from `data\data_mmr.csv` and the results file should be written to `data\best_teams.csv`.

#### Restrictions
There amount of data rows must be divisible by 5 and there must be at least 2 teams to be made.

If taken directly from the `mmr_collect.py` script, the 5 require roles should be available as well
as `best_MMR`.

All non-integer values in `best_MMR` must be manually inputted as well.

#### Considerations
The defaults for balancing the team are as follows (and may be modified):
* `TOTAL_PERM = 250000`
* `TOTAL_SWAP = 250000`

The permutation count are randomly generated permutations that look for optimal team setups. The swap
count are randomly swapped players made on the best team setup to look for more optimal teams. This 
value is fairly large despite only have `player_length ^ 2` total swaps in case of incredibly large
data sets, or finding another optimal team. 

The script works specifically for League teams of 5, however `TEAM_SIZE` may be updated for other team
sizes. That change would break the role preferences step, requiring that if you comment it out if you do
this.
