__author__ = "TheComet"

import socket
import logging
import struct
import time
from MappingInfo import MappingInfo

ProtocolVersion = 0
MappingInfoChecksum = 1
MappingInfoRequest = 2
MappingInfoFighterKinds = 3
MappingInfoFighterStatusKinds = 4
MappingInfoStageKinds = 5
MappingInfoHitStatusKinds = 6
MappingInfoRequestComplete = 7
MatchStart = 8
MatchResume = 9
MatchEnd = 10
TrainingStart = 11
TrainingResume = 12
TrainingReset = 13
TrainingEnd = 14
FighterState = 15

ProtocolMajor = 0x01
ProtocolMinor = 0x00


class ReFramedClient:

    def on_training_started(self, meth):
        self.__training_started_callbacks.append(meth)
        return meth

    def on_training_resumed(self, meth):
        self.__training_resumed_callbacks.append(meth)
        return meth

    def on_training_ended(self, meth):
        self.__training_ended_callbacks.append(meth)
        return meth

    def on_match_started(self, meth):
        self.__match_started_callbacks.append(meth)
        return meth

    def on_match_resumed(self, meth):
        self.__match_resumed_callbacks.append(meth)
        return meth

    def on_match_ended(self, meth):
        self.__match_ended_callbacks.append(meth)
        return meth

    def on_frame(self, meth):
        self.__frame_callbacks.append(meth)
        return meth

    def __init__(self):
        self.sock = None
        self.mapping_info = MappingInfo.load("mapping_info.json")

        self.__training_started_callbacks = list()
        self.__training_resumed_callbacks = list()
        self.__training_ended_callbacks = list()
        self.__match_started_callbacks = list()
        self.__match_resumed_callbacks = list()
        self.__match_ended_callbacks = list()
        self.__frame_callbacks = list()

    def connect(self, ipaddress, port=42069):
        if self.sock is not None:
            self.disconnect()

        # Connect to switch
        logging.info(f"Connecting to {ipaddress}:{port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while connected == False:
            try:
                self.sock.connect((ipaddress, port))
                connected = True
            except Exception as e:
                logging.error(f"Failed to connect to client: {e}")
                logging.error("Retrying in 5 seconds...")
                time.sleep(5)


        return connected

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.sock = None
        logging.info("Disconnected")

    def run(self):
        # Will need to check the protocol version is compatible
        self.sock.send(bytes([ProtocolVersion]))

        # Request either checksum for mapping info or copy of mapping info if we haven't cached it
        if self.mapping_info is None:
            self.sock.send(bytes([MappingInfoRequest]))
        else:
            self.sock.send(bytes([MappingInfoChecksum]))

        entry_ids = dict()

        while True:
            msg_type = self.recv_exact(1)[0]

            if msg_type == ProtocolVersion:
                # Protocol version is 2 bytes, major and minor
                msg = self.recv_exact(2)
                major, minor = int(msg[0]), int(msg[1])
                if major == ProtocolMajor and minor == ProtocolMinor:
                    logging.info(f"Using protocol version {major}.{minor}")
                else:
                    logging.error(f"Switch is using incompatible protocol version {major}.{minor}")
                    break

            elif msg_type == MappingInfoChecksum:
                # Checksum is a uint32
                msg = self.recv_exact(4)
                checksum = (msg[0] << 24) | (msg[1] << 16) | (msg[2] << 8) | (msg[3] << 0)

                if self.mapping_info is not None and self.mapping_info.checksum == checksum:
                    logging.info(f"Mapping info checksum up to date: {checksum:02x}")

                    # If game or training session is running, try resuming
                    logging.info("Requesting match/training resume...")
                    self.sock.send(bytes([MatchResume, TrainingResume]))
                    continue  # All good

                logging.info(f"Mapping info outdated, requesting new")
                self.sock.send(bytes([MappingInfoRequest]))

            elif msg_type == MappingInfoRequest:
                # Checksum is a uint32
                msg = self.recv_exact(4)
                checksum = (msg[0] << 24) | (msg[1] << 16) | (msg[2] << 8) | (msg[3] << 0)

                # Prepare mapping info structure for new info
                self.mapping_info = MappingInfo(checksum)
                logging.info(f"Downloading mapping info with checksum {checksum:02x} (this may take 10-20 seconds)...")

            elif msg_type == MappingInfoFighterKinds:
                fighter_id = self.recv_exact(1)[0]
                len = self.recv_exact(1)[0]
                name = self.recv_exact(len).decode("utf-8")

                self.mapping_info.fighter_names[fighter_id] = name
                logging.debug(f"MappingInfoFighterKinds: {fighter_id} -> {name}")

            elif msg_type == MappingInfoFighterStatusKinds:
                fighter_id = self.recv_exact(1)[0]
                status_id = self.recv_exact(2)
                len = self.recv_exact(1)[0]
                name = self.recv_exact(len).decode("utf-8")

                status_id = (status_id[0] << 8) | (status_id[1] << 0)

                if fighter_id == 255:
                    self.mapping_info.fighter_base_status_names[status_id] = name
                    logging.debug(f"MappingInfoFighterStatusKinds: {status_id} -> {name}")
                else:
                    self.mapping_info.fighter_specific_status_names.setdefault(fighter_id, dict())[status_id] = name
                    logging.debug(f"MappingInfoFighterStatusKinds: {fighter_id}: {status_id} -> {name}")

            elif msg_type == MappingInfoStageKinds:
                stage_id = self.recv_exact(2)
                len = self.recv_exact(1)[0]
                name = self.recv_exact(len).decode("utf-8")

                stage_id = (stage_id[0] << 8) | (stage_id[1] << 0)

                self.mapping_info.stage_names[stage_id] = name
                logging.debug(f"MappingInfoStageKinds: {stage_id} -> {name}")

            elif msg_type == MappingInfoHitStatusKinds:
                status_id = self.recv_exact(1)[0]
                len = self.recv_exact(1)[0]
                name = self.recv_exact(len).decode("utf-8")

                self.mapping_info.hit_status_names[status_id] = name
                logging.debug(f"MappingInfoHitStatusKinds: {status_id} -> {name}")

            elif msg_type == MappingInfoRequestComplete:
                # Save mapping info
                logging.info("Saving mapping info...")
                self.mapping_info.save("mapping_info.json")

                # If game or training session is running, try resuming
                logging.info("Requesting match/training resume...")
                self.sock.send(bytes([MatchResume, TrainingResume]))

            elif msg_type == TrainingStart or msg_type == TrainingResume:
                stage_id = self.recv_exact(2)
                player_fighter_id = self.recv_exact(1)[0]
                cpu_fighter_id = self.recv_exact(1)[0]

                stage_id = (stage_id[0] << 8) | (stage_id[1] << 0)
                entry_ids = {0: 0, 1: 1}  # Always the same in training mode

                logging.info("Training started/resumed")
                callbacks = self.__training_started_callbacks if msg_type == TrainingStart else self.__training_resumed_callbacks
                for l in callbacks:
                    l(self.mapping_info, stage_id, player_fighter_id, cpu_fighter_id)

            elif msg_type == TrainingEnd:
                logging.info("Training ended")
                for l in self.__training_ended_callbacks:
                    l()
            elif msg_type == MatchStart or msg_type == MatchResume:
                stage_id = self.recv_exact(2)
                player_count = self.recv_exact(1)[0]

                stage_id = (stage_id[0] << 8) | (stage_id[1] << 0)

                entry_ids = self.recv_exact(player_count)
                entry_ids = {k: v for k, v in enumerate(entry_ids)}

                fighter_ids = self.recv_exact(player_count)
                fighter_ids = [int(fighter_id) for fighter_id in fighter_ids]

                player_tags = list()
                player_names = list()

                for i in range(player_count):
                    # NOTE: tags are stored as UTF-16 but this isn't implemented server-side yet (I don't know how to
                    # find player tags yet). So the player tags are simply hard coded to "Player X" for now
                    len = self.recv_exact(1)[0]
                    tag = self.recv_exact(len).decode("utf-8")  # Because it's hard-coded server-side, the data is sent as utf-8 for now
                    player_tags.append(tag)
                    player_names.append(tag)

                logging.info("Match started/resumed")
                callbacks = self.__match_started_callbacks if msg_type == MatchStart else self.__match_resumed_callbacks
                for l in callbacks:
                    l(self.mapping_info, stage_id, fighter_ids, player_tags, player_names)

            elif msg_type == MatchEnd:
                logging.info("Match ended")
                for l in self.__match_ended_callbacks:
                    l()

            elif msg_type == FighterState:
                frame, entry_id, posx, posy = struct.unpack("!IBff", self.recv_exact(13))

                damage = self.recv_exact(2)
                damage = ((damage[0] << 8) | (damage[1] << 0)) / 50.0

                hitstun = self.recv_exact(2)
                hitstun = ((hitstun[0] << 8) | (hitstun[1] << 0)) / 100.0

                shield = self.recv_exact(2)
                shield = ((shield[0] << 8) | (shield[1] << 0)) / 200.0

                status = struct.unpack("!H", self.recv_exact(2))

                m0, m1, m2, m3, m4 = self.recv_exact(5)
                motion = (m0 << 32) | (m1 << 24) | (m2 << 16) | (m3 << 8) | (m4 << 0)

                hit_status, stocks, flags = self.recv_exact(3)

                attack_connected = True if (flags & 0x01) else False
                facing_direction = True if (flags & 0x02) else False

                lastframe = -1
                lastidx = -1

                if entry_id in entry_ids:
                    for l in self.__frame_callbacks:
                        l(self.mapping_info, frame, entry_ids[entry_id], fighter_ids, posx, posy, damage, hitstun, shield, status, motion, hit_status, stocks, attack_connected, facing_direction)

            else:
                logging.warning(f"unhandled message type: {msg_type}")

    def recv_exact(self, count):
        buf = bytes()
        while count > 0:
            chunk = self.sock.recv(count)
            buf += chunk
            count -= len(chunk)
        return buf
