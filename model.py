import time
from typing import List
import numpy as np


def sigmoid(x, s):
    return 1 / (1 + np.exp(-s * x))


class Rotor:

    def __init__(
        self,
        id_,
        E,  # joule
        emitter_angle,  # radian
        collector_angle,  # radian
        energy_sharing_neuron=0.001,
        emitter_rotation_neuron=np.random.randn(2),
        collector_rotation_neuron=np.random.randn(2),
    ):

        self.id = id_

        # state variables
        self.E = float(E)
        self.emitter_angle = emitter_angle
        self.collector_angle = collector_angle
        self.alive = True

        # physics variables
        self.E_min = 0
        self.E_max = 1
        assert self.E_min <= self.E <= self.E_max

        # evolutionable variables
        self.energy_sharing_neuron = energy_sharing_neuron
        self.emitter_rotation_neuron = emitter_rotation_neuron
        self.collector_rotation_neuron = collector_rotation_neuron

        # стремиться к восстановлению связи. поиск связи. чтобы сбросить лишнюю энергию
        # дать луч коммуницирующему соседу это отдать часть своей энергии
        # во благо того чтобы своя внутрення энергия не стала
        # слишком (дистабилизирующе) большой и чтобы общая конфигурация (упорядоченная структура) потоков сохранилась

    def soc(self):
        return self.E / (self.E_max - self.E_min)

    def energy_to_share(self):
        return self.energy_sharing_neuron * self.soc()

    def emit_energy(self):
        e = self.energy_to_share()
        self.E -= e
        return e

    def recive_energy(self, e):
        assert e >= 0
        self.E += e

    def emitter_rotation_probability(self):
        # more internal energy, more probability of motion
        return 0.9 * self.soc()

    def collector_rotation_probability(self):
        return 0.9 * self.soc()

    def think_rotation_angle(self, W, x):
        z = W @ x
        a = sigmoid(z, 0.2)
        if 0 <= a < 1 / 4:
            a = 1
        elif 1 / 4 <= a < 2 / 4:
            a = 2
        elif 2 / 4 <= a < 3 / 4:
            a = 3
        elif 3 / 4 <= a < 1:
            a = 4
        else:
            assert False
        return a * np.pi / 2

    def emitter_rotation_angle(self):
        x = np.array([self.soc(), self.emitter_angle / (2 * np.pi)])
        W = self.emitter_rotation_neuron
        return self.think_rotation_angle(W, x)

    def collector_rotation_angle(self):
        x = np.array([self.soc(), self.collector_angle / (2 * np.pi)])
        W = self.collector_rotation_neuron
        return self.think_rotation_angle(W, x)

    def energetic_cost_unit_of_rotation(self, angle):
        return 0.001 * angle / (2 * np.pi)

    def emt_rot_work(self, rot_a):
        return 5 * self.energetic_cost_unit_of_rotation(rot_a)

    def emt_rot_heat(self, rot_a):
        return 2 * self.energetic_cost_unit_of_rotation(rot_a)

    def col_rot_work(self, rot_a):
        return 5 * self.energetic_cost_unit_of_rotation(rot_a)

    def col_rot_heat(self, rot_a):
        return 2 * self.energetic_cost_unit_of_rotation(rot_a)

    def step_heat(self):
        return 0.001

    def ray_thickness(self): ...

    def step(self):
        emt_rot_p = self.emitter_rotation_probability()
        col_rot_p = self.collector_rotation_probability()
        emt_rot_a = self.emitter_rotation_angle()
        col_rot_a = self.collector_rotation_angle()

        rotate_emitter = (
            np.random.choice([0, 1], p=[(1 - emt_rot_p), emt_rot_p]).item() == 1
        )
        rotate_collector = (
            np.random.choice([0, 1], p=[(1 - col_rot_p), col_rot_p]).item() == 1
        )

        if rotate_emitter:
            self.emitter_angle += emt_rot_a
            self.emitter_angle %= 2 * np.pi
            self.E = (
                self.E - self.emt_rot_work(emt_rot_a) - self.emt_rot_heat(emt_rot_a)
            )

        if rotate_collector:
            self.collector_angle += col_rot_a
            self.collector_angle %= 2 * np.pi
            self.E = (
                self.E - self.col_rot_work(col_rot_a) - self.col_rot_heat(col_rot_a)
            )

        self.step_heat()

        if self.E < self.E_min or self.E > self.E_max:
            self.alive = False

        # TODO при некоторых обстоятельствах (например когда энергия оптимальна
        # или когда есть какие то (например энергетическое) совпадения с живым соседом)
        # и когда по соседству есть пустые места, чувак рождает новых на пустые
        # соседствующие места.
        # при рождении происходят мутации в гене определяющем поведение


class Grid:

    def __init__(self, m, n, s, init_energy):

        self.m = m  # rows
        self.n = n  # columns

        self.rotors_number = int(self.m * self.n)

        self.s = s  # space_between_rotors
        self.rotor_radius = 0.1 * self.s
        self.h = self.m * self.s
        self.w = self.n * self.s

        self.scatter_of_rotors = []
        for i in range(self.m):
            for j in range(self.n):
                self.scatter_of_rotors.append(
                    [j * self.s - self.w // 2, i * self.s - self.h // 2]
                )

        self.rotors: List[Rotor] = [
            Rotor(
                id_=i,
                E=init_energy // self.rotors_number,
                emitter_angle=0,
                collector_angle=np.pi,
            )
            for i in range(self.rotors_number)
        ]

        self.rays = []

    def rotor_id_by_position(self, row, column):
        return row * self.n + column

    def energies(self):
        energies_matrix = np.zeros((self.m, self.n))
        for i in range(self.m):
            for j in range(self.n):
                rotor_id = self.rotor_id_by_position(i, j)
                rotor = self.rotors[rotor_id]
                e = rotor.E
                energies_matrix[i, j] = e
        return energies_matrix

    def emitters(self):  # segments to draw
        emitters = []
        for k in range(self.rotors_number):
            r = self.rotor_radius
            phi = self.rotors[k].emitter_angle
            emitter = [
                self.scatter_of_rotors[k],
                [
                    self.scatter_of_rotors[k][0] + r * np.cos(phi),
                    self.scatter_of_rotors[k][1] + r * np.sin(phi),
                ],
            ]
            emitters.append(emitter)
        return emitters

    def collectors(self):  # segments to draw
        collectors = []
        for k in range(self.rotors_number):
            r = self.rotor_radius
            psi = self.rotors[k].collector_angle
            collector = [
                self.scatter_of_rotors[k],
                [
                    self.scatter_of_rotors[k][0] + r * np.cos(psi),
                    self.scatter_of_rotors[k][1] + r * np.sin(psi),
                ],
            ]
            collectors.append(collector)
        return collectors

    def step(self):
        self.rays = []
        for i in range(self.m):
            for j in range(self.n):
                rotor_id = self.rotor_id_by_position(i, j)
                rotor = self.rotors[rotor_id]
                if not rotor.alive:
                    continue
                if rotor.emitter_angle == 0:
                    if j == self.n - 1:
                        # TODO visualize reciving of energy from left and emission to top, right and botom
                        continue
                    right_neighbor_id = self.rotor_id_by_position(i, j + 1)
                    right_neighbor = self.rotors[right_neighbor_id]
                    if not right_neighbor.alive:
                        continue
                    if right_neighbor.collector_angle == np.pi:
                        self.rays.append(
                            [
                                self.scatter_of_rotors[rotor_id],
                                self.scatter_of_rotors[right_neighbor_id],
                            ]
                        )
                        e = rotor.emit_energy()
                        right_neighbor.recive_energy(e)
                elif rotor.emitter_angle == np.pi / 2:
                    if i == self.m - 1:
                        continue
                    top_neighbor_id = self.rotor_id_by_position(i + 1, j)
                    top_neighbor = self.rotors[top_neighbor_id]
                    if not top_neighbor.alive:
                        continue
                    if top_neighbor.collector_angle == 3 * np.pi / 2:
                        self.rays.append(
                            [
                                self.scatter_of_rotors[rotor_id],
                                self.scatter_of_rotors[top_neighbor_id],
                            ]
                        )
                        e = rotor.emit_energy()
                        top_neighbor.recive_energy(e)
                elif rotor.emitter_angle == np.pi:
                    if j == 0:
                        continue
                    left_neighbor_id = self.rotor_id_by_position(i, j - 1)
                    left_neighbor = self.rotors[left_neighbor_id]
                    if not left_neighbor.alive:
                        continue
                    if left_neighbor.collector_angle == 0:
                        self.rays.append(
                            [
                                self.scatter_of_rotors[rotor_id],
                                self.scatter_of_rotors[left_neighbor_id],
                            ]
                        )
                        e = rotor.emit_energy()
                        left_neighbor.recive_energy(e)
                elif rotor.emitter_angle == 3 * np.pi / 2:
                    if i == 0:
                        continue
                    bottom_neighbor_id = self.rotor_id_by_position(i - 1, j)
                    bottom_neighbor = self.rotors[bottom_neighbor_id]
                    if not bottom_neighbor.alive:
                        continue
                    if bottom_neighbor.collector_angle == np.pi / 2:
                        self.rays.append(
                            [
                                self.scatter_of_rotors[rotor_id],
                                self.scatter_of_rotors[bottom_neighbor_id],
                            ]
                        )
                        e = rotor.emit_energy()
                        bottom_neighbor.recive_energy(e)
        for rotor in self.rotors:
            if rotor.alive:
                rotor.step()
