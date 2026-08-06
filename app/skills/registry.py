from .search import SearchSkill
from .lineage import LineageSkill
from .enrich import EnrichSkill
from .quality import QualitySkill

SKILLS = {
    "search": SearchSkill(),
    "lineage": LineageSkill(),
    "enrich": EnrichSkill(),
    "quality": QualitySkill(),
}