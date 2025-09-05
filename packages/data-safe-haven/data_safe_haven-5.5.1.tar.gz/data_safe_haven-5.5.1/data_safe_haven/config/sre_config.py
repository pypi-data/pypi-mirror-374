"""SRE configuration file backed by blob storage"""

from __future__ import annotations

from typing import ClassVar, Self

from data_safe_haven.serialisers import AzureSerialisableModel, ContextBase
from data_safe_haven.types import SafeSreName, SoftwarePackageCategory

from .config_sections import (
    ConfigSectionAzure,
    ConfigSectionDockerHub,
    ConfigSectionSRE,
    ConfigSectionUserServices,
    ConfigSubsectionDnsSidecar,
    ConfigSubsectionNexus,
    ConfigSubsectionRemoteDesktopOpts,
    ConfigSubsectionStorageQuotaGB,
)


def sre_config_name(sre_name: str) -> str:
    """Construct a YAML filename given an input SRE name."""
    return f"sre-{sre_name}.yaml"


class SREConfig(AzureSerialisableModel):
    """Serialisable config for a secure research environment component."""

    config_type: ClassVar[str] = "SREConfig"
    default_filename: ClassVar[str] = "sre.yaml"

    azure: ConfigSectionAzure
    description: str
    dockerhub: ConfigSectionDockerHub
    name: SafeSreName
    sre: ConfigSectionSRE
    user_services: ConfigSectionUserServices = ConfigSectionUserServices()

    @property
    def filename(self) -> str:
        """Construct a canonical filename for this SREConfig."""
        return sre_config_name(self.name)

    @classmethod
    def from_remote_by_name(
        cls: type[Self], context: ContextBase, sre_name: str
    ) -> SREConfig:
        """Load an SREConfig from Azure storage."""
        return cls.from_remote(context, filename=sre_config_name(sre_name))

    @classmethod
    def template(cls: type[Self], tier: int | None = None) -> SREConfig:
        """Create SREConfig without validation to allow "replace me" prompts."""
        # Set tier-dependent defaults
        if tier == 0:
            allow_workspace_internet = True
            remote_desktop_allow_copy = True
            remote_desktop_allow_paste = True
            software_packages = SoftwarePackageCategory.ANY
        elif tier == 1:
            allow_workspace_internet = True
            remote_desktop_allow_copy = True
            remote_desktop_allow_paste = True
            software_packages = SoftwarePackageCategory.ANY
        elif tier == 2:  # noqa: PLR2004
            allow_workspace_internet = False
            remote_desktop_allow_copy = False
            remote_desktop_allow_paste = False
            software_packages = SoftwarePackageCategory.ANY
        elif tier == 3:  # noqa: PLR2004
            allow_workspace_internet = False
            remote_desktop_allow_copy = False
            remote_desktop_allow_paste = False
            software_packages = SoftwarePackageCategory.PRE_APPROVED
        elif tier == 4:  # noqa: PLR2004
            allow_workspace_internet = False
            remote_desktop_allow_copy = False
            remote_desktop_allow_paste = False
            software_packages = SoftwarePackageCategory.NONE
        else:
            allow_workspace_internet = (
                "True/False: whether to allow outbound internet access from workspaces.  "  # type: ignore
                "WARNING setting this to True will allow data to be moved out of the SRE "
                "WITHOUT OVERSIGHT OR APPROVAL"
            )
            remote_desktop_allow_copy = "True/False: whether to allow copying text out of the environment."  # type: ignore
            remote_desktop_allow_paste = "True/False: whether to allow pasting text into the environment."  # type: ignore
            software_packages = "[any/pre-approved/none]: which Python/R packages to allow users to install."  # type: ignore

        return SREConfig.model_construct(
            azure=ConfigSectionAzure.model_construct(
                location="Azure location where SRE resources will be deployed.",
                subscription_id="ID of the Azure subscription that the SRE will be deployed to",
                tenant_id="Home tenant for the Azure account used to deploy infrastructure: `az account show`",
            ),
            dockerhub=ConfigSectionDockerHub.model_construct(
                access_token="A DockerHub personal access token (PAT) with 'Public Read-Only' permissions. See instructions here: https://docs.docker.com/security/for-developers/access-tokens/",
                username="Your DockerHub username.",
            ),
            description="Human-friendly name for this SRE deployment.",
            name="A name for this config which consists only of letters, numbers and underscores.",
            sre=ConfigSectionSRE.model_construct(
                admin_email_address="Email address shared by all administrators",
                admin_ip_addresses=["List of IP addresses belonging to administrators"],
                allow_workspace_internet=allow_workspace_internet,
                databases=["List of database systems to deploy"],  # type:ignore
                data_provider_ip_addresses=[
                    "List of IP addresses belonging to data providers"
                ],
                remote_desktop=ConfigSubsectionRemoteDesktopOpts.model_construct(
                    allow_copy=remote_desktop_allow_copy,
                    allow_paste=remote_desktop_allow_paste,
                ),
                research_user_ip_addresses=[
                    "List of IP addresses belonging to users",
                    "You can also use the tag 'Internet' instead of a list",
                ],
                software_packages=software_packages,
                storage_quota_gb=ConfigSubsectionStorageQuotaGB.model_construct(
                    home="Total size in GiB across all home directories [minimum: 100].",  # type: ignore
                    shared="Total size in GiB for the shared directories [minimum: 100].",  # type: ignore
                ),
                timezone="Timezone in pytz format (eg. Europe/London)",
                workspace_skus=[
                    "List of Azure VM SKUs that will be used for data analysis."
                ],
            ),
            user_services=ConfigSectionUserServices.model_construct(
                nexus=ConfigSubsectionNexus.model_construct(
                    persistent_quota_gb="Total size in GiB for Nexus' persistent directory. "  # type: ignore
                ),
                dns_sidecar=ConfigSubsectionDnsSidecar.model_construct(
                    cron_expression="Cron-formatted repeating schedule ('* * * * *') for DNS update.",
                    replica_timeout="Maximum number of seconds a DNS sidecar job is allowed to run.",  # type: ignore
                    retry_limit="Maximum number of retries before failing the DNS sidecar job.",  # type: ignore
                ),
            ),
        )
