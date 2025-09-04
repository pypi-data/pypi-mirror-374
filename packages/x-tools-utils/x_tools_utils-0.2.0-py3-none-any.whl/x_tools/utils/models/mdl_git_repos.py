""" Seznam Git Repositories """

from enum import StrEnum



class TGitRepos(StrEnum):
    """ Enum for Git Repositories. """
    # '0_doc'
    API_MANAGEMENT        = 'api_management'
    APPL_TEMPLATE         = 'appl_template'
    CKP_SHUTDOWN          = 'ckp_shutdown'
    CLOUDCONF_TOOL        = 'cloudconf_tool'
    DB_DEV_TOOLS          = 'db_dev_tools'
    DB_MONITOR            = 'db_monitor'
    DB_SYNC               = 'db_sync'
    DB_TOOLS              = 'db_tools'
    DEPLOY_SCRIPT         = 'deploy_script'
    DEPLOY_TC_API         = 'deploy_tc_api'
    ELPO_IIS_RESTART      = 'elpo_iis_restart'
    ESB_DEPLOY            = 'esb_deploy'
    GEFDB_DEPLOY          = 'gefdb_deploy'
    GEFDB_RELEASE         = 'gefdb_release'
    GEF_BE                = 'gef_be'
    GEF_RESTART_PROD      = 'gef_restart_prod'
    HUGO_CODELIST         = 'hugo_codelist'
    HUGO_ISV_CACHE        = 'hugo_isv_cache'
    HUGO_ON_OFF           = 'hugo_on_off'
    IIS_DEPLOY            = 'iis_deploy'
    IPORT_APPL_RESTART    = 'iport_appl_restart'
    IPORT_DQC_MONITORING  = 'iport_dqc_monitoring'
    IPORT_DWHTK_MONITORING= 'iport_dwhtk_monitoring'
    IPORT_FRAMEWORK       = 'iport_framework'
    IPORT_HUGO_CHECK      = 'iport_hugo_check'
    IPORT_HUGO_DB_SCRIPTS = 'iport_hugo_db_scripts'
    IPORT_IISCDU          = 'iport_iiscdu'
    IPORT_JOK             = 'iport_jok'
    IPORT_MAIL            = 'iport_mail'
    IPORT_MOCK_CLIENT     = 'iport_mock_client'
    IPORT_MONITORING      = 'iport_monitoring'
    JIRA_CONFLUENCE       = 'jira_confluence'
    JOK_RESTART_PROD      = 'jok_restart_prod'
    KCC                   = 'kcc'
    LIBS                  = 'libs'
    LIQUIBASE_DEPLOY      = 'liquibase_deploy'
    MFT_TOOL              = 'mft_tool'
    MFW_CDU               = 'mfw_cdu'
    MFW_GEF               = 'mfw_gef'
    MFW_GEF_PROD          = 'mfw_gef_prod'
    MFW_HUGO              = 'mfw_hugo'
    MFW_JOK               = 'mfw_jok'
    MFW_KDP               = 'mfw_kdp'
    MOBAXTERM_GIT         = 'mobaxterm_git'
    MONITORING_CLOUDCONF  = 'monitoring_cloudconf'
    MONITORING_TOMCAT     = 'monitoring_tomcat'
    PLS_AS_DATE           = 'pls_as_date'
    PLS_AS_RESTART        = 'pls_as_restart'
    PLS_DEPLOY            = 'pls_deploy'
    PLS_FTP_RESTART       = 'pls_ftp_restart'
    PLS_RELEASE           = 'pls_release'
    PLS_TOOLS             = 'pls_tools'
    PRINTNET_TEMPLATES    = 'printnet_templates'
    RELEASE_TOOL          = 'release_tool'
    RETARGET_DS           = 'retarget_ds'
    SERVICE_APPLICATION   = 'service_application'
    SIMPLE_SERVICE_APP    = 'simple_service_app'
    SWITCH_WEB_PROD       = 'switch_web_prod'
    TIA_DEPLOY            = 'tia_deploy'
    TIA_DS_RECONNECT      = 'tia_ds_reconnect'
    TIA_TOOLS             = 'tia_tools'
    WEB_PKS               = 'web_pks'
    X_TOOLS               = 'x_tools'


repos_all = [repo.value for repo in TGitRepos]

repos_of_ebr = [
    TGitRepos.GEF_BE,
    TGitRepos.IIS_DEPLOY,
    TGitRepos.MFW_GEF,
    TGitRepos.MFW_HUGO,
    TGitRepos.MONITORING_CLOUDCONF,
    TGitRepos.MONITORING_TOMCAT,
    TGitRepos.SERVICE_APPLICATION,
    ]

repos_of_osr = [
    TGitRepos.DB_MONITOR,
    TGitRepos.DB_SYNC,
    TGitRepos.DB_TOOLS,
    TGitRepos.DEPLOY_SCRIPT,
    TGitRepos.DEPLOY_TC_API,
    TGitRepos.GEFDB_DEPLOY,
    TGitRepos.GEFDB_RELEASE,
    TGitRepos.LIQUIBASE_DEPLOY,
    TGitRepos.PLS_DEPLOY,
    TGitRepos.PLS_RELEASE,
    TGitRepos.PLS_TOOLS,
    TGitRepos.RELEASE_TOOL,
    TGitRepos.TIA_DEPLOY,
    TGitRepos.TIA_TOOLS,
    ]
