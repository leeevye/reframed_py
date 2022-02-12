__author__ = "TheComet"

import json
import os


class MappingInfo:
    def __init__(self, checksum=0):
        self.checksum = checksum

        # Maps fighter IDs to names, such as 8 -> "Pikachu"
        self.fighter_names = dict()

        # Maps fighter status IDs to enum names such as "FIGHTER_STATUS_KIND_IDLE"
        self.fighter_base_status_names = dict()

        # Maps fighter-specific status IDs to enum names
        self.fighter_specific_status_names = dict()

        # Maps stage IDs to stage names
        self.stage_names = dict()

        # Maps hit status IDs to enum names
        self.hit_status_names = dict()

    @staticmethod
    def load(filename):
        if not os.path.exists(filename):
            return None

        j = json.loads(open(filename, "rb").read().decode("utf-8"))
        m = MappingInfo()
        m.checksum = int(j["checksum"])
        m.fighter_names = {int(k): v for k, v in j["fighternames"].items()}
        m.fighter_base_status_names = {int(k): v for k, v in j["fighterstatus"]["base"].items()}
        m.fighter_specific_status_names = {int(k1): {int(k2): v2 for k2, v2 in v1.items()} for k1, v1 in j["fighterstatus"]["specific"].items()}
        m.hit_status_names = {int(k): v for k, v in j["hitstatus"].items()}
        m.stage_names = {int(k): v for k, v in j["stages"].items()}
        return m

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(json.dumps({
                "checksum": self.checksum,
                "fighternames": self.fighter_names,
                "fighterstatus": {
                    "base": self.fighter_base_status_names,
                    "specific": self.fighter_specific_status_names
                },
                "hitstatus": self.hit_status_names,
                "stages": self.stage_names
            }, indent=2).encode("utf-8"))
