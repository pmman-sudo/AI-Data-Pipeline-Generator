from abc import ABC, abstractmethod


class BaseSkill(ABC):
    """
    Base class for every AI Skill.
    """

    name = "base"

    @abstractmethod
    def execute(self, context):
        """
        Executes the skill.

        Parameters
        ----------
        context : dict
            Shared information passed between skills.

        Returns
        -------
        dict
        """
        pass