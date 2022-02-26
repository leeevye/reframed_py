import sys
import logging
from ReFramedClient import ReFramedClient
from datetime import datetime
import replayed

logging.basicConfig(level=logging.INFO)

client = ReFramedClient()
if len(sys.argv) > 1:
    if not client.connect(sys.argv[1]):
        sys.exit(1)
else:
    if not client.connect("192.168.76.107"): #client.connect(input("Switch IP Address: ")):
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
    with open("stats\\obsscene.stats", 'w') as outputfile:
        outputfile.write("Game")

    open("stats\\p1.stats", 'w').close()
    open("stats\\p2.stats", 'w').close()
    open("stats\\names.stats", 'w').close()
    with open("stats\\names.stats", 'a') as outputfile:
        outputfile.write("Calculating...")

    try:
        print(f"stage: {mapping_info.stage_names[stage_id]}")
    except KeyError:
        print(f"stage: Unknown")

    print(f"num players: {len(fighter_ids)}")

    global mappinginfo
    global fighterids

    global lastframe
    global lastidx
    lastframe = -1
    lastidx = -1

    mappinginfo = mapping_info
    fighterids = fighter_ids

    global replay
    global replayname
    replayname = "replays\\"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+f" - {mapping_info.fighter_names[fighter_ids[0]]} VS {mapping_info.fighter_names[fighter_ids[1]]}.replay"
    replay = open(replayname, "a")

    try:
        replay.write(f"Stage: {mapping_info.stage_names[stage_id]}\n")
    except KeyError:
        replay.write("Stage: Unknown\n")

    for i, fighter_id in enumerate(fighter_ids):
        matchinfo = f"Player {i}: Tag: {tags[i]}, Name: {names[i]}, Fighter: {mapping_info.fighter_names[fighter_id]}, Alt: \n"
        print(matchinfo)
        replay.write(matchinfo)
    replay.write("\nMATCH START\n")
    replay.flush()

@client.on_match_resumed
def handle_match_resumed(mapping_info, stage_id, fighter_ids, tags, names):
    global replay
    global replayname
    replayname = "replays\\"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+f" - {mapping_info.fighter_names[fighter_ids[0]]} VS {mapping_info.fighter_names[fighter_ids[1]]}.replay"
    replay = open(replayname, "a")

    print("match resumed")

    open("stats\\p1.stats", 'w').close()
    open("stats\\p2.stats", 'w').close()

    try:
        stage_name = mapping_info.stage_names[stage_id]
    except KeyError:
        stage_name = "Unknown"
    print("Stage: "+stage_name)
    replay.write("Stage: "+stage_name+"\n")
    print(f"num players: {len(fighter_ids)}")

    global mappinginfo
    global fighterids

    global lastframe
    global lastidx
    lastframe = -1
    lastidx = -1

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
    replayfile = open(replayname)
    replayed.replayedstatistics(replayfile, replayname)


@client.on_frame
def handle_frame(mapping_info, frame, idx, fighter_ids, posx, posy, damage, hitstun, shield, status, motion, hit_status, stocks, attack_connected, facing_direction):
    # Uncomment this for lots of info
    #frameinfo = f"\n{idx}: {frame=}, {posx=}, {posy=}, {damage=}, {hitstun=}, {shield=}, {status=}, {motion=}, {hit_status=}, {stocks=}, {attack_connected=}, {facing_direction=}"
    global lastframe
    global lastidx
    if frame == lastframe and idx == lastidx:
        return
    else:
        lastframe = frame
        lastidx = idx

    try:
        #print(status[0])
        status = mapping_info.fighter_base_status_names[status[0]]
    except KeyError:
        try:
            status = mapping_info.fighter_specific_status_names[fighter_ids[idx]][status[0]]
        except KeyError:
            status = "UNKNOWN_STATUS"
        except:
            status = "UNKNOWN_STATUS"
            print(mapping_info.fighter_specific_status_names[fighter_ids[idx]])
            print(status[0])

    frameinfo = f"{frame=}, {idx=}, {stocks=}, {damage=}, {hitstun=}, {shield=}, {posx=}, {posy=}, {status=}, {attack_connected=}\n"
    #print(frameinfo)
    replay.write(frameinfo)
    pass

try:
    client.run()
except:
    print("Could not connect")
    input("Press any key to exit")
client.disconnect()
