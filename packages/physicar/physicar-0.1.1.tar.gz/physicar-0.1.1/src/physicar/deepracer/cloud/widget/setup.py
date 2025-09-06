def setup_widget():
    import os
    import ipywidgets as widgets
    from IPython.display import display
    from physicar.deepracer.cloud.utils import (
        get_language, 
        get_time_zone, 
    )
    
    current_dir = os.getcwd()
    expected_dir = os.path.expanduser("~/physicar-deepracer-for-cloud")
    if not os.path.samefile(current_dir, expected_dir):
        return None
    
    from IPython.display import display
    import ipywidgets as widgets
    from physicar.deepracer.cloud.constants import SUPPORTED_LANGUAGES, SUPPORTED_TIMEZONES
    from physicar.deepracer.cloud.utils import get_language, set_language, get_time_zone, set_time_zone

    display(widgets.VBox([
        widgets.HTML("<h3>Language</h3>"),
        lang := widgets.Dropdown(
            options={k + f" ({v})":k for k,v in SUPPORTED_LANGUAGES.items()}, 
            value=get_language(),
            description=""
        ),
    ]))

    lang.observe(lambda change: set_language(change['new']), names='value')

    display(widgets.VBox([
        widgets.HTML("<h3>Time Zone</h3>"),
        time_zone := widgets.Dropdown(
            options=SUPPORTED_TIMEZONES, 
            value=get_time_zone(),
            description=""
        ),
    ]))

    time_zone.observe(lambda change: set_time_zone(change['new']), names='value')