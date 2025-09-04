from edsnlp.core import registry

from .myocardial_infarction import MyocardialInfarctionMatcher
from .patterns import default_patterns

DEFAULT_CONFIG = dict(
    patterns=default_patterns,
    label="myocardial_infarction",
    span_setter={"ents": True, "myocardial_infarction": True},
)

create_component = registry.factory.register(
    "eds.myocardial_infarction",
    assigns=["doc.ents", "doc.spans"],
)(MyocardialInfarctionMatcher)
