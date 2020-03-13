"""
omppc binding
maked by semyon442
last ver
"""
import subprocess

from common.log import logUtils as log
from helpers import mapsHelper
from common.constants import mods as PlayMods

class OmppcError(Exception):
    pass


class Omppc:

    OMPPC_FOLDER = ".data/omppc"

    def __init__(self, beatmap_, score_):
        self.beatmap = beatmap_
        self.score = score_
        self.pp = 0
        self.getPP()

    def _runProcess(self):
        # Run with dotnet
        command = \
            "luajit ./pp/omppc/omppc.lua " \
            "-b {map} " \
            "-s {score_.score} " \
            "-m {score_.mods}".format(
                map=self.mapPath,
                score_=self.score
            )
        log.debug("omppc ~> running {}".format(command))
        process = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE)

        # Get pp from output
        output = process.stdout.decode("utf-8", errors="ignore")
        log.debug("omppc ~> output: {}".format(output))
        pp = 0
        try:
            pp = float(output)
        except ValueError:
            raise OmppcError(
                "Invalid 'pp' value (got '{}', expected a float)".format(output))

        log.debug("omppc ~> returned pp: {}".format(pp))
        return pp

    def getPP(self):
        try:
            # Reset pp
            self.pp = 0
            # Disable V2 PPs on Mania due bad calculations in calculator
            if (self.score.mods&PlayMods.SCOREV2) and (self.score.gameMode == 3):
                return 0

            # Cache map
            mapsHelper.cacheMap(self.mapPath, self.beatmap)

            # Calculate pp
            self.pp = self._runProcess()
        except Exception as e1:
            print(e1)
        except OmppcError as e:
            log.warning("Invalid beatmap {}".format(
                self.beatmap.beatmapID))
            self.pp = 0
        finally:
            return self.pp

    @property
    def mapPath(self):
        return f"{self.OMPPC_FOLDER}/maps/{self.beatmap.beatmapID}.osu"
