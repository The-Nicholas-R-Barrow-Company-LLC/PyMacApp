from .models import App
from .setuptools import BuildConfig

class AppFactory:
    def __init__(self, app: App) -> None:
        self.app = app

# class AppFactory():
#     def __init__(self) -> None:
#         logger.info(f"AppFactory initialized: {self}")

#     def setup(self, bundler, packager, notary_agent:NotaryAgent, stapler:Stapler) -> None:
#         logger.debug(f"setting-up {self}: {bundler=}, {packager=}, {notary_agent=}, {stapler=}")
#         self.attach_bundler(bundler)
#         self.attach_packager(packager)
#         self.attach_notary_agent(notary_agent)
#         self.attach_stapler(stapler)
#         logger.debug(f"setup complete ({self})")

#     def attach_bundler(self):
#         pass

#     def attach_packager(self):
#         pass

#     def attach_notary_agent(self, notary_agent:NotaryAgent) -> NotaryAgent:
#         self.notary_agent = notary_agent
#         logger.debug(f"{notary_agent} attached to {self}")
#         return self.notary_agent

#     def attach_stapler(self, stapler:Stapler) -> Stapler:
#         self.stapler = stapler
#         logger.debug(f"{stapler} attached to {self}")
#         return self.stapler