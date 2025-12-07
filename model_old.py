from typing import List
import numpy as np
from copy import copy


class Photon:

    def __init__(self, E, x, y, v_x, v_y):
        self.E = E  # E = plank * f
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y

    def position(self):
        return np.ndarray([self.x, self.y])

    def velocity(self):
        return np.ndarray([self.v_x, self.v_y])

    def set_velocity(self, v_x, v_y):
        self.v_x = v_x
        self.v_y = v_y

    def step(self, dt):
        self.x += self.dt * self.v_x
        self.y += self.dt * self.v_y


class Agent:

    def __init__(self, id_, E, s, plank, angle, blinks_per_emission_T, emission_quant):
        self.id = id_
        self.E = float(E)  # E = plank * f
        self.s = bool(s)  # {0, 1}
        self.plank = float(plank)
        self.angle = angle

        self.blinks_per_emission_T = int(blinks_per_emission_T)
        self.emission_quant = float(emission_quant)

        self.blinks_made_befor_emission = 0

        self.rotation_frequency = 1

    def blink_T(self):
        self.plank / self.E  # W*s*s / W*s = s

    def rotate(
        self,
    ):  # change state = consume order = change communicational conditions
        # rotate direction of emited photon
        angle_delta = 0.001  # TODO low
        energy_for_work = 0.001  # TODO low
        self.angle += angle_delta
        self.E -= energy_for_work

    def emit(self) -> float:
        emission = 0
        quants_to_emit = self.blinks_made_befor_emission // self.blinks_per_emission_T
        for _ in range(quants_to_emit):
            self.E -= self.emission_quant
            emission += self.emission_quant
        self.blinks_made_befor_emission %= self.blinks_per_emission_T
        return emission

    def step(self, control_dt):
        self.rotate()
        blinks_n = control_dt / self.blink_T()
        for blink_i in range(blinks_n):
            self.s = not self.s
            self.blinks_made_befor_emission += blink_i


class PhotonGenerator:

    def __init__(self, x, y, emission_rate):
        self.x = x
        self.y = y
        self.emission_rate = emission_rate
        # TODO self.photons_probability_distribution = ...
        self.photons: List[Photon] = []

    def position(self):
        return np.ndarray([self.x, self.y])

    def generate_photons(self):
        self.photons = []
        to_emit = 0
        while to_emit < self.emission_rate:
            Ep = 1
            p = Photon(E=Ep, x=self.x, y=self.y, v_x=0.1, v_y=0.1)
            self.photons.append(p)
            to_emit += Ep


class Grid:

    def __init__(self, x, y, w, h, agents):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.gap = 0.01
        self.agents: List[Agent] = agents

    def position(self):
        return np.ndarray([self.x, self.y])

    def agent_position_by_id(self, agent_id: int) -> np.ndarray:
        y = agent_id // int(self.w / self.gap)
        x = agent_id % int(self.w / self.gap)
        return np.ndarray([x, y])

    def angle_to_velocity(self, angle) -> np.ndarray:
        v_x = np.cos(angle)
        v_y = np.sin(angle)
        v = np.ndarray([v_x, v_y])
        return v / np.linalg.norm(v)

    def emit(self) -> List[Photon]:
        photons = []
        for a in self.agents:
            emission = a.emit()
            position = self.agent_position_by_id(a.id)
            velosity = self.angle_to_velocity(a.angle)
            photon = Photon(
                emission, position[0], position[1], velosity[0], velosity[1]
            )
            photons.append(photon)
        return photons

    def rotate(self):
        for a in self.agents:
            a.rotate()

    def step(self):  # step agents
        for a in self.agents:
            a.step()


class System:

    def __init__(self):
        self.photons_generator: PhotonGenerator = PhotonGenerator(x, y, emission_rate)
        self.grid: Grid = Grid(x, y, w, h, agents)
        self.photons = copy(self.photons_generator.photons)
        self.distance_epsilon = 0.0001

    def photons_agents_energy_exchange(self):
        for a in self.grid.agents:
            for p in self.photons:
                distance = p.position() - a.position
                if np.linalg.norm(distance) <= self.distance_epsilon:
                    self.interchange(a, p)

    def step(self): ...

    # TODO take agents from grid emission and so on
