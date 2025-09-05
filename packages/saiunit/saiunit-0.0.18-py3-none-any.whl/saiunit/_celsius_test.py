# Copyright 2024 BDP Ecosystem Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import numpy as np

import saiunit as u


def test1():
    a = u.celsius2kelvin(0)
    assert a == 273.15 * u.kelvin

    b = u.celsius2kelvin(-100)
    assert u.math.allclose(b, 173.15 * u.kelvin)


def test2():
    a = u.kelvin2celsius(273.15 * u.kelvin)
    assert a == 0

    b = u.kelvin2celsius(173.15 * u.kelvin)
    assert np.isclose(b, -100)
