from .Baseline import BaselineV0
from ..plot_utils import module_plot
import numpy as np
from pydantic import ConfigDict, Field
from ..example_formatter import NoIndent
from typing import Literal, Annotated, Union

class NoisewidthV0(BaselineV0):
    model_config = ConfigDict(json_schema_extra={
        'examples': [
            {
                "module": "PBU0001",
                "version": "v0",
                "name": "noisewidth",
                "measurement_date": "2023-01-01T12:00:00+01:00",
                "location": "BU",
                "user_created": "hayden",
                '3':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                '1':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                '2':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60),
                '0':NoIndent(np.ones((16,16), dtype=int).tolist(), max_length=60)
            },   
        ],
        'table': 'test',
        'component_types': [],
        'module_types': ['Production', 'PreProduction', 'Digital', 'Prototype', 'Fake Production'],
        'description': 'Baseline / Noisewidth for a module. Each position follows the standard of this module pcb version in this lablog, it should never change again: https://bu.nebraskadetectorlab.com/submission/4879'
    })
    name: Literal['noisewidth'] = 'noisewidth'

    def plot(self):
        """Plot all 4 16x16 arrays (3, 2, 1, 0) in a 2x2 subplot layout"""
        return module_plot(
            test_name = self.name,
            pos_0 = self.pos_0,
            pos_1 = self.pos_1,
            pos_2 = self.pos_2,
            pos_3 = self.pos_3,
            vmin = 0,
            vmax = 16
        )
    
NoisewidthType = Annotated[Union[NoisewidthV0], Field(discriminator="version")]