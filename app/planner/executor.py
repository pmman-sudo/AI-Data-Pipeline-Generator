from app.planner.skills import SkillRegistry


class Executor:

    def __init__(self):
        self.registry = SkillRegistry()

    def execute(self, plan, context):

        results = {}

        for step in plan.steps:

            print(
                f"\nRunning Skill: {step.skill}"
            )

            # ------------------------------------------
            # Find skill
            # ------------------------------------------

            skill = self.registry.get(
                step.skill.value
            )

            # ------------------------------------------
            # Build shared context
            # ------------------------------------------

            skill_context = {
                **context,
                "results": results,
            }

            # ------------------------------------------
             # Execute skill
            # ------------------------------------------

            result = skill(
                skill_context
            )

            # ------------------------------------------
            # Stop workflow if skill fails
            # ------------------------------------------

            if isinstance(result, dict):

                if result.get("status") == "failed":

                    print(
                        f"\n❌ Skill failed: "
                        f"{step.skill.value}"
                    )

                    print(
                        f"Reason: "
                        f"{result.get('reason', 'Unknown error')}"
                    )

                    results[step.skill.value] = result

                    break


            # ------------------------------------------
            # Save result
            # ------------------------------------------

            results[step.skill.value] = result

            # ------------------------------------------
            # QUALITY GATE
            # ------------------------------------------

            if step.skill.value == "validate":

                validation_status = result.get(
                    "validation"
                )

                if validation_status != "pass":

                    print(
                        "\n❌ VALIDATION FAILED"
                    )

                    print(
                        f"Details: "
                        f"{result.get('details', 'Unknown validation error')}"
                    )

                    print(
                        "Stopping workflow."
                    )

                    break

                print(
                    "\n✅ VALIDATION PASSED"
                )

        return results