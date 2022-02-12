import sys
import logging
from ReFramedClient import ReFramedClient
from datetime import datetime



logging.basicConfig(level=logging.INFO)


client = ReFramedClient()
if not client.connect("192.168.1.36"):
    sys.exit(1)


@client.on_training_started
def handle_training_started(mapping_info, stage_id, player_fighter_id, cpu_fighter_id):
    print("training started")

    try:
        print(f"stage: {mapping_info.stage_names[stage_id]}")
    except KeyError:
        print(f"stage: Unknown")

    print(f"player fighter: {mapping_info.fighter_names[player_fighter_id]}")
    print(f"cpu fighter: {mapping_info.fighter_names[cpu_fighter_id]}")


@client.on_training_resumed
def handle_training_resumed(mapping_info, stage_id, player_fighter_id, cpu_fighter_id):
    print("training resumed")

    try:
        print(f"stage: {mapping_info.stage_names[stage_id]}")
    except KeyError:
        print(f"stage: Unknown")

    print(f"player fighter: {mapping_info.fighter_names[player_fighter_id]}")
    print(f"cpu fighter: {mapping_info.fighter_names[cpu_fighter_id]}")


@client.on_training_ended
def handle_training_ended():
    print("training ended")


@client.on_match_started
def handle_match_started(mapping_info, stage_id, fighter_ids, tags, names):
    print("match started")

    try:
        print(f"stage: {mapping_info.stage_names[stage_id]}")
    except KeyError:
        print(f"stage: Unknown")

    print(f"num players: {len(fighter_ids)}")

    global mappinginfo
    global fighterids

    mappinginfo = mapping_info
    fighterids = fighter_ids

    global replay
    replay = open("replays\\"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+f" - {mapping_info.fighter_names[fighter_ids[0]]} VS {mapping_info.fighter_names[fighter_ids[1]]}", "a")

    for i, fighter_id in enumerate(fighter_ids):
        matchinfo = f"Player {i}: Tag: {tags[i]}, Name: {names[i]}, Fighter: {mapping_info.fighter_names[fighter_id]}\n"
        print(matchinfo)
        replay.write(matchinfo)
    replay.write("\nMATCH START\n")
    replay.flush()

@client.on_match_resumed
def handle_match_resumed(mapping_info, stage_id, fighter_ids, tags, names):
    global replay
    try:
        replay = open("replays\\"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+f" - {mapping_info.fighter_names[fighter_ids[0]]} VS {mapping_info.fighter_names[fighter_ids[1]]}", "a")
    except IOError:
        pass

    print("match resumed")
    try:
        stage_name = mapping_info.stage_names[stage_id]

    except KeyError:
        stage_name = "Unknown"
    print("Stage: "+stage_name)
    replay.write("Stage: "+stage_name+"\n")
    print(f"num players: {len(fighter_ids)}")

    global mappinginfo
    global fighterids

    mappinginfo = mapping_info
    fighterids = fighter_ids

    for i, fighter_id in enumerate(fighter_ids):
        matchinfo = f"Player {i}: Tag: {tags[i]}, Name: {names[i]}, Fighter: {mapping_info.fighter_names[fighter_id]}\n"
        print(matchinfo)
        replay.write(matchinfo)
    replay.write("\nMATCH START\n")
    replay.flush()


@client.on_match_ended
def handle_match_ended():
    print("match ended")
    global replay
    replay.write("MATCH END")
    replay.close()


@client.on_frame
def handle_frame(mapping_info, frame, idx, fighter_ids, posx, posy, damage, hitstun, shield, status, motion, hit_status, stocks, attack_connected, facing_direction):
    # Uncomment this for lots of info
    #frameinfo = f"\n{idx}: {frame=}, {posx=}, {posy=}, {damage=}, {hitstun=}, {shield=}, {status=}, {motion=}, {hit_status=}, {stocks=}, {attack_connected=}, {facing_direction=}"
    try:
        #print(status[0])
        status = mapping_info.fighter_base_status_names[status[0]]
    except KeyError:
        try:
            status = mapping_info.fighter_specific_status_names[fighter_ids[idx]][status[0]]
        except KeyError:
            status = "UNKNOWN_STATUS"

    frameinfo = f"{frame=}, {idx=}, {stocks=}, {damage=}, {hitstun=}, {shield=}, {posx=}, {posy=}, {status=}, {attack_connected=}\n"
    #print(frameinfo)
    replay.write(frameinfo)
    pass

client.run()
client.disconnect()
