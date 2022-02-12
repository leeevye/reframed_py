#replayfile = open("..\\replays\\examplereplay")
replayfile = open("..\\replays\\"+"2022-02-12_10-15-42 - Sonic VS Corrin")

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

lines_to_read = [1, 2]
j=0
oldp1stats = []
oldp2stats = []
p1punishing = 0
p2punishing = 0
p1landedonstage = True
p2landedonstage = True

p1punishes = 0
p2punishes = 0
p1killingpunishes = 0
p2killingpunishes = 0

def isbeingpunished(playerstats, oldplayerstats, playerlandedonstage, opponentpunishing, punishes, killingpunishes):
    """
    this function determines whether or not a player is being punished
    """
    if playerstats[status] == "FIGHTER_STATUS_KIND_LANDING" or playerstats[status] == "FIGHTER_STATUS_KIND_PASSIVE" or playerstats[status] == "FIGHTER_STATUS_KIND_PASSIVE_FB" or playerstats[status] == "FIGHTER_STATUS_KIND_WAIT" or playerstats[status] == "FIGHTER_STATUS_KIND_GUARD_ON" or playerstats[status] == "FIGHTER_STATUS_KIND_JUMP_SQUAT" or playerstats[status] == "FIGHTER_STATUS_KIND_WALK" or playerstats[status] == "FIGHTER_STATUS_KIND_DASH":
        playerlandedonstage = True
    if ((oldplayerstats[damage] < playerstats[damage]) and (oldplayerstats[hitstun] < playerstats[hitstun])) or playerstats[status] == "FIGHTER_STATUS_KIND_SHIELD_BREAK_FLY":
        if opponentpunishing == 0:
            punishes = punishes+1
        opponentpunishing = 45
        playerlandedonstage = False
    if opponentpunishing and playerlandedonstage:
        opponentpunishing = opponentpunishing-1
        #print("PUNISHING", end='')
        #print(opponentpunishing)
    if opponentpunishing and (oldplayerstats[stocks] > playerstats[stocks]):
        killingpunishes = killingpunishes+1
        print("!!!")
        print(playerstats[frame])
        print(oldplayerstats[frame])
        print(oldplayerstats[stocks])
        print(playerstats[stocks])
        input("!!!")
        opponentpunishing = False

    return playerstats, oldplayerstats, playerlandedonstage, opponentpunishing, punishes, killingpunishes

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


for i, line in enumerate(replayfile):
    if line == "MATCH START\n":
        #print("gaming started")
        break

lines_to_read = [1, 2]
j=0
oldp1stats = []
oldp2stats = []
p1punishing = 0
p2punishing = 0
p1landedonstage = True
p2landedonstage = True
p1totaldamage = 0
p2totaldamage = 0
for position, line in enumerate(replayfile):
    if line == "MATCH END":
        #print("gaming stopped")
        replayfile.close()
        break

    stats = [s.split("=")[1] for s in line.split(", ")]
    stats[attackconnected] = stats[attackconnected].removesuffix("\n")
    stats[status] = stats[status][1:-1]

    stats = convertstats(stats)

    if position == lines_to_read[0]:
        #print("player1")
        p1stats = stats
        if oldp1stats == []:
            oldp1stats = p1stats

        p1stats, oldp1stats, p1landedonstage, p2punishing, p2punishes, p2killingpunishes = isbeingpunished(p1stats, oldp1stats, p1landedonstage, p2punishing, p2punishes, p2killingpunishes)
        if oldp1stats[damage] < p1stats[damage]:
            p1totaldamage = p1totaldamage+(p1stats[damage]-oldp1stats[damage])

        oldp1stats = p1stats
        lines_to_read[0] = lines_to_read[0]+2

    elif position == lines_to_read[1]:
        #print("player2")
        p2stats = stats
        if oldp2stats == []:
            oldp2stats = p2stats

        p2stats, oldp2stats, p2landedonstage, p1punishing, p1punishes, p1killingpunishes = isbeingpunished(p2stats, oldp2stats, p2landedonstage, p1punishing, p1punishes, p1killingpunishes)
        if oldp2stats[damage] < p2stats[damage]:
            p2totaldamage = p2totaldamage+(p2stats[damage]-oldp2stats[damage])

        oldp2stats = p2stats
        lines_to_read[1] = lines_to_read[1]+2

print("\nSTATISTICS:")
print("\nPlayer 1:")
print("Punishes: ", end='')
print(p1punishes)
print("Killing Punishes: ", end='')
print(p1killingpunishes)
print("Openings / Kill: ", end='')
try:
    print(p1punishes/p1killingpunishes)
except ZeroDivisionError:
    print("N/A")
print("Neutral Wins: ", end='')
try:
    print(str(round((p1punishes/(p1punishes+p2punishes))*100, 1))+"%")
except ZeroDivisionError:
    print("N/A")
print("Total Damage Dealt: ", end='')
print(round(p2totaldamage, 1))
print("Average Kill%: ", end='')
try:
    print(round(p2totaldamage/p1killingpunishes, 1))
except ZeroDivisionError:
    print("N/A")
print("Average Damage / Punish: ", end='')
try:
    print(round(p2totaldamage/p1punishes,1))
except ZeroDivisionError:
    print("N/A")






print("\nPlayer 2:")
print("Punishes: ", end='')
print(p2punishes)
print("Killing Punishes: ", end='')
print(p2killingpunishes)
print("Openings / Kill: ", end='')
try:
    print(p2punishes/p2killingpunishes)
except ZeroDivisionError:
    print("N/A")
print("Neutral Wins: ", end='')
try:
    print(str(round((p2punishes/(p1punishes+p2punishes))*100, 1))+"%")
except ZeroDivisionError:
    print("N/A")
print("Total Damage Dealt: ", end='')
print(p1totaldamage)
print("Average Kill%: ", end='')
try:
    print(p1totaldamage/p2killingpunishes)
except ZeroDivisionError:
    print("N/A")
print("Average Damage / Punish: ", end='')
try:
    print(p1totaldamage/p2punishes)
except ZeroDivisionError:
    print("N/A")

exit()
    #print(line)


    #j = j+1
    #if j == 20:
    #    exit()
