from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.environment_config_analytics_settings import EnvironmentConfigAnalyticsSettings
    from ..models.environment_config_cluster_settings import EnvironmentConfigClusterSettings
    from ..models.environment_config_compliance_settings import EnvironmentConfigComplianceSettings
    from ..models.environment_config_email_settings import EnvironmentConfigEmailSettings
    from ..models.environment_config_file_settings import EnvironmentConfigFileSettings
    from ..models.environment_config_git_lab_settings import EnvironmentConfigGitLabSettings
    from ..models.environment_config_google_settings import EnvironmentConfigGoogleSettings
    from ..models.environment_config_ldap_settings import EnvironmentConfigLdapSettings
    from ..models.environment_config_localization_settings import EnvironmentConfigLocalizationSettings
    from ..models.environment_config_log_settings import EnvironmentConfigLogSettings
    from ..models.environment_config_metrics_settings import EnvironmentConfigMetricsSettings
    from ..models.environment_config_native_app_settings import EnvironmentConfigNativeAppSettings
    from ..models.environment_config_office_365_settings import EnvironmentConfigOffice365Settings
    from ..models.environment_config_password_settings import EnvironmentConfigPasswordSettings
    from ..models.environment_config_privacy_settings import EnvironmentConfigPrivacySettings
    from ..models.environment_config_rate_limit_settings import EnvironmentConfigRateLimitSettings
    from ..models.environment_config_saml_settings import EnvironmentConfigSamlSettings
    from ..models.environment_config_service_settings import EnvironmentConfigServiceSettings
    from ..models.environment_config_sql_settings import EnvironmentConfigSqlSettings
    from ..models.environment_config_support_settings import EnvironmentConfigSupportSettings
    from ..models.environment_config_team_settings import EnvironmentConfigTeamSettings


T = TypeVar("T", bound="EnvironmentConfig")


@_attrs_define
class EnvironmentConfig:
    """
    Attributes:
        service_settings (Union[Unset, EnvironmentConfigServiceSettings]):
        team_settings (Union[Unset, EnvironmentConfigTeamSettings]):
        sql_settings (Union[Unset, EnvironmentConfigSqlSettings]):
        log_settings (Union[Unset, EnvironmentConfigLogSettings]):
        password_settings (Union[Unset, EnvironmentConfigPasswordSettings]):
        file_settings (Union[Unset, EnvironmentConfigFileSettings]):
        email_settings (Union[Unset, EnvironmentConfigEmailSettings]):
        rate_limit_settings (Union[Unset, EnvironmentConfigRateLimitSettings]):
        privacy_settings (Union[Unset, EnvironmentConfigPrivacySettings]):
        support_settings (Union[Unset, EnvironmentConfigSupportSettings]):
        git_lab_settings (Union[Unset, EnvironmentConfigGitLabSettings]):
        google_settings (Union[Unset, EnvironmentConfigGoogleSettings]):
        office_365_settings (Union[Unset, EnvironmentConfigOffice365Settings]):
        ldap_settings (Union[Unset, EnvironmentConfigLdapSettings]):
        compliance_settings (Union[Unset, EnvironmentConfigComplianceSettings]):
        localization_settings (Union[Unset, EnvironmentConfigLocalizationSettings]):
        saml_settings (Union[Unset, EnvironmentConfigSamlSettings]):
        native_app_settings (Union[Unset, EnvironmentConfigNativeAppSettings]):
        cluster_settings (Union[Unset, EnvironmentConfigClusterSettings]):
        metrics_settings (Union[Unset, EnvironmentConfigMetricsSettings]):
        analytics_settings (Union[Unset, EnvironmentConfigAnalyticsSettings]):
    """

    service_settings: Union[Unset, "EnvironmentConfigServiceSettings"] = UNSET
    team_settings: Union[Unset, "EnvironmentConfigTeamSettings"] = UNSET
    sql_settings: Union[Unset, "EnvironmentConfigSqlSettings"] = UNSET
    log_settings: Union[Unset, "EnvironmentConfigLogSettings"] = UNSET
    password_settings: Union[Unset, "EnvironmentConfigPasswordSettings"] = UNSET
    file_settings: Union[Unset, "EnvironmentConfigFileSettings"] = UNSET
    email_settings: Union[Unset, "EnvironmentConfigEmailSettings"] = UNSET
    rate_limit_settings: Union[Unset, "EnvironmentConfigRateLimitSettings"] = UNSET
    privacy_settings: Union[Unset, "EnvironmentConfigPrivacySettings"] = UNSET
    support_settings: Union[Unset, "EnvironmentConfigSupportSettings"] = UNSET
    git_lab_settings: Union[Unset, "EnvironmentConfigGitLabSettings"] = UNSET
    google_settings: Union[Unset, "EnvironmentConfigGoogleSettings"] = UNSET
    office_365_settings: Union[Unset, "EnvironmentConfigOffice365Settings"] = UNSET
    ldap_settings: Union[Unset, "EnvironmentConfigLdapSettings"] = UNSET
    compliance_settings: Union[Unset, "EnvironmentConfigComplianceSettings"] = UNSET
    localization_settings: Union[Unset, "EnvironmentConfigLocalizationSettings"] = UNSET
    saml_settings: Union[Unset, "EnvironmentConfigSamlSettings"] = UNSET
    native_app_settings: Union[Unset, "EnvironmentConfigNativeAppSettings"] = UNSET
    cluster_settings: Union[Unset, "EnvironmentConfigClusterSettings"] = UNSET
    metrics_settings: Union[Unset, "EnvironmentConfigMetricsSettings"] = UNSET
    analytics_settings: Union[Unset, "EnvironmentConfigAnalyticsSettings"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.service_settings, Unset):
            service_settings = self.service_settings.to_dict()

        team_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.team_settings, Unset):
            team_settings = self.team_settings.to_dict()

        sql_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sql_settings, Unset):
            sql_settings = self.sql_settings.to_dict()

        log_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.log_settings, Unset):
            log_settings = self.log_settings.to_dict()

        password_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.password_settings, Unset):
            password_settings = self.password_settings.to_dict()

        file_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.file_settings, Unset):
            file_settings = self.file_settings.to_dict()

        email_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.email_settings, Unset):
            email_settings = self.email_settings.to_dict()

        rate_limit_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.rate_limit_settings, Unset):
            rate_limit_settings = self.rate_limit_settings.to_dict()

        privacy_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.privacy_settings, Unset):
            privacy_settings = self.privacy_settings.to_dict()

        support_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.support_settings, Unset):
            support_settings = self.support_settings.to_dict()

        git_lab_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.git_lab_settings, Unset):
            git_lab_settings = self.git_lab_settings.to_dict()

        google_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.google_settings, Unset):
            google_settings = self.google_settings.to_dict()

        office_365_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.office_365_settings, Unset):
            office_365_settings = self.office_365_settings.to_dict()

        ldap_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ldap_settings, Unset):
            ldap_settings = self.ldap_settings.to_dict()

        compliance_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.compliance_settings, Unset):
            compliance_settings = self.compliance_settings.to_dict()

        localization_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.localization_settings, Unset):
            localization_settings = self.localization_settings.to_dict()

        saml_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.saml_settings, Unset):
            saml_settings = self.saml_settings.to_dict()

        native_app_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.native_app_settings, Unset):
            native_app_settings = self.native_app_settings.to_dict()

        cluster_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cluster_settings, Unset):
            cluster_settings = self.cluster_settings.to_dict()

        metrics_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics_settings, Unset):
            metrics_settings = self.metrics_settings.to_dict()

        analytics_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.analytics_settings, Unset):
            analytics_settings = self.analytics_settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if service_settings is not UNSET:
            field_dict["ServiceSettings"] = service_settings
        if team_settings is not UNSET:
            field_dict["TeamSettings"] = team_settings
        if sql_settings is not UNSET:
            field_dict["SqlSettings"] = sql_settings
        if log_settings is not UNSET:
            field_dict["LogSettings"] = log_settings
        if password_settings is not UNSET:
            field_dict["PasswordSettings"] = password_settings
        if file_settings is not UNSET:
            field_dict["FileSettings"] = file_settings
        if email_settings is not UNSET:
            field_dict["EmailSettings"] = email_settings
        if rate_limit_settings is not UNSET:
            field_dict["RateLimitSettings"] = rate_limit_settings
        if privacy_settings is not UNSET:
            field_dict["PrivacySettings"] = privacy_settings
        if support_settings is not UNSET:
            field_dict["SupportSettings"] = support_settings
        if git_lab_settings is not UNSET:
            field_dict["GitLabSettings"] = git_lab_settings
        if google_settings is not UNSET:
            field_dict["GoogleSettings"] = google_settings
        if office_365_settings is not UNSET:
            field_dict["Office365Settings"] = office_365_settings
        if ldap_settings is not UNSET:
            field_dict["LdapSettings"] = ldap_settings
        if compliance_settings is not UNSET:
            field_dict["ComplianceSettings"] = compliance_settings
        if localization_settings is not UNSET:
            field_dict["LocalizationSettings"] = localization_settings
        if saml_settings is not UNSET:
            field_dict["SamlSettings"] = saml_settings
        if native_app_settings is not UNSET:
            field_dict["NativeAppSettings"] = native_app_settings
        if cluster_settings is not UNSET:
            field_dict["ClusterSettings"] = cluster_settings
        if metrics_settings is not UNSET:
            field_dict["MetricsSettings"] = metrics_settings
        if analytics_settings is not UNSET:
            field_dict["AnalyticsSettings"] = analytics_settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_config_analytics_settings import EnvironmentConfigAnalyticsSettings
        from ..models.environment_config_cluster_settings import EnvironmentConfigClusterSettings
        from ..models.environment_config_compliance_settings import EnvironmentConfigComplianceSettings
        from ..models.environment_config_email_settings import EnvironmentConfigEmailSettings
        from ..models.environment_config_file_settings import EnvironmentConfigFileSettings
        from ..models.environment_config_git_lab_settings import EnvironmentConfigGitLabSettings
        from ..models.environment_config_google_settings import EnvironmentConfigGoogleSettings
        from ..models.environment_config_ldap_settings import EnvironmentConfigLdapSettings
        from ..models.environment_config_localization_settings import EnvironmentConfigLocalizationSettings
        from ..models.environment_config_log_settings import EnvironmentConfigLogSettings
        from ..models.environment_config_metrics_settings import EnvironmentConfigMetricsSettings
        from ..models.environment_config_native_app_settings import EnvironmentConfigNativeAppSettings
        from ..models.environment_config_office_365_settings import EnvironmentConfigOffice365Settings
        from ..models.environment_config_password_settings import EnvironmentConfigPasswordSettings
        from ..models.environment_config_privacy_settings import EnvironmentConfigPrivacySettings
        from ..models.environment_config_rate_limit_settings import EnvironmentConfigRateLimitSettings
        from ..models.environment_config_saml_settings import EnvironmentConfigSamlSettings
        from ..models.environment_config_service_settings import EnvironmentConfigServiceSettings
        from ..models.environment_config_sql_settings import EnvironmentConfigSqlSettings
        from ..models.environment_config_support_settings import EnvironmentConfigSupportSettings
        from ..models.environment_config_team_settings import EnvironmentConfigTeamSettings

        d = dict(src_dict)
        _service_settings = d.pop("ServiceSettings", UNSET)
        service_settings: Union[Unset, EnvironmentConfigServiceSettings]
        if isinstance(_service_settings, Unset):
            service_settings = UNSET
        else:
            service_settings = EnvironmentConfigServiceSettings.from_dict(_service_settings)

        _team_settings = d.pop("TeamSettings", UNSET)
        team_settings: Union[Unset, EnvironmentConfigTeamSettings]
        if isinstance(_team_settings, Unset):
            team_settings = UNSET
        else:
            team_settings = EnvironmentConfigTeamSettings.from_dict(_team_settings)

        _sql_settings = d.pop("SqlSettings", UNSET)
        sql_settings: Union[Unset, EnvironmentConfigSqlSettings]
        if isinstance(_sql_settings, Unset):
            sql_settings = UNSET
        else:
            sql_settings = EnvironmentConfigSqlSettings.from_dict(_sql_settings)

        _log_settings = d.pop("LogSettings", UNSET)
        log_settings: Union[Unset, EnvironmentConfigLogSettings]
        if isinstance(_log_settings, Unset):
            log_settings = UNSET
        else:
            log_settings = EnvironmentConfigLogSettings.from_dict(_log_settings)

        _password_settings = d.pop("PasswordSettings", UNSET)
        password_settings: Union[Unset, EnvironmentConfigPasswordSettings]
        if isinstance(_password_settings, Unset):
            password_settings = UNSET
        else:
            password_settings = EnvironmentConfigPasswordSettings.from_dict(_password_settings)

        _file_settings = d.pop("FileSettings", UNSET)
        file_settings: Union[Unset, EnvironmentConfigFileSettings]
        if isinstance(_file_settings, Unset):
            file_settings = UNSET
        else:
            file_settings = EnvironmentConfigFileSettings.from_dict(_file_settings)

        _email_settings = d.pop("EmailSettings", UNSET)
        email_settings: Union[Unset, EnvironmentConfigEmailSettings]
        if isinstance(_email_settings, Unset):
            email_settings = UNSET
        else:
            email_settings = EnvironmentConfigEmailSettings.from_dict(_email_settings)

        _rate_limit_settings = d.pop("RateLimitSettings", UNSET)
        rate_limit_settings: Union[Unset, EnvironmentConfigRateLimitSettings]
        if isinstance(_rate_limit_settings, Unset):
            rate_limit_settings = UNSET
        else:
            rate_limit_settings = EnvironmentConfigRateLimitSettings.from_dict(_rate_limit_settings)

        _privacy_settings = d.pop("PrivacySettings", UNSET)
        privacy_settings: Union[Unset, EnvironmentConfigPrivacySettings]
        if isinstance(_privacy_settings, Unset):
            privacy_settings = UNSET
        else:
            privacy_settings = EnvironmentConfigPrivacySettings.from_dict(_privacy_settings)

        _support_settings = d.pop("SupportSettings", UNSET)
        support_settings: Union[Unset, EnvironmentConfigSupportSettings]
        if isinstance(_support_settings, Unset):
            support_settings = UNSET
        else:
            support_settings = EnvironmentConfigSupportSettings.from_dict(_support_settings)

        _git_lab_settings = d.pop("GitLabSettings", UNSET)
        git_lab_settings: Union[Unset, EnvironmentConfigGitLabSettings]
        if isinstance(_git_lab_settings, Unset):
            git_lab_settings = UNSET
        else:
            git_lab_settings = EnvironmentConfigGitLabSettings.from_dict(_git_lab_settings)

        _google_settings = d.pop("GoogleSettings", UNSET)
        google_settings: Union[Unset, EnvironmentConfigGoogleSettings]
        if isinstance(_google_settings, Unset):
            google_settings = UNSET
        else:
            google_settings = EnvironmentConfigGoogleSettings.from_dict(_google_settings)

        _office_365_settings = d.pop("Office365Settings", UNSET)
        office_365_settings: Union[Unset, EnvironmentConfigOffice365Settings]
        if isinstance(_office_365_settings, Unset):
            office_365_settings = UNSET
        else:
            office_365_settings = EnvironmentConfigOffice365Settings.from_dict(_office_365_settings)

        _ldap_settings = d.pop("LdapSettings", UNSET)
        ldap_settings: Union[Unset, EnvironmentConfigLdapSettings]
        if isinstance(_ldap_settings, Unset):
            ldap_settings = UNSET
        else:
            ldap_settings = EnvironmentConfigLdapSettings.from_dict(_ldap_settings)

        _compliance_settings = d.pop("ComplianceSettings", UNSET)
        compliance_settings: Union[Unset, EnvironmentConfigComplianceSettings]
        if isinstance(_compliance_settings, Unset):
            compliance_settings = UNSET
        else:
            compliance_settings = EnvironmentConfigComplianceSettings.from_dict(_compliance_settings)

        _localization_settings = d.pop("LocalizationSettings", UNSET)
        localization_settings: Union[Unset, EnvironmentConfigLocalizationSettings]
        if isinstance(_localization_settings, Unset):
            localization_settings = UNSET
        else:
            localization_settings = EnvironmentConfigLocalizationSettings.from_dict(_localization_settings)

        _saml_settings = d.pop("SamlSettings", UNSET)
        saml_settings: Union[Unset, EnvironmentConfigSamlSettings]
        if isinstance(_saml_settings, Unset):
            saml_settings = UNSET
        else:
            saml_settings = EnvironmentConfigSamlSettings.from_dict(_saml_settings)

        _native_app_settings = d.pop("NativeAppSettings", UNSET)
        native_app_settings: Union[Unset, EnvironmentConfigNativeAppSettings]
        if isinstance(_native_app_settings, Unset):
            native_app_settings = UNSET
        else:
            native_app_settings = EnvironmentConfigNativeAppSettings.from_dict(_native_app_settings)

        _cluster_settings = d.pop("ClusterSettings", UNSET)
        cluster_settings: Union[Unset, EnvironmentConfigClusterSettings]
        if isinstance(_cluster_settings, Unset):
            cluster_settings = UNSET
        else:
            cluster_settings = EnvironmentConfigClusterSettings.from_dict(_cluster_settings)

        _metrics_settings = d.pop("MetricsSettings", UNSET)
        metrics_settings: Union[Unset, EnvironmentConfigMetricsSettings]
        if isinstance(_metrics_settings, Unset):
            metrics_settings = UNSET
        else:
            metrics_settings = EnvironmentConfigMetricsSettings.from_dict(_metrics_settings)

        _analytics_settings = d.pop("AnalyticsSettings", UNSET)
        analytics_settings: Union[Unset, EnvironmentConfigAnalyticsSettings]
        if isinstance(_analytics_settings, Unset):
            analytics_settings = UNSET
        else:
            analytics_settings = EnvironmentConfigAnalyticsSettings.from_dict(_analytics_settings)

        environment_config = cls(
            service_settings=service_settings,
            team_settings=team_settings,
            sql_settings=sql_settings,
            log_settings=log_settings,
            password_settings=password_settings,
            file_settings=file_settings,
            email_settings=email_settings,
            rate_limit_settings=rate_limit_settings,
            privacy_settings=privacy_settings,
            support_settings=support_settings,
            git_lab_settings=git_lab_settings,
            google_settings=google_settings,
            office_365_settings=office_365_settings,
            ldap_settings=ldap_settings,
            compliance_settings=compliance_settings,
            localization_settings=localization_settings,
            saml_settings=saml_settings,
            native_app_settings=native_app_settings,
            cluster_settings=cluster_settings,
            metrics_settings=metrics_settings,
            analytics_settings=analytics_settings,
        )

        environment_config.additional_properties = d
        return environment_config

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
