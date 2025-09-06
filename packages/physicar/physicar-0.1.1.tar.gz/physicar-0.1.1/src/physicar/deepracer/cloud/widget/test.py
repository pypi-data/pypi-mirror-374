def test_widget():
    import os
    current_dir = os.getcwd()
    expected_dir = os.path.expanduser("~/physicar-deepracer-for-cloud")
    if not os.path.samefile(current_dir, expected_dir):
        return None
    
    import ipywidgets as widgets
    from IPython.display import display
    from physicar.deepracer.cloud.config_validation import (
        get_tracks_info, 
        ConfigValidationError
    )
    from physicar.deepracer.cloud.constants import DATA_URL, DATA_PATH
    from physicar.deepracer.cloud.utils import (
        get_language, 
        get_time_zone, 
        get_model_list,
    )
    from physicar.deepracer.cloud.run import TestJob
    
    def get_img_widget(path, **kwargs):
        img_format = path.split(".")[-1].lower().strip()
        img_format = "jpeg" if img_format == "jpg" else img_format

        if img_format == "svg":
            with open(path, "r", encoding="utf-8") as f:
                svg_html = f.read()
                img = widgets.HTML(
                    value=svg_html,
                    **kwargs
                )
        else:
            with open(path, "rb") as f:
                img_bytes = f.read()
            img = widgets.Image(
                value=img_bytes, 
                format=img_format,
                **kwargs
            )
        return img

    lang = get_language()
    time_zone = get_time_zone()
    tracks_info = get_tracks_info()

    ####### Model Selection #####
    model_name_options = {model_info["ModelName"]:model_info["ModelName"] for model_info in get_model_list(time_zone) if model_info["Status"] in ["ready", "training", "testing", "stopping"]}
    
    display(
        widgets.VBox([
            widgets.HTML(f"<h2>--- Test Model ---</h2>"),
            model_name := widgets.Dropdown(
                options=model_name_options,
                value=list(model_name_options.keys())[0] if model_name_options else None,
                description="Test Model Name:",
                style={'description_width': '130px'},
                layout=widgets.Layout(width="auto", max_width="100%"),
                disabled=not bool(model_name_options)
            ),
        ])
    )

    ####### Simulation Settings #####
    display(
        widgets.VBox([
            widgets.HTML(f"<h2>--- Test Simulation ---</h2>"),
            widgets.HBox([
                widgets.VBox([
                    track_id := widgets.Dropdown(
                        options={f"[{i+1:02d}] {v['track_name']}": k for i, (k, v) in enumerate(tracks_info.items())},
                        value="2024_reinvent_champ",
                        description="Track:",
                        style={'description_width': '120px'},
                        layout=widgets.Layout(margin="10px 0")
                    ),
                    track_direction := widgets.Dropdown(
                        options=["counterclockwise", "clockwise"],
                        value="counterclockwise",
                        description="Direction:",
                        style={'description_width': '120px'}
                    ),
                    race_type := widgets.Dropdown(
                        options={
                            "Time Trial": "time_trial",
                            "Object Avoidance": "object_avoidance"
                        },
                        value="time_trial",
                        description="Race Type:",
                        style={'description_width': '120px'}
                    ),
                ], layout=widgets.Layout(width="60%")),
                track_img := get_img_widget(
                    os.path.join(DATA_PATH, "tracks", "thumbnail", "2024_reinvent_champ.svg"),
                    layout=widgets.Layout(width="40%", max_height="180px", margin="10px")
                )
            ]),
        ])
    )

    ####### Object Avoidance Settings #####
    display(
        object_avoidance_settings := widgets.VBox([
            widgets.HTML("<h3>Object Avoidance</h3>"),
            object_type := widgets.Dropdown(
                options={
                    "Box": "box",
                    "DeepRacer Box": "deepracer_box", 
                    "DeepRacer Car": "deepracer_car",
                    "Amazon Box": "amazon_box"
                },
                value="box",
                description="Object Type:",
                style={'description_width': '150px'}
            ),
            number_of_objects := widgets.Dropdown(
                options=list(range(1, 11)),
                value=3,
                description="Number of Objects:",
                style={'description_width': '150px'}
            ),
            randomize_object_locations := widgets.Checkbox(
                value=True,
                description="Randomize Object Locations"
            ),
            object_locations_container := widgets.VBox([
                widgets.HTML("<h4>Object Locations</h4>"),
                object_locations_widgets := widgets.VBox([])
            ])
        ])
    )

    # Object locations widgets 생성
    def create_object_location_widgets(num_objects):
        location_widgets = []
        progress_interval = 100/(num_objects+1)
        
        for i in range(num_objects):
            progress_value = round(progress_interval * (i+1))
            lane_value = "outside" if i%2==0 else "inside"
            
            location_widget = widgets.HBox([
                widgets.HTML(f"Object {i}", layout=widgets.Layout(width="70px")),
                widgets.BoundedFloatText(
                    value=float(progress_value),
                    min=0.0, max=100.0, step=1.0,
                    description='Progress (%):',
                    style={'description_width': '80px'}
                ),
                widgets.Dropdown(
                    options=["inside", "outside"],
                    value=lane_value,
                    description='Lane:',
                    style={'description_width': '50px'}
                )
            ])
            location_widgets.append(location_widget)
        
        return location_widgets

    # 초기 object locations 설정
    def update_object_locations():
        if randomize_object_locations.value:
            object_locations_container.layout.display = "none"
        else:
            object_locations_container.layout.display = "flex"
            num_objects = number_of_objects.value
            object_locations_widgets.children = create_object_location_widgets(num_objects)

    ####### Test Settings #####
    display(
        widgets.VBox([
            widgets.HTML("<h2>--- Test Settings ---</h2>"),
            number_of_trials := widgets.Dropdown(
                options=list(range(1, 21)),
                value=3,
                description="Number of Trials:",
                style={'description_width': '150px'}
            ),
            checkpoint := widgets.Dropdown(
                options=["best", "last"],
                value="last",
                description="Checkpoint:",
                style={'description_width': '150px'}
            ),
            widgets.HTML("<h3>Penalty Settings</h3>"),
            is_offtrack_penalty := widgets.BoundedFloatText(
                value=3.0,
                min=0.0, max=60.0, step=0.1,
                description="Off-track Penalty (sec):",
                style={'description_width': '150px'}
            ),
            is_crashed_penalty := widgets.BoundedFloatText(
                value=5.0,
                min=0.0, max=60.0, step=0.1,
                description="Crash Penalty (sec):",
                style={'description_width': '150px'}
            ),
        ])
    )

    # Event handlers
    def _update_track_img(change):
        track_id_value = change["new"]
        track_info = tracks_info[track_id_value]
        track_thumbnail = track_info['thumbnail']
        track_img.value = f'<img src="{DATA_URL}/tracks/thumbnail/{track_thumbnail}">'

    def _update_track_direction(change):
        track_id_value = change["new"]
        track_info = tracks_info[track_id_value]
        valid_directions = track_info['track_direction']
        track_direction.options = valid_directions
        if track_direction.value not in valid_directions:
            track_direction.value = valid_directions[0]

    def _update_object_avoidance_visibility(change):
        if change["new"] == "object_avoidance":
            object_avoidance_settings.layout.display = "flex"
        else:
            object_avoidance_settings.layout.display = "none"

    def _update_object_locations_visibility(change):
        update_object_locations()

    def _update_object_locations_count(change):
        if not randomize_object_locations.value:
            update_object_locations()

    # 이벤트 리스너 등록
    track_id.observe(_update_track_img, names="value")
    track_id.observe(_update_track_direction, names="value")
    race_type.observe(_update_object_avoidance_visibility, names="value")
    randomize_object_locations.observe(_update_object_locations_visibility, names="value")
    number_of_objects.observe(_update_object_locations_count, names="value")

    # 초기 상태 설정
    _update_object_avoidance_visibility({"new": race_type.value})
    update_object_locations()

    # Global variable for test job
    test_job = None

    ####### Test Execution #####
    display(
        widgets.VBox([
            widgets.HTML("<h2>=== Start Test ===</h2>"),
            widgets.HBox([
                start_test_button := widgets.Button(
                    description="Start Test",
                    button_style='success',
                    icon='play',
                    layout=widgets.Layout(width="200px"),
                    style={'description_width': 'initial', 'button_color': None, 'font_weight': 'normal'},
                    disabled=not bool(model_name_options)
                ),
                start_button_spinner := widgets.HTML("", layout=widgets.Layout(margin="10px 0 0 10px")),
            ]),
            error_message := widgets.HTML("", layout=widgets.Layout(margin="10px 0 0 0")),
            warning_message := widgets.HTML("", layout=widgets.Layout(margin="10px 0 0 0")),
            widgets.HBox([
                continue_button := widgets.Button(
                    description="Continue",
                    button_style='info',
                    icon='forward',
                    layout=widgets.Layout(width="200px"),
                    style={'description_width': 'initial', 'button_color': None, 'font_weight': 'normal'},
                    disabled=True,
                ),
                cancel_button := widgets.Button(
                    description="Cancel",
                    button_style='danger',
                    icon='times',
                    layout=widgets.Layout(width="200px", margin="0 0 0 10px"),
                    style={'description_width': 'initial', 'button_color': None, 'font_weight': 'normal'},
                    disabled=True,
                ),
                continue_button_spinner := widgets.HTML("", layout=widgets.Layout(margin="10px 0 0 10px")),
            ]),
            success_message := widgets.HTML("", layout=widgets.Layout(margin="10px 0 0 0")),
        ])
    )
    continue_button.layout.display = "none"
    cancel_button.layout.display = "none"

    # 버튼 아이콘 정렬을 위한 CSS 스타일 추가
    from IPython.display import HTML
    display(HTML("""
    <style>
    .widget-button .fa {
        vertical-align: middle;
        margin-right: 5px;
        display: inline-block;
        line-height: 1;
    }
    .widget-button {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .widget-button .widget-label {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """))

    def get_test_config():
        config = {
            "model_name": model_name.value,
            "simulation": {
                "main": {
                    "track_id": track_id.value,
                    "track_direction": track_direction.value,
                    "race_type": race_type.value
                }
            },
            "test": {
                "number_of_trials": number_of_trials.value,
                "checkpoint": checkpoint.value,
                "penalty": {
                    "is_offtrack": is_offtrack_penalty.value,
                    "is_crashed": is_crashed_penalty.value
                }
            }
        }
        
        if race_type.value == "object_avoidance":
            config["simulation"]["main"]["object_avoidance"] = {
                "object_type": object_type.value,
                "number_of_objects": number_of_objects.value,
                "randomize_object_locations": randomize_object_locations.value
            }
            
            if not randomize_object_locations.value:
                object_locations = []
                for i in range(number_of_objects.value):
                    if i < len(object_locations_widgets.children):
                        location_widget = object_locations_widgets.children[i]
                        progress_widget = location_widget.children[1]
                        lane_widget = location_widget.children[2]
                        object_locations.append({
                            "progress": progress_widget.value,
                            "lane": lane_widget.value
                        })
                config["simulation"]["main"]["object_avoidance"]["object_locations"] = object_locations
        
        return config

    def start_test(button):
        global test_job
        start_test_button.disabled = True
        start_button_spinner.value = "<i class='fa fa-spinner fa-spin'></i>"
        error_message.value = ""
        warning_message.value = ""
        success_message.value = ""
        
        try:
            test_job = TestJob(
                config=get_test_config(),
                lang=lang,
            )
        except ConfigValidationError as e:
            error = {  
                "error_type": "ConfigValidationError",
                "error_message": str(e).strip(),  
                "error_config_path": e.config_path,
                "error_value": e.value,  
            }
            error_message.value = f"""
            <div style='background-color: #ffe6e6; border: 1px solid #ff6b6b; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #d63031; margin: 0 0 10px 0;'><i class='fa fa-exclamation-triangle'></i> Configuration Error</h4>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Message:</strong> {error['error_message']}</p>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Path:</strong> {error['error_config_path']}</p>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Value:</strong> {error['error_value']}</p>
            </div>
            """
            start_test_button.disabled = False
            start_button_spinner.value = ""
            return
        except Exception as e:
            error = {
                "error_type": e.__class__.__name__,
                "error_message": str(e).strip(),
            } 
            error_message.value = f"""
            <div style='background-color: #ffe6e6; border: 1px solid #ff6b6b; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #d63031; margin: 0 0 10px 0;'><i class='fa fa-exclamation-triangle'></i> Unexpected Error</h4>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Type:</strong> {error['error_type']}</p>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Message:</strong> {error['error_message']}</p>
            </div>
            """
            start_test_button.disabled = False
            start_button_spinner.value = ""
            return

        if test_job.warnings:
            warning_html = """
            <div style='background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #856404; margin: 0 0 10px 0;'><i class='fa fa-exclamation-circle'></i> Warnings</h4>
                <p style='margin: 5px 0; color: #856404;'>Please check the following warnings before proceeding.</p>
            """
            for i, warning in enumerate(test_job.warnings):
                warning_title = warning.get('title', 'Warning')
                warning_message_text = warning.get('message', str(warning))
                warning_html += f"""
                <div style='background-color: #fff; border-left: 3px solid #ffc107; padding: 10px; margin: 10px 0;'>
                    <strong>{warning_title}</strong><br>
                    <span style='color: #6c757d;'>{warning_message_text}</span>
                </div>
                """
            warning_html += "</div>"
            warning_message.value = warning_html
            
            start_test_button.layout.display = "none"
            start_test_button.disabled = False
            start_button_spinner.value = ""
            continue_button.layout.display = "inline-flex"
            continue_button.disabled = False
            cancel_button.layout.display = "inline-flex"
            cancel_button.disabled = False
        else:
            output_model_name = test_job.start()
            success_message.value = f"""
            <div style='background-color: #d4edda; border: 1px solid #28a745; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #155724; margin: 0 0 10px 0;'><i class='fa fa-check-circle'></i> Test Started!</h4>
                <p style='margin: 5px 0; color: #155724;'><strong>Model Name:</strong> {output_model_name}</p>
                <p style='margin: 5px 0; color: #6c757d;'>Test has started successfully.</p>
                <p style='margin: 10px 0 5px 0; color: #155724;'>
                    <a href="02_your_models.ipynb" target="_blank" 
                       style="display: inline-block; padding: 8px 16px; background-color: #007acc; 
                              color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        📊 Monitor Test Progress
                    </a>
                </p>
            </div>
            """
            start_test_button.disabled = False
            start_test_button.layout.display = "inline-flex"
            start_button_spinner.value = ""
            continue_button.disabled = True
            continue_button.layout.display = "none"
            cancel_button.disabled = True
            cancel_button.layout.display = "none"

    def _continue_button_clicked(b):
        global test_job
        continue_button.disabled = True
        cancel_button.disabled = True
        cancel_button.layout.display = "none"
        continue_button_spinner.value = "<i class='fa fa-spinner fa-spin'></i>"
        warning_message.value = ""
        
        try:
            output_model_name = test_job.start()
            success_message.value = f"""
            <div style='background-color: #d4edda; border: 1px solid #28a745; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #155724; margin: 0 0 10px 0;'><i class='fa fa-check-circle'></i> Test Started!</h4>
                <p style='margin: 5px 0; color: #155724;'><strong>Model Name:</strong> {output_model_name}</p>
                <p style='margin: 5px 0; color: #6c757d;'>Test has started successfully despite warnings.</p>
                <p style='margin: 10px 0 5px 0; color: #155724;'>
                    <a href="02_your_models.ipynb" target="_blank" 
                       style="display: inline-block; padding: 8px 16px; background-color: #007acc; 
                              color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        📊 Monitor Test Progress
                    </a>
                </p>
            </div>
            """
            start_test_button.disabled = False
            start_test_button.layout.display = "inline-flex"
            continue_button_spinner.value = ""
            continue_button.disabled = True
            continue_button.layout.display = "none"
            cancel_button.disabled = True
            cancel_button.layout.display = "none"
        except Exception as e:
            error_message.value = f"""
            <div style='background-color: #ffe6e6; border: 1px solid #ff6b6b; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #d63031; margin: 0 0 10px 0;'><i class='fa fa-exclamation-triangle'></i> Test Failed</h4>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Error:</strong> {str(e)}</p>
            </div>
            """
            start_test_button.disabled = False
            start_test_button.layout.display = "inline-flex"
            continue_button_spinner.value = ""
            continue_button.disabled = True
            continue_button.layout.display = "none"
            cancel_button.disabled = True
            cancel_button.layout.display = "none"

    def _cancel_button_clicked(b):
        start_test_button.layout.display = "inline-flex"
        start_test_button.disabled = False
        continue_button.layout.display = "none"
        continue_button.disabled = True
        cancel_button.layout.display = "none"
        cancel_button.disabled = True
        warning_message.value = ""

    start_test_button.on_click(start_test)
    continue_button.on_click(_continue_button_clicked)
    cancel_button.on_click(_cancel_button_clicked)