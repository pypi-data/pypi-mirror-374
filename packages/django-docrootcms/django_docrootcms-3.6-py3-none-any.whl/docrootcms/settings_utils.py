# settings utilities to minimize code in the settings file
import pathlib


def app_is_installed(installed_apps: list, app_name: str) -> bool:
    if app_name in installed_apps:
        return True
    # if we don't have the appname exact lets look for starting with;
    #   ex: docroot.app.AppConfig
    for app in installed_apps:
        if app.startswith(f'{app_name}.'):
            return True
    return False
