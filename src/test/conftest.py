"""Configuration pytest partagée.

Ajoute au sys.path les dossiers que le code applicatif importe « à plat »
(les calculateurs via `pipelines.transform`, l'API via son WORKDIR), afin que
les tests s'importent de la même façon en local et dans la CI.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for _p in (
    os.path.join(_ROOT, "src", "pipelines", "transform"),
    os.path.join(_ROOT, "src", "api"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)
