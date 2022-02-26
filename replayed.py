import sys
import glob
import os
import statistics

frame = 0
idx = 1
stocks = 2
damage = 3
hitstun = 4
shield = 5
posx = 6
posy = 7
status = 8
attackconnected = 9

def replayedstatistics(replayfile, filename):
    """
    This is the important thing
    """
    p1stats = None
    p2stats = None
    oldp1stats = None
    oldp2stats = None
    p1punishing = 0
    p2punishing = 0
    p1landedonstage = True
    p2landedonstage = True
    p1punishes = 0
    p2punishes = 0
    p1killingpunishes = 0
    p2killingpunishes = 0
    p1totaldamage = 0
    p2totaldamage = 0
    p1damagetaken = 0
    p2damagetaken = 0
    p1damagesatdeath = []
    p2damagesatdeath = []
    p1stagecontrol = 0
    p2stagecontrol = 0
    firstblood = None
    p1firsthits = []
    p1lasthits = []
    p1latesthit = None
    p2firsthits = []
    p2lasthits = []
    p2latesthit = None

    started = 0
    startframe = None
    p1frames = []
    p2frames = []
    playerinfo = []
    players = {}

    global frame
    global idx
    global stocks
    global damage
    global hitstun
    global shield
    global posx
    global posy
    global status
    global attackconnected

    for position, line in enumerate(replayfile):

        if not started:
            if line == "MATCH START\n":
                started = 2
            elif line[0:7] == "Stage: ":
                stage = line[7:]
            elif line[0:7] == "Player ":
                playerid = line[7:8]
                playerinfo = line[10:].split(", ")
                i = 0
                for info in playerinfo:
                    playerinfo[i] = info.split(": ")[1]
                    i = i+1
                playerinfo[-1] = playerinfo[-1].removesuffix("\n")
                players[playerid] = playerinfo

            continue
        elif line == "MATCH END":
            endframe = stats[frame]
            durationframes = startframe - endframe
            durationseconds = round(durationframes/60)
            durationmins, durationsecs = divmod(durationseconds, 60)
            replayfile.close()
            break

        stats = [s.split("=")[1] for s in line.split(", ")]
        stats[attackconnected] = stats[attackconnected].removesuffix("\n")
        stats[status] = stats[status][1:-1]
        stats = convertstats(stats)

        if started == 2 and stats[idx] == 1: #skips forst line of replay, the first frame only gets recorded for player 1, not for player 0.
            startframe = stats[frame]
            started = 1
            continue

        if stats[idx] == 0:
            if (stats[frame] in p1frames):
                continue
            else:
                p1frames.append(stats[frame])

            p1stats = stats
            if oldp1stats == None:
                oldp1stats = p1stats

        elif stats[idx] == 1:
            if (stats[frame] in p2frames):
                continue
            else:
                p2frames.append(stats[frame])

            p2stats = stats
            if oldp2stats == None:
                oldp2stats = p2stats

        if p1stats is not None and p2stats is not None:
            # a dodgy failsafe
            if p1stats[frame] != p2stats[frame]:
                print("bro wtf")
                print(p1stats[frame])
                print(p2stats[frame])

            # Damage
            if p1stats[damage] > oldp1stats[damage]:
                p1damagetaken = p1damagetaken + (p1stats[damage] - oldp1stats[damage])
            if p2stats[damage] > oldp2stats[damage]:
                p2damagetaken = p2damagetaken + (p2stats[damage] - oldp2stats[damage])

            # Damage but accounting for heals
            #if oldp1stats[damage] != p1stats[damage] and p1stats[status] != "FIGHTER_STATUS_KIND_REBIRTH":
                #p1totaldamage = p1totaldamage + (p1stats[damage] - oldp1stats[damage])
            #if oldp2stats[damage] != p2stats[damage] and p2stats[status] != "FIGHTER_STATUS_KIND_REBIRTH":
                #p2totaldamage = p2totaldamage + (p2stats[damage] - oldp2stats[damage])

            # Stocks
            if p1stats[stocks] < oldp1stats[stocks]:
                p1damagesatdeath.append(p1stats[damage])
            if p2stats[stocks] < oldp2stats[stocks]:
                p2damagesatdeath.append(p2stats[damage])

            # First Blood
            if firstblood is None:
                if len(p1damagesatdeath) == 1 and len(p2damagesatdeath) == 0:
                    firstblood = "Player 2"
                elif len(p1damagesatdeath) == 0 and len(p2damagesatdeath) == 1:
                    firstblood = "Player 1"

            # Punishes
            p1stats, oldp1stats, p1landedonstage, p2punishing, p2punishes, p2killingpunishes, p2firsthits, p2lasthits, p2latesthit = punishes(p1stats, oldp1stats, p1landedonstage, p2punishing, p2punishes, p2killingpunishes, p2firsthits, p2lasthits, p2latesthit, p2stats)
            p2stats, oldp2stats, p2landedonstage, p1punishing, p1punishes, p1killingpunishes, p1firsthits, p1lasthits, p1latesthit = punishes(p2stats, oldp2stats, p2landedonstage, p1punishing, p1punishes, p1killingpunishes, p1firsthits, p1lasthits, p1latesthit, p1stats)


            # Stage Control
            if abs(p2stats[posx]) < abs(p1stats[posx]):
                p2stagecontrol = p2stagecontrol + 1
            elif abs(p2stats[posx]) > abs(p1stats[posx]):
                p1stagecontrol = p1stagecontrol + 1

            # Reset Player Stats
            oldp1stats = p1stats
            oldp2stats = p2stats
            p1stats = None
            p2stats = None


    if True:
        
        with open("stats\\p1.stats", 'a') as outputfile:
            outputfile.write(players["0"][2]+"\n\n")
            basicstatistics(p1punishes, p2punishes, p1killingpunishes, p2damagetaken, p1damagesatdeath, p2damagesatdeath, p1stagecontrol, p2stagecontrol, p1firsthits, p1lasthits, outputfile)
        with open("stats\\p2.stats", 'a') as outputfile:
            outputfile.write(players["1"][2]+"\n\n")
            basicstatistics(p2punishes, p1punishes, p2killingpunishes, p1damagetaken, p2damagesatdeath, p1damagesatdeath, p2stagecontrol, p1stagecontrol, p2firsthits, p2lasthits, outputfile)
        open("stats\\names.stats", 'w').close()
        with open("stats\\names.stats", 'a') as outputfile:
            outputfile.write("VS\n\nNeutral Wins\nStocks Taken\nOpenings / Kill\nNeutral Win %\nTotal Damage Done\nAverage Kill Percent\nAverage Damage / Opening\nEarliest Kill\nLatest Death\nStage Control %")
        with open("stats\\obsscene.stats", 'w') as outputfile:
            outputfile.write("Statistics")

        filenames = ["stats\\"+filename[11:].removesuffix('.replay')+".stats", "stats\\latest.stats"]
        #filename = filename[11:].removesuffix('.replay')+".stats"
        #filename = "latest.stats"
        for file in filenames:
            open(file, 'w').close()
            with open(file, "a") as outputfile:
                outputfile.write("Player 1:\n")
                finalstatistics(p1punishes, p2punishes, p1killingpunishes, p2damagetaken, p1damagesatdeath, p2damagesatdeath, p1stagecontrol, p2stagecontrol, p1firsthits, p1lasthits, outputfile)
                outputfile.write("\nPlayer 2:\n")
                finalstatistics(p2punishes, p1punishes, p2killingpunishes, p1damagetaken, p2damagesatdeath, p1damagesatdeath, p2stagecontrol, p1stagecontrol, p2firsthits, p2lasthits, outputfile)

                outputfile.write("\nStage: ")
                outputfile.write(stage) #stage
                outputfile.write("Duration: ")
                outputfile.write(str(durationmins)+":"+str(durationsecs)+"\n")
                outputfile.write("First Blood: ")
                try:
                    outputfile.write(firstblood+"\n")
                except:
                    outputfile.write("N/A\n")
                outputfile.write("P1 Character: ")
                outputfile.write(players["0"][2]+"\n")
                outputfile.write("P2 Character: ")
                outputfile.write(players["1"][2]+"\n")
                outputfile.write("P1 Alt: ")
                outputfile.write("N/A"+"\n")
                outputfile.write("P2 Alt: ")
                outputfile.write("N/A"+"\n")
                outputfile.write("P1 Tag: ")
                outputfile.write(players["0"][0]+"\n")
                outputfile.write("P2 Tag: ")
                outputfile.write(players["1"][0]+"\n")

def convertstats(stats):
    """
    this function properly formats stats
    """
    i=0
    for stat in stats:
        if i <= 2:
            stats[i] = int(stat)
        elif i <= 7:
            stats[i] = float(stat)
        elif i == 9:
            if stat == "True":
                stats[i] = True
            else:
                stats[i] = False
        i=i+1
    return stats

def punishes(playerstats, oldplayerstats, playerlandedonstage, opponentpunishing, punishes, killingpunishes, opponentfirsthits, opponentlasthits, opponentlatesthit, opponentstats):
    """
    this function performs the checks and calculations around player punishes
    """
    if playerstats[status] == "FIGHTER_STATUS_KIND_LANDING" or playerstats[status] == "FIGHTER_STATUS_KIND_PASSIVE" or playerstats[status] == "FIGHTER_STATUS_KIND_PASSIVE_FB" or playerstats[status] == "FIGHTER_STATUS_KIND_WAIT" or playerstats[status] == "FIGHTER_STATUS_KIND_GUARD_ON" or playerstats[status] == "FIGHTER_STATUS_KIND_JUMP_SQUAT" or playerstats[status] == "FIGHTER_STATUS_KIND_WALK" or playerstats[status] == "FIGHTER_STATUS_KIND_DASH":
        playerlandedonstage = True
    if ((oldplayerstats[damage] < playerstats[damage]) and (oldplayerstats[hitstun] < playerstats[hitstun])) or playerstats[status] == "FIGHTER_STATUS_KIND_SHIELD_BREAK_FLY":
        if opponentpunishing == 0:
            punishes = punishes+1
            opponentfirsthits.append(opponentstats[status])
        opponentpunishing = 45
        opponentlatesthit = opponentstats[status]
        playerlandedonstage = False
    if opponentpunishing and playerlandedonstage:
        opponentpunishing = opponentpunishing-1
    if opponentpunishing and (oldplayerstats[stocks] > playerstats[stocks]):
        killingpunishes = killingpunishes+1
        opponentlasthits.append(opponentlatesthit)
        opponentpunishing = False

    return playerstats, oldplayerstats, playerlandedonstage, opponentpunishing, punishes, killingpunishes, opponentfirsthits, opponentlasthits, opponentlatesthit

def finalstatistics(playerpunishes, opponentpunishes, playerkillingpunishes, opponentdamagetaken, playerdamagesatdeath, opponentdamagesatdeath, playerstagecontrol, opponentstagecontrol, playerfirsthits, playerlasthits, outputfile):
    """
    this function calculates final statistics
    """
    outputfile.write("Neutral Wins: ")
    outputfile.write(str(playerpunishes)+"\n")
    outputfile.write("Stocks Taken: ")
    outputfile.write(str(playerkillingpunishes)+"\n")
    outputfile.write("Openings / Kill: ")
    try:
        outputfile.write(str(round(playerpunishes/playerkillingpunishes, 2))+"\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write("Neutral Win %: ")
    try:
        outputfile.write(str(round((playerpunishes/(playerpunishes+opponentpunishes))*100, 2))+"%\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write("Total Damage Done: ")
    outputfile.write(str(round(opponentdamagetaken, 1))+"\n")
    outputfile.write("Average Kill Percent: ")
    try:
        outputfile.write(str(round(statistics.mean(opponentdamagesatdeath), 1))+"\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write("Average Damage / Opening: ")
    try:
        outputfile.write(str(round(opponentdamagetaken/playerpunishes,1))+"\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write("Earliest Kill: ")
    try:
        outputfile.write(str(round(min(opponentdamagesatdeath), 1))+"\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write("Latest Death: ")
    try:
        outputfile.write(str(round(max(playerdamagesatdeath), 1))+"\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write("Stage Control %: ")
    try:
        outputfile.write(str(round(playerstagecontrol/(playerstagecontrol+opponentstagecontrol)*100, 2))+"%\n")
    except:
        outputfile.write("N/A\n")
    if False:
        outputfile.write("Most Common Neutral Opener: ")
        try:
            outputfile.write(statistics.mode(playerfirsthits)+"\n")
        except:
            outputfile.write("N/A\n")
        outputfile.write("Most Common Kill Move: ")
        try:
            outputfile.write(statistics.mode(playerlasthits)+"\n")
        except:
            outputfile.write("N/A\n")
    return

def basicstatistics(playerpunishes, opponentpunishes, playerkillingpunishes, opponentdamagetaken, playerdamagesatdeath, opponentdamagesatdeath, playerstagecontrol, opponentstagecontrol, playerfirsthits, playerlasthits, outputfile):
    """
    this function calculates final statistics but combined
    """
    outputfile.write(str(playerpunishes)+"\n")
    outputfile.write(str(playerkillingpunishes)+"\n")
    try:
        outputfile.write(str(round(playerpunishes/playerkillingpunishes, 2))+"\n")
    except:
        outputfile.write("N/A\n")
    try:
        outputfile.write(str(round((playerpunishes/(playerpunishes+opponentpunishes))*100, 2))+"%\n")
    except:
        outputfile.write("N/A\n")
    outputfile.write(str(round(opponentdamagetaken, 1))+"\n")
    try:
        outputfile.write(str(round(statistics.mean(opponentdamagesatdeath), 1))+"\n")
    except:
        outputfile.write("N/A\n")
    try:
        outputfile.write(str(round(opponentdamagetaken/playerpunishes,1))+"\n")
    except:
        outputfile.write("N/A\n")
    try:
        outputfile.write(str(round(min(opponentdamagesatdeath), 1))+"\n")
    except:
        outputfile.write("N/A\n")
    try:
        outputfile.write(str(round(max(playerdamagesatdeath), 1))+"\n")
    except:
        outputfile.write("N/A\n")
    try:
        outputfile.write(str(round(playerstagecontrol/(playerstagecontrol+opponentstagecontrol)*100, 2))+"%\n")
    except:
        outputfile.write("N/A\n")
    if False:
        try:
            outputfile.write(statistics.mode(playerfirsthits)+"\n")
        except:
            outputfile.write("N/A\n")
        try:
            outputfile.write(statistics.mode(playerlasthits)+"\n")
        except:
            outputfile.write("N/A\n")
    return

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        replayfile = open(sys.argv[1])

    else: #get latest replay file
        list_of_files = glob.glob("replays\\*.replay")
        filename = max(list_of_files, key=os.path.getctime)
        replayfile = open(filename)

    replayedstatistics(replayfile, filename)
    exit()
