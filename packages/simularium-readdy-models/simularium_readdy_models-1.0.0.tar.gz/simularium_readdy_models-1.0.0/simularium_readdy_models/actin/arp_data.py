#!/usr/bin/env python

import math

import numpy as np

from ..common import ReaddyUtil
from .actin_structure import ActinStructure


class ArpData:
    """
    Arp branch nucleator data.
    """

    arp_id = -1
    position = None
    bound = False
    nucleated = False
    daughter_fiber = None
    assigned = False
    distance_from_mother_pointed = math.inf

    def __init__(
        self, arp_id, position, bound=True, nucleated=False, daughter_fiber=None
    ):
        self.arp_id = arp_id
        self.position = position
        self.bound = bound
        self.nucleated = nucleated
        self.daughter_fiber = daughter_fiber
        self.assigned = False
        self.distance_from_mother_pointed = math.inf

    def get_closest_actin_index(
        self, particle_ids, actin_arp_ids, mother_fiber, particles
    ):
        """
        get the index of the closest actin monomer to the arp position
        excluding the barbed end (because that monomer would also be bound to this arp).
        """
        min_distance = math.inf
        closest_actin_index = -1
        for index in range(len(particle_ids) - 1):
            particle_id = particle_ids[index]
            if (
                "actin" in particles[particle_id].type_name
                and particle_id not in actin_arp_ids
            ):
                distance = np.linalg.norm(
                    particles[particle_id].position - self.position
                )
                if distance < min_distance:
                    closest_actin_index = index
                    min_distance = distance
        if mother_fiber is not None and self.daughter_fiber is not None:
            # if this arp is nucleated, check that the branch will grow roughly
            # in the correct direction, otherwise chose a neighbor actin
            # so the branch grows the other direction
            closest_actin_pos = particles[particle_ids[closest_actin_index]].position
            v_daughter = self.daughter_fiber.get_nearest_segment_direction(
                closest_actin_pos
            )
            closest_actin_axis_pos = mother_fiber.get_nearest_position(
                closest_actin_pos
            )
            v_closest = closest_actin_pos - closest_actin_axis_pos
            dot = (
                v_daughter[0] * v_closest[0]
                + v_daughter[1] * v_closest[1]
                + v_daughter[2] * v_closest[2]
            )
            if dot < 0:
                if closest_actin_index < len(particle_ids) - 2:
                    closest_actin_index += 1
                elif closest_actin_index > 0:
                    closest_actin_index -= 1
                else:
                    raise Exception(
                        "Failed to find actin_arp2 that would nucleate branch "
                        "in correct direction"
                    )
        return closest_actin_index

    def get_bound_arp_rotation(self, mother_fiber, actin_arp2_pos):
        """
        get the difference in the arp's current orientation
        compared to the initial orientation as a rotation matrix.
        """
        v_mother = mother_fiber.get_nearest_segment_direction(self.position)
        actin_arp2_axis_pos = mother_fiber.get_nearest_position(actin_arp2_pos)
        v_actin_arp2 = ReaddyUtil.normalize(actin_arp2_pos - actin_arp2_axis_pos)
        current_orientation = ReaddyUtil.get_orientation_from_vectors(
            v_mother, v_actin_arp2
        )
        return np.matmul(
            current_orientation, np.linalg.inv(ActinStructure.bound_arp_orientation())
        )

    def get_bound_monomer_position(self, actin_arp2_pos, mother_fiber, monomer_type):
        """
        get the offset vector in the arp's local space for the nearby monomers.
        """
        offset_vector = (
            ActinStructure.branch_monomer_position(monomer_type)
            - ActinStructure.mother_branch_position()
        )
        rotation = self.get_bound_arp_rotation(mother_fiber, actin_arp2_pos)
        return actin_arp2_pos + np.squeeze(np.array(np.dot(rotation, offset_vector)))

    def get_nucleated_arp_rotation(self, v_mother, v_daughter):
        """
        get the difference in the arp's current orientation
        compared to the initial orientation as a rotation matrix.
        """
        branch_angle = ReaddyUtil.get_angle_between_vectors(v_mother, v_daughter)
        # rotate daughter axis to ideal branch angle
        axis = np.cross(v_mother, v_daughter)
        angle = ActinStructure.branch_angle() - branch_angle
        v_daughter = ReaddyUtil.rotate(v_daughter, axis, angle)
        current_orientation = ReaddyUtil.get_orientation_from_vectors(
            v_mother, v_daughter
        )
        return np.matmul(
            current_orientation,
            np.linalg.inv(ActinStructure.nucleated_arp_orientation()),
        )

    def get_local_nucleated_monomer_position(self, v_mother, v_daughter, monomer_type):
        """
        get the offset vector in the arp's local space for the nearby monomers.
        """
        offset_vector = (
            ActinStructure.branch_monomer_position(monomer_type)
            - ActinStructure.mother_branch_position()
        )
        rotation = self.get_nucleated_arp_rotation(v_mother, v_daughter)
        return np.squeeze(np.array(np.dot(rotation, offset_vector)))

    @staticmethod
    def rotate_position_to_match_branch_angle(
        monomer_position, branch_angle, arp_mother_position, branch_normal
    ):
        """
        rotate a monomer position near a branch to match the actual branch angle
        (angles in radians).
        """
        angle = ActinStructure.branch_angle() - branch_angle
        pivot = (
            arp_mother_position
            + ActinStructure.actin_distance_from_axis() * branch_normal
        )
        v = monomer_position - pivot
        return pivot + ReaddyUtil.rotate(v, branch_normal, angle)
