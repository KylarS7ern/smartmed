from kivy.uix.screenmanager import ScreenManager

from smartmed.ui.screens.user_login_screen import UserLoginScreen
from smartmed.ui.screens.main_menu_screen import MainMenuScreen
from smartmed.ui.screens.status_screen import StatusScreen
from smartmed.ui.screens.plan_list_screen import PlanListScreen
from smartmed.ui.screens.log_screen import LogScreen
from smartmed.ui.screens.plan_edit_screen import PlanEintragErfassenScreen
from smartmed.ui.screens.settings_menu_screen import SettingsMenuScreen
from smartmed.ui.screens.patient_settings_screen import PatientSettingsScreen
from smartmed.ui.screens.settings_screen import SettingsScreen
from smartmed.ui.screens.advanced_settings_screen import AdvancedSettingsScreen


def build_screen_manager() -> ScreenManager:
    sm = ScreenManager()

    sm.add_widget(UserLoginScreen(name='login'))
    sm.add_widget(MainMenuScreen(name='menu'))
    sm.add_widget(StatusScreen(name='status'))
    sm.add_widget(PlanListScreen(name='plan_list'))
    sm.add_widget(LogScreen(name='log'))
    sm.add_widget(PlanEintragErfassenScreen(name='plan_edit'))

    sm.add_widget(SettingsMenuScreen(name='settings_menu'))
    sm.add_widget(PatientSettingsScreen(name='settings_patient'))
    sm.add_widget(SettingsScreen(name='settings'))
    sm.add_widget(AdvancedSettingsScreen(name='settings_advanced'))

    sm.current = 'login'
    return sm
