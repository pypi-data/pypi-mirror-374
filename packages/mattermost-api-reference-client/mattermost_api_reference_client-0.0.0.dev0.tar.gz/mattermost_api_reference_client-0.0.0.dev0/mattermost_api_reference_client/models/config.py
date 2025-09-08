from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.config_analytics_settings import ConfigAnalyticsSettings
    from ..models.config_cluster_settings import ConfigClusterSettings
    from ..models.config_compliance_settings import ConfigComplianceSettings
    from ..models.config_email_settings import ConfigEmailSettings
    from ..models.config_file_settings import ConfigFileSettings
    from ..models.config_git_lab_settings import ConfigGitLabSettings
    from ..models.config_google_settings import ConfigGoogleSettings
    from ..models.config_ldap_settings import ConfigLdapSettings
    from ..models.config_localization_settings import ConfigLocalizationSettings
    from ..models.config_log_settings import ConfigLogSettings
    from ..models.config_metrics_settings import ConfigMetricsSettings
    from ..models.config_native_app_settings import ConfigNativeAppSettings
    from ..models.config_office_365_settings import ConfigOffice365Settings
    from ..models.config_password_settings import ConfigPasswordSettings
    from ..models.config_privacy_settings import ConfigPrivacySettings
    from ..models.config_rate_limit_settings import ConfigRateLimitSettings
    from ..models.config_saml_settings import ConfigSamlSettings
    from ..models.config_service_settings import ConfigServiceSettings
    from ..models.config_sql_settings import ConfigSqlSettings
    from ..models.config_support_settings import ConfigSupportSettings
    from ..models.config_team_settings import ConfigTeamSettings


T = TypeVar("T", bound="Config")


@_attrs_define
class Config:
    """
    Attributes:
        service_settings (Union[Unset, ConfigServiceSettings]):
        team_settings (Union[Unset, ConfigTeamSettings]):
        sql_settings (Union[Unset, ConfigSqlSettings]):
        log_settings (Union[Unset, ConfigLogSettings]):
        password_settings (Union[Unset, ConfigPasswordSettings]):
        file_settings (Union[Unset, ConfigFileSettings]):
        email_settings (Union[Unset, ConfigEmailSettings]):
        rate_limit_settings (Union[Unset, ConfigRateLimitSettings]):
        privacy_settings (Union[Unset, ConfigPrivacySettings]):
        support_settings (Union[Unset, ConfigSupportSettings]):
        git_lab_settings (Union[Unset, ConfigGitLabSettings]):
        google_settings (Union[Unset, ConfigGoogleSettings]):
        office_365_settings (Union[Unset, ConfigOffice365Settings]):
        ldap_settings (Union[Unset, ConfigLdapSettings]):
        compliance_settings (Union[Unset, ConfigComplianceSettings]):
        localization_settings (Union[Unset, ConfigLocalizationSettings]):
        saml_settings (Union[Unset, ConfigSamlSettings]):
        native_app_settings (Union[Unset, ConfigNativeAppSettings]):
        cluster_settings (Union[Unset, ConfigClusterSettings]):
        metrics_settings (Union[Unset, ConfigMetricsSettings]):
        analytics_settings (Union[Unset, ConfigAnalyticsSettings]):
    """

    service_settings: Union[Unset, "ConfigServiceSettings"] = UNSET
    team_settings: Union[Unset, "ConfigTeamSettings"] = UNSET
    sql_settings: Union[Unset, "ConfigSqlSettings"] = UNSET
    log_settings: Union[Unset, "ConfigLogSettings"] = UNSET
    password_settings: Union[Unset, "ConfigPasswordSettings"] = UNSET
    file_settings: Union[Unset, "ConfigFileSettings"] = UNSET
    email_settings: Union[Unset, "ConfigEmailSettings"] = UNSET
    rate_limit_settings: Union[Unset, "ConfigRateLimitSettings"] = UNSET
    privacy_settings: Union[Unset, "ConfigPrivacySettings"] = UNSET
    support_settings: Union[Unset, "ConfigSupportSettings"] = UNSET
    git_lab_settings: Union[Unset, "ConfigGitLabSettings"] = UNSET
    google_settings: Union[Unset, "ConfigGoogleSettings"] = UNSET
    office_365_settings: Union[Unset, "ConfigOffice365Settings"] = UNSET
    ldap_settings: Union[Unset, "ConfigLdapSettings"] = UNSET
    compliance_settings: Union[Unset, "ConfigComplianceSettings"] = UNSET
    localization_settings: Union[Unset, "ConfigLocalizationSettings"] = UNSET
    saml_settings: Union[Unset, "ConfigSamlSettings"] = UNSET
    native_app_settings: Union[Unset, "ConfigNativeAppSettings"] = UNSET
    cluster_settings: Union[Unset, "ConfigClusterSettings"] = UNSET
    metrics_settings: Union[Unset, "ConfigMetricsSettings"] = UNSET
    analytics_settings: Union[Unset, "ConfigAnalyticsSettings"] = UNSET
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
        from ..models.config_analytics_settings import ConfigAnalyticsSettings
        from ..models.config_cluster_settings import ConfigClusterSettings
        from ..models.config_compliance_settings import ConfigComplianceSettings
        from ..models.config_email_settings import ConfigEmailSettings
        from ..models.config_file_settings import ConfigFileSettings
        from ..models.config_git_lab_settings import ConfigGitLabSettings
        from ..models.config_google_settings import ConfigGoogleSettings
        from ..models.config_ldap_settings import ConfigLdapSettings
        from ..models.config_localization_settings import ConfigLocalizationSettings
        from ..models.config_log_settings import ConfigLogSettings
        from ..models.config_metrics_settings import ConfigMetricsSettings
        from ..models.config_native_app_settings import ConfigNativeAppSettings
        from ..models.config_office_365_settings import ConfigOffice365Settings
        from ..models.config_password_settings import ConfigPasswordSettings
        from ..models.config_privacy_settings import ConfigPrivacySettings
        from ..models.config_rate_limit_settings import ConfigRateLimitSettings
        from ..models.config_saml_settings import ConfigSamlSettings
        from ..models.config_service_settings import ConfigServiceSettings
        from ..models.config_sql_settings import ConfigSqlSettings
        from ..models.config_support_settings import ConfigSupportSettings
        from ..models.config_team_settings import ConfigTeamSettings

        d = dict(src_dict)
        _service_settings = d.pop("ServiceSettings", UNSET)
        service_settings: Union[Unset, ConfigServiceSettings]
        if isinstance(_service_settings, Unset):
            service_settings = UNSET
        else:
            service_settings = ConfigServiceSettings.from_dict(_service_settings)

        _team_settings = d.pop("TeamSettings", UNSET)
        team_settings: Union[Unset, ConfigTeamSettings]
        if isinstance(_team_settings, Unset):
            team_settings = UNSET
        else:
            team_settings = ConfigTeamSettings.from_dict(_team_settings)

        _sql_settings = d.pop("SqlSettings", UNSET)
        sql_settings: Union[Unset, ConfigSqlSettings]
        if isinstance(_sql_settings, Unset):
            sql_settings = UNSET
        else:
            sql_settings = ConfigSqlSettings.from_dict(_sql_settings)

        _log_settings = d.pop("LogSettings", UNSET)
        log_settings: Union[Unset, ConfigLogSettings]
        if isinstance(_log_settings, Unset):
            log_settings = UNSET
        else:
            log_settings = ConfigLogSettings.from_dict(_log_settings)

        _password_settings = d.pop("PasswordSettings", UNSET)
        password_settings: Union[Unset, ConfigPasswordSettings]
        if isinstance(_password_settings, Unset):
            password_settings = UNSET
        else:
            password_settings = ConfigPasswordSettings.from_dict(_password_settings)

        _file_settings = d.pop("FileSettings", UNSET)
        file_settings: Union[Unset, ConfigFileSettings]
        if isinstance(_file_settings, Unset):
            file_settings = UNSET
        else:
            file_settings = ConfigFileSettings.from_dict(_file_settings)

        _email_settings = d.pop("EmailSettings", UNSET)
        email_settings: Union[Unset, ConfigEmailSettings]
        if isinstance(_email_settings, Unset):
            email_settings = UNSET
        else:
            email_settings = ConfigEmailSettings.from_dict(_email_settings)

        _rate_limit_settings = d.pop("RateLimitSettings", UNSET)
        rate_limit_settings: Union[Unset, ConfigRateLimitSettings]
        if isinstance(_rate_limit_settings, Unset):
            rate_limit_settings = UNSET
        else:
            rate_limit_settings = ConfigRateLimitSettings.from_dict(_rate_limit_settings)

        _privacy_settings = d.pop("PrivacySettings", UNSET)
        privacy_settings: Union[Unset, ConfigPrivacySettings]
        if isinstance(_privacy_settings, Unset):
            privacy_settings = UNSET
        else:
            privacy_settings = ConfigPrivacySettings.from_dict(_privacy_settings)

        _support_settings = d.pop("SupportSettings", UNSET)
        support_settings: Union[Unset, ConfigSupportSettings]
        if isinstance(_support_settings, Unset):
            support_settings = UNSET
        else:
            support_settings = ConfigSupportSettings.from_dict(_support_settings)

        _git_lab_settings = d.pop("GitLabSettings", UNSET)
        git_lab_settings: Union[Unset, ConfigGitLabSettings]
        if isinstance(_git_lab_settings, Unset):
            git_lab_settings = UNSET
        else:
            git_lab_settings = ConfigGitLabSettings.from_dict(_git_lab_settings)

        _google_settings = d.pop("GoogleSettings", UNSET)
        google_settings: Union[Unset, ConfigGoogleSettings]
        if isinstance(_google_settings, Unset):
            google_settings = UNSET
        else:
            google_settings = ConfigGoogleSettings.from_dict(_google_settings)

        _office_365_settings = d.pop("Office365Settings", UNSET)
        office_365_settings: Union[Unset, ConfigOffice365Settings]
        if isinstance(_office_365_settings, Unset):
            office_365_settings = UNSET
        else:
            office_365_settings = ConfigOffice365Settings.from_dict(_office_365_settings)

        _ldap_settings = d.pop("LdapSettings", UNSET)
        ldap_settings: Union[Unset, ConfigLdapSettings]
        if isinstance(_ldap_settings, Unset):
            ldap_settings = UNSET
        else:
            ldap_settings = ConfigLdapSettings.from_dict(_ldap_settings)

        _compliance_settings = d.pop("ComplianceSettings", UNSET)
        compliance_settings: Union[Unset, ConfigComplianceSettings]
        if isinstance(_compliance_settings, Unset):
            compliance_settings = UNSET
        else:
            compliance_settings = ConfigComplianceSettings.from_dict(_compliance_settings)

        _localization_settings = d.pop("LocalizationSettings", UNSET)
        localization_settings: Union[Unset, ConfigLocalizationSettings]
        if isinstance(_localization_settings, Unset):
            localization_settings = UNSET
        else:
            localization_settings = ConfigLocalizationSettings.from_dict(_localization_settings)

        _saml_settings = d.pop("SamlSettings", UNSET)
        saml_settings: Union[Unset, ConfigSamlSettings]
        if isinstance(_saml_settings, Unset):
            saml_settings = UNSET
        else:
            saml_settings = ConfigSamlSettings.from_dict(_saml_settings)

        _native_app_settings = d.pop("NativeAppSettings", UNSET)
        native_app_settings: Union[Unset, ConfigNativeAppSettings]
        if isinstance(_native_app_settings, Unset):
            native_app_settings = UNSET
        else:
            native_app_settings = ConfigNativeAppSettings.from_dict(_native_app_settings)

        _cluster_settings = d.pop("ClusterSettings", UNSET)
        cluster_settings: Union[Unset, ConfigClusterSettings]
        if isinstance(_cluster_settings, Unset):
            cluster_settings = UNSET
        else:
            cluster_settings = ConfigClusterSettings.from_dict(_cluster_settings)

        _metrics_settings = d.pop("MetricsSettings", UNSET)
        metrics_settings: Union[Unset, ConfigMetricsSettings]
        if isinstance(_metrics_settings, Unset):
            metrics_settings = UNSET
        else:
            metrics_settings = ConfigMetricsSettings.from_dict(_metrics_settings)

        _analytics_settings = d.pop("AnalyticsSettings", UNSET)
        analytics_settings: Union[Unset, ConfigAnalyticsSettings]
        if isinstance(_analytics_settings, Unset):
            analytics_settings = UNSET
        else:
            analytics_settings = ConfigAnalyticsSettings.from_dict(_analytics_settings)

        config = cls(
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

        config.additional_properties = d
        return config

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
