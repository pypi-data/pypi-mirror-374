# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Private helper functions for the `from_usd` package."""

# Standard Library
from typing import Optional

# Third Party
import numpy as np
from pxr import Usd, UsdGeom

# NVIDIA
import nvidia.srl.usd.prim_helper as prim_helper
from nvidia.srl.basics.enum import Enum, auto


class NodeType(Enum):
    """Enum to denote the node type."""

    GEOMETRY = auto()
    JOINT = auto()
    LINK = auto()
    SENSOR = auto()
    PHONY = auto()


def _is_geometry_prim(prim: Usd.Prim) -> bool:
    """Check if the given prim is a primitive geometry object prim."""
    geometry_types = [UsdGeom.Cylinder, UsdGeom.Cube, UsdGeom.Sphere, UsdGeom.Mesh]

    for geometry_type in geometry_types:
        if prim.IsA(geometry_type):
            return True
    return False


def _is_joint_prim(prim: Usd.Prim) -> bool:
    """Check if the given prim is a joint prim."""
    return prim_helper.is_a_joint(prim)


def _is_link_prim(prim: Usd.Prim) -> bool:
    """Check if the given prim is a link prim."""
    # A prim without a type is assumed to be of type Xform with an identity transform
    if prim.GetTypeName() == "":
        return True
    return prim.IsA(UsdGeom.Xform)


def _is_sensor_prim(prim: Usd.Prim) -> bool:
    """Check if the given prim is a sensor object prim."""
    valid_type_names = ["Camera", "IsaacImuSensor"]
    return prim.GetTypeName() in valid_type_names


def _is_urdf_prim(prim: Usd.Prim) -> bool:
    """Check if the given prim is a prim used in the URDF."""
    return _is_joint_prim(prim) or _is_link_prim(prim) or _is_geometry_prim(prim)


def _get_prim_scale(prim: Usd.Prim) -> Optional[np.ndarray]:
    """Get the prim's scaling value."""
    try:
        scale = prim.GetAttribute("xformOp:scale").Get()
        if scale is not None:
            return np.array(scale)
        else:
            return None
    except ValueError:
        return None
