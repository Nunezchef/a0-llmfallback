from python.helpers.extension import Extension
from usr.helpers import llm_fallback


class InstallLlmFallback(Extension):
    async def execute(self, **kwargs):
        if self.agent:
            llm_fallback.install_agent_fallback_hooks(self.agent)
