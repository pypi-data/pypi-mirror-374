# SPDX-FileCopyrightText: 2024-present Hayden Swanson <hayden_swanson22@yahoo.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import Environment, PackageLoader, select_autoescape
from typing import Any, Union, Annotated
from pydantic import Field, TypeAdapter

from matplotlib import use as pltuse
pltuse("agg")

jinja_env = Environment(
    loader=PackageLoader(__name__),
    autoescape=select_autoescape()
)

from .upload import Session, get_model, now_utc, localize_datetime

##########################################################################
# Tamalero
from .tamalero.Baseline import BaselineType
from .tamalero.Noisewidth import NoisewidthType
# Sensor
from .sensor.ChargeCollection import ChargeCollectionType
from .sensor.CurrentStability import CurrentStabilityType
from .sensor.CurrentUniformity import CurrentUniformityType
from .sensor.CurrentUniformity import CurrentUniformityType
from .sensor.GainCurve import GainCurveType
from .sensor.GainLayerUniformity import GainLayerUniformityType
from .sensor.InterpadResistance import InterpadResistanceType
from .sensor.InterpadWidth import InterpadWidthType
from .sensor.MPVStability import MPVStabilityType
from .sensor.SensorIV import SensorIVType
from .sensor.TestArrayCV import TestArrayCVType
from .sensor.TestArrayIV import TestArrayIVType
from .sensor.TimeResolution import TimeResolutionType
# Gantry
from .gantry.PickAndPlace import PickAndPlaceType
from .gantry.SubassemblyAlignment import SubassemblyAlignmentType
# Fake
from .fake.fake_test_component import FakeTestComponentType
from .fake.fake_test_module import FakeTestModuleType
# TestByImage
from .test_by_image.test_by_image import TestByImageType
# Get all test types
_tests = (
    ChargeCollectionType,
    CurrentStabilityType,
    CurrentUniformityType,
    GainCurveType,
    GainLayerUniformityType,
    InterpadResistanceType,
    InterpadWidthType,
    MPVStabilityType,
    SensorIVType,
    TestArrayCVType,
    TestArrayIVType,
    TimeResolutionType,
    BaselineType,
    NoisewidthType,
    PickAndPlaceType,
    SubassemblyAlignmentType,
    FakeTestComponentType,
    FakeTestModuleType,
    TestByImageType    
)
##########################################################################

TestType = Annotated[Union[_tests], Field(discriminator="name")]
TestModel = TypeAdapter(TestType)

__all__ = [
    'Session', 
    'get_model', 
    'jinja_env', 
    'now_utc', 
    'localize_datetime',
]



