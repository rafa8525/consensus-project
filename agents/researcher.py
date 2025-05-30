import logging

class Researcher:
    def __init__(self):
        logging.info("[Researcher] Initialized with deep role")

    def enrich_tasks(self, tasks):
        logging.info(f"[Researcher] Adding contextual intelligence to tasks: {tasks}")
        enriched = []
        for task in tasks:
            if "framework" in task.lower():
                enriched.append(f"{task} [add industry best practices]")
            elif "summary" in task.lower():
                enriched.append(f"{task} [attach highlights and key wins]")
            else:
                enriched.append(f"{task} [context added]")
        return enriched
