import numpy as np

from internutopia.core.object import BaseObject
from internutopia.core.scene.scene import IScene
from internutopia_extension.configs.objects import DynamicCubeCfg


@BaseObject.register('DynamicCube')
class DynamicCube(BaseObject):
    def __init__(self, config: DynamicCubeCfg, scene: IScene):
        super().__init__(config, scene)
        self._config = config

    def set_up_to_scene(self, scene: IScene):
        from omni.isaac.core.objects import DynamicCuboid

        scene.add(
            DynamicCuboid(
                prim_path=self._config.prim_path,
                name=self._config.name,
                position=np.array(self._config.position),
                orientation=np.array(self._config.orientation),
                scale=np.array(self._config.scale),
                color=np.array(self._config.color),
            )
        )
