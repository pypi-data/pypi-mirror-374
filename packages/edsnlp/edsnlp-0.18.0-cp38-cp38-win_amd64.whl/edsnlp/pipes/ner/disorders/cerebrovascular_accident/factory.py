from edsnlp.core import registry

from .cerebrovascular_accident import CerebrovascularAccidentMatcher
from .patterns import default_patterns

DEFAULT_CONFIG = dict(
    patterns=default_patterns,
    label="cerebrovascular_accident",
    span_setter={"ents": True, "cerebrovascular_accident": True},
)

create_component = registry.factory.register(
    "eds.cerebrovascular_accident",
    assigns=["doc.ents", "doc.spans"],
)(CerebrovascularAccidentMatcher)
