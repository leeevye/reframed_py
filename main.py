import sys
import logging
from ReFramedClient import ReFramedClient
from datetime import datetime
import replayed
import toml

logging.basicConfig(level=logging.INFO)

settings = toml.load("settings.toml")
switchip = settings["switch"]["ipaddress"]

client = ReFramedClient()
if switchip == "0.0.0.0":
    print("You can set your Switch's IP in settings.toml to connect faster next time!")
    if not client.connect(input("Enter your Switch IP Address: ")):
        sys.exit(1)
else:
    if not client.connect(switchip):
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
    with open("stats\\obsscene.txt", 'w') as outputfile:
        outputfile.write("Game")

    open("stats\\p1stats.txt", 'w').close()
    open("stats\\p2stats.txt", 'w').close()
    open("stats\\names.txt", 'w').close()
    open("stats\\p1char.txt", 'w').close()
    open("stats\\p2char.txt", 'w').close()

    with open("stats\\names.txt", 'a') as outputfile:
        outputfile.write("Calculating...")
    with open("stats\\p1char.txt", 'a') as outputfile:
        outputfile.write(mapping_info.fighter_names[fighter_ids[0]])
    with open("stats\\p2char.txt", 'a') as outputfile:
        outputfile.write(mapping_info.fighter_names[fighter_ids[1]])

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

    global countingdown
    global countdown
    countingdown = False
    countdown = 2

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

    open("stats\\p1stats.txt", 'w').close()
    open("stats\\p2stats.txt", 'w').close()

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
    global countingdown
    global countdown
    countingdown = False
    countdown = 2
    with open("stats\\obsscene.txt", 'w') as outputfile:
        outputfile.write("Statistics")
    #try:
        #replay.write("MATCH END")
        #replay.close()
    #except:
        #pass
    #replayfile = open(replayname)
    #replayed.replayedstatistics(replayfile, replayname)


@client.on_frame
def handle_frame(mapping_info, frame, idx, fighter_ids, posx, posy, damage, hitstun, shield, status, motion, hit_status, stocks, attack_connected, facing_direction):
    # Uncomment this for lots of info
    #frameinfo = f"\n{idx}: {frame=}, {posx=}, {posy=}, {damage=}, {hitstun=}, {shield=}, {status=}, {motion=}, {hit_status=}, {stocks=}, {attack_connected=}, {facing_direction=}"
    global lastframe
    global lastidx
    global countingdown
    global countdown

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

    if stocks == 0 and countingdown == False and countdown == 2:
        countingdown = True

    if countdown == 0:
        if countingdown == True:
            countingdown = False
            print("DONE")
            try:
                replay.write("MATCH END")
                replay.close()
            except:
                pass
            replayfile = open(replayname)
            replayed.replayedstatistics(replayfile, replayname)
        else:
            return
    else:
        if countingdown == True:
            countdown = countdown - 1
        replay.write(frameinfo)


#try:
client.run()
#except Exception as e:
#    print(e)
#    input("Press any key to exit")
client.disconnect()
