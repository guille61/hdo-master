from flask_wtf import FlaskForm
import ldap
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from .config import LDAP_HOST, LDAP_BASE, READ_GROUP, WRITE_GROUP

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw = {"placeholder": "Usuario", "autofocus": None})
    password = PasswordField('Password', validators=[DataRequired()], render_kw = {"placeholder": "Contraseña"})
    submit = SubmitField('Login')

    def validate_username(self, field):
        
        # Esto esta comentado para poder probar sin validr contra el dominio.

        #try:
        #    conn = ldap.initialize(LDAP_HOST)
        #except ldap.SERVER_DOWN as e:
        #    raise ValidationError("Error de conexión con el dominio. Contactar con HDO.")
        
        #conn.set_option(ldap.OPT_REFERRALS, 0)

        #try:
        #    conn.simple_bind_s(f"kostales\\{self.username.data}", self.password.data)
        #except ldap.INVALID_CREDENTIALS:
        #    raise ValidationError("Usuario y/o contraseña incorrecta.")
        
        #result = conn.search_s(base = LDAP_BASE, scope = ldap.SCOPE_SUBTREE, filterstr = f"name={self.username.data}", attrlist = ["name", "memberof"])
        
        result = [('CN=perez014,OU=Azure Sync,OU=SE,OU=USR,DC=es,DC=kostal,DC=int', {'memberOf': [b'CN=R_HDO,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=Acronis_MA_Admin,OU=Acronis,OU=Groups,DC=ma,DC=kostal,DC=int', b'CN=l__VOL1_HP_Formaci\xc3\xb3n_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=Office_Printer,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_LinuxUsers,OU=Firewall,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=lnxadminses,OU=Linux,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=essehdo05_RDP,OU=LocalDevicePermissions,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_VNC_HDO,OU=VNC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA: L\xc3\xadneas M\xc3\xb3vil,CN=Users,DC=kostal,DC=int', b'CN=l__F_FOD_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__HP_HP2_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__HP_HP1_HP1.2_POLICOMPETENCIA_Fotos personal_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__HP_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_HDO,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_KEMA_Read,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__VOL1_APE_APP2_Kospa Projects Information_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BYT_LocalAdminUser_KAE,OU=BeyondTrust,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__VOL1_AQ_AQT_AQL_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ESSE_WLAN_SPONSOR,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=R_SPAREPARTS,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=es_mail_enabled_users,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ESSE_UC-Cluster-EMEA-Advanced-Service-Users,OU=UC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__F_FB_01_CONTROLLING_02_FORECAST_FOR _TOP7_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__VOL1_PUBLICO_PL_TOP7_re,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA: CERT,OU=Lista de distribuci\xc3\xb3n,OU=USR,DC=es,DC=kostal,DC=int', b'CN=W_KOSPASIS,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=MA_DPO_SUPERVISOR,OU=MATA,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_Record_Meetings_NOT_ALLOWED,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=global_adfs_dracoon_prod_es,OU=ADFS,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=LC_ES_User,OU=LineControlling,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=l__USER_SG4_vazque01_Sara_md,OU=essesan001.es.kostal.int,OU=8MAN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_MS-Teams_Users,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA: HomeOffice_1,OU=Lista de distribuci\xc3\xb3n,OU=USR,DC=es,DC=kostal,DC=int', b'CN=KOSPA: HDO,OU=Lista de distribuci\xc3\xb3n,OU=USR,DC=es,DC=kostal,DC=int', b'CN=VPN_Extended_Users_ES,OU=VPN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=W_REWORK,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=es_passwordsafe_users_HDO1,OU=PasswordSafe,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=AQP_READ_INTRANET,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=HDO_USERS_INTRANET,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=VPN_RAS_ES,OU=VPN,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA_HD_ALL,OU=SE,OU=USR,DC=es,DC=kostal,DC=int', b'CN=GRP_ALL_BMC_12.0_Active_Admins,OU=BMC,OU=Groups,DC=kostal,DC=int', b'CN=KOSPA_HDO,OU=SE,OU=USR,DC=es,DC=kostal,DC=int', b'CN=MA_Hardware_Agents,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_SecureDiskHelpdesk,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=Workstation_Administrators_ES,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=MA_Software_Agents,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BMC_Patchmanagement_Prod,OU=BMC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BMC_Patchmanagement_Test,OU=BMC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BMC_ServiceDesk_Prod,OU=BMC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BMC_ServiceDesk_Test,OU=BMC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BMC_Operator_Prod,OU=BMC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_BMC_Operator_Test,OU=BMC,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=Airwatch_User_ES,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=PasswordPolicy_Administrators,CN=Users,DC=es,DC=kostal,DC=int', b'CN=PasswordPolicy_ServiceAccounts,CN=Users,DC=es,DC=kostal,DC=int', b'CN=es_Collab_and_NetworkingUsers,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ALL_CDB_User,OU=Groups,DC=kostal,DC=int', b'CN=VPN_ExternalAllowed,OU=Groups,DC=kostal,DC=int', b'CN=ES_Hardware_Agents,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_Software_Agents,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=W_ESD_INTRANET,OU=INTRANET,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=W_MATA,OU=MATA,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=MATA_MAP,OU=MATA,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=InternetUser,CN=Users,DC=kostal,DC=int', b'CN=InternetAccessAdmins,CN=Users,DC=kostal,DC=int', b'CN=HDOInternational,OU=H,OU=Verteiler,OU=USR,DC=de,DC=kostal,DC=int', b'CN=W_F_FOD,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA: Inform\xc3\xa1tica,OU=Lista de distribuci\xc3\xb3n,OU=USR,DC=es,DC=kostal,DC=int', b'CN=R_DPO_HFD,OU=DPO,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_WLAN_ACCESS,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=ES_InternetAdminUser,CN=Users,DC=es,DC=kostal,DC=int', b'CN=DimNetGuests,OU=DimNet,OU=Iquidoss,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA_IT,OU=SE,OU=USR,DC=es,DC=kostal,DC=int', b'CN=ES_InternetEMailUser,CN=Users,DC=es,DC=kostal,DC=int', b'CN=DossierUsers,OU=Dossier,OU=Iquidoss,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=8dprUsers,OU=8dpr,OU=Iquidoss,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=F_USERS,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=NAS_MANTEN,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=EVERYONE,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=EVERYBODY,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=KOSPA: Users,OU=Lista de distribuci\xc3\xb3n,OU=USR,DC=es,DC=kostal,DC=int', b'CN=IT,OU=Groups,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=APPL_W,OU=Volumes,OU=Groups,DC=es,DC=kostal,DC=int', b'CN=HelpDesk,CN=Users,DC=es,DC=kostal,DC=int'], 'name': [b'perez014']})]
        # -----------------------------------------------------------------------------

        if not result:
            raise ValidationError("No se han encontrado datos para este usuario.")
        
        memberof = [x.decode("utf-8").split("CN=")[1].split(",")[0] for x in result[0][1]["memberOf"]]

        if READ_GROUP not in memberof and WRITE_GROUP not in memberof:
            raise ValidationError("Usuario sin permisos para acceder a la aplicación.")
