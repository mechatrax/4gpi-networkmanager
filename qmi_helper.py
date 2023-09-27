import sys, gi

gi.require_version('Qmi', '1.0')
from gi.repository import Gio, GLib, Qmi


DEFAULT_TIMEOUT = 10
SET_OPERATING_MODE_TIMEOUT = 30

# Cannot access member of '3GPP' due to 'SyntaxError: invalid decimal literal'
QMI_WDS_PROFILE_TYPE_3GPP = getattr(Qmi.WdsProfileType, '3GPP')


class QmiHelper():
    def __init__(self):
        self._err = None
        self._loop = None
        self._timeout = None
    
    def _quit_loop(self):
        self._timeout = None
        self._loop.quit()
    
    
    def _sync(self, timeout_sec=30):
        self._loop = GLib.MainLoop()
        self._timeout = GLib.timeout_add_seconds(timeout_sec, self._quit_loop)
        self._loop.run()
        if self._timeout:
            GLib.source_remove(self._timeout)
        if self._err:
            raise self._err
   
    
class QmiDeviceHelper(QmiHelper):
    def __init__(self, path):
        super().__init__()
        self._dev = None
        
        file = Gio.File.new_for_path(path)
        Qmi.Device.new(file, None, self._device_new_ready, None)
        self._sync()
    
    
    def _device_close_ready(self, qmi_dev, res, user_data=None):
        try:
            qmi_dev.close_finish(res)
            self._dev = None
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()

    
    def _device_open_ready(self, qmi_dev, res, user_data=None):
        try:
            qmi_dev.open_finish(res)
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()
    
    
    def _device_new_ready(self, unused, res, user_data=None):
        try:
            self._dev = Qmi.Device.new_finish(res)
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()


    def open_sync(self):
        self._dev.open(Qmi.DeviceOpenFlags.PROXY, DEFAULT_TIMEOUT, None, self._device_open_ready, None)
        self._sync()
    
    
    def close_sync(self):
        self._dev.close_async(DEFAULT_TIMEOUT, None, self._device_close_ready, None)
        self._sync()
    
    
    def get_device(self):
        return self._dev


class QmiClientHelper(QmiHelper):
    def __init__(self, qmi_dev, service):
        super().__init__()
        self._dev = qmi_dev
        self._service = service
        self._client = None
    
    
    def _client_alloc_ready(self, qmi_dev, res, user_data=None):
        try:
            self._client = qmi_dev.allocate_client_finish(res)
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()
    
    
    def _client_release_ready(self, qmi_client, res, user_data=None):
        try:
            qmi_client.release_client_finish(res)
            self._client = None
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()
    
    
    def client_allocate_sync(self):
        self._dev.allocate_client(self._service, Qmi.CID_NONE, DEFAULT_TIMEOUT, None, self._client_alloc_ready, None)
        self._sync()
    
    
    def client_release_sync(self):
        self._dev.release_client(self._client, Qmi.DeviceReleaseClientFlags.RELEASE_CID, DEFAULT_TIMEOUT, None, self._client_release_ready, None)
        self._sync()


class QmiClientDmsHelper(QmiClientHelper):
    def __init__(self, dev):
        super().__init__(dev, Qmi.Service.DMS)


    def _set_operating_mode_ready(self, qmi_client_dms, res, user_data=None):
        try:
            output = qmi_client_dms.set_operating_mode_finish(res)
            output.get_result()
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()


    def operating_mode_online_sync(self):
        input = Qmi.MessageDmsSetOperatingModeInput.new()
        input.set_mode(Qmi.DmsOperatingMode.ONLINE)
        self._client.set_operating_mode(input, SET_OPERATING_MODE_TIMEOUT, None, self._set_operating_mode_ready, None)
        self._sync()


    def operating_mode_lowpower_sync(self):
        input = Qmi.MessageDmsSetOperatingModeInput.new()
        input.set_mode(Qmi.DmsOperatingMode.LOW_POWER)
        self._client.set_operating_mode(input, SET_OPERATING_MODE_TIMEOUT, None, self._set_operating_mode_ready, None)
        self._sync()


class QmiClientWdsHelper(QmiClientHelper):
    def __init__(self, dev):
        super().__init__(dev, Qmi.Service.WDS)
        self._default_settings = None
        self._profile_list = None
        
    
    def _create_profile_ready(self, qmi_client_wds, res, user_data=None):
        try:
            output = qmi_client_wds.create_profile_finish(res)
            output.get_result()
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()


    def _modify_profile_ready(self, qmi_client_wds, res, user_data=None):
        try:
            output = qmi_client_wds.modify_profile_finish(res)
            output.get_result()
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()


    def _get_default_settings_ready(self, qmi_client_wds, res, user_data=None):
        try:
            output = qmi_client_wds.get_default_settings_finish(res)
            output.get_result()
            self._default_settings = output
        except GLib.GError as gerr:
            self._err = gerr

        self._quit_loop()
        
        
    def _get_profile_list_ready(self, qmi_client_wds, res, user_data=None):
        try:
            output = qmi_client_wds.get_profile_list_finish(res)
            output.get_result()
            self._profile_list = output.get_profile_list()
        except GLib.GError as gerr:
            self._err = gerr
    
        self._quit_loop()

    
    def create_profile_sync(self, apn, pdp, user='', passwd='', auth=Qmi.WdsAuthentication.NONE):
        input = Qmi.MessageWdsCreateProfileInput.new()
        input.set_profile_type(QMI_WDS_PROFILE_TYPE_3GPP)
        input.set_apn_name(apn)
        input.set_pdp_type(pdp)
        input.set_username(user)
        input.set_password(passwd)
        input.set_authentication(auth)
        
        self._client.create_profile(input, DEFAULT_TIMEOUT, None, self._create_profile_ready, None)
        self._sync()
        
    
    def modify_profile_sync(self, apn, pdp, user='', passwd='', auth=Qmi.WdsAuthentication.NONE, id=1):
        input = Qmi.MessageWdsModifyProfileInput.new()
        input.set_profile_identifier(QMI_WDS_PROFILE_TYPE_3GPP, id)
        input.set_apn_name(apn)
        input.set_pdp_type(pdp)
        input.set_username(user)
        input.set_password(passwd)
        input.set_authentication(auth)
        
        self._client.modify_profile(input, DEFAULT_TIMEOUT, None, self._modify_profile_ready, None)
        self._sync()
        
        
    def get_default_settings_sync(self):
        input = Qmi.MessageWdsGetDefaultSettingsInput.new()
        input.set_profile_type(QMI_WDS_PROFILE_TYPE_3GPP)
        self._client.get_default_settings(input, DEFAULT_TIMEOUT, None, self._get_default_settings_ready, None)
        self._sync()
        
        return self._default_settings
    
    
    def get_profile_list_sync(self):
        input = Qmi.MessageWdsGetProfileListInput.new()
        input.set_profile_type(QMI_WDS_PROFILE_TYPE_3GPP)
        
        self._client.get_profile_list(input, DEFAULT_TIMEOUT, None, self._get_profile_list_ready, None)
        self._sync()
        
        return self._profile_list


