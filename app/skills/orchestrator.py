from .registry import SKILLS


class SkillOrchestrator:

    def run(self, workflow, context):

        for step in workflow:

            skill = SKILLS.get(step)

            if skill is None:
                raise ValueError(f"Unknown skill: {step}")

            context = skill.execute(context)

        return context