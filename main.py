import json
from datetime import datetime
import os

#open followers.json
with open('followers_1.json') as file:
  followers_json = json.load(file)

#open following.json
with open('following.json') as file:
  following_json = json.load(file)

followersLst = []
followingLst = []

#get each follower and add it to followersLst
for followers in followers_json:
  followersLst.append(followers['string_list_data'][0]['value'])

#get each following and add it to followingLst
for following in following_json["relationships_following"]:
  followingLst.append(following["string_list_data"][0]['value'])

#list of people not following me back
people_not_following_me_back = [i for i in followingLst if i not in followersLst]

#write to file with date
now = datetime.now()
filename = f"past_runs/people_i_dont_follow_{now.month}_{now.day}_{now.year}.txt"

os.makedirs("past_runs", exist_ok=True)

try:
    with open(filename, "w") as f:
        for i, people in enumerate(people_not_following_me_back):
            f.write("{num}. {name}\n".format(num=i+1, name=people))
    print(f"Successfully wrote results to {filename}")
except Exception as e:
    print(f"Error writing to file: {e}")