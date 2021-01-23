from . import settings as settings_module


# Settings context processor, so that certain settings can be accessed
# when rendering templates. See also TEMPLATES in settings.py.
def settings(request):
    selected_settings = {}
    return {"settings": selected_settings}
