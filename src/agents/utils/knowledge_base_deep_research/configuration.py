class Configuration:
    """
    Configuration for the knowledge base agent.
    """
    def __init__(self):
        self.max_iterations: int = 3

    def to_dict(self):
        return {
            "max_iterations": self.max_iterations
        }

    @classmethod
    def from_runnable_config(cls, config):
        run_config = config.get("configurable", {})
        instance = cls()
        instance.max_iterations = run_config.get("max_iterations", instance.max_iterations)
        return instance 