def training_widget():
    import os
    current_dir = os.getcwd()
    expected_dir = os.path.expanduser("~/physicar-deepracer-for-cloud")
    if not os.path.samefile(current_dir, expected_dir):
        return None
    
    from io import BytesIO
    import ipywidgets as widgets
    from IPython.display import display
    from ipywidgets import Layout
    from physicar.deepracer.cloud.locales.model_name import model_name_trans
    from physicar.deepracer.cloud.locales.description import description_trans
    from physicar.deepracer.cloud.debug_reward_function import DebugRewardFunctionError
    from physicar.deepracer.cloud.run import TrainingJob
    from physicar.deepracer.cloud.config_validation import (
        get_tracks_info, 
        value_show_dict,
        validate_str_regex,
        validate_str_len,
        ConfigValidationError
    )
    from physicar.deepracer.cloud.constants import IMAGE_PATH, DATA_URL, DATA_PATH
    from physicar.deepracer.cloud.utils import (
        get_language, 
        get_time_zone, 
        get_model_list,
        read_txt,
        get_discrete_action_space_img,
        get_continuous_action_space_img
    )



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


    ####### Pretrained #####

    pretrained_model_name_options = {model_info["ModelName"]:model_info["ModelName"] for model_info in get_model_list(time_zone) if model_info["Status"] in ["ready", "training", "testing", "stopping"]}
    display(
        widgets.VBox([
            widgets.HTML(f"<h2>--- Pretrained Model ---</h2>"),
            pretrained := widgets.Checkbox(
                value=False, 
                description=value_show_dict["pretrained"], 
                indent=False,
                disabled=False if pretrained_model_name_options else True,
            ),
            pretrained_model_name := widgets.Dropdown(
                options=pretrained_model_name_options, 
                description=value_show_dict["pretrained_model_name"],
                style={'description_width': '150px'},
                layout=widgets.Layout(display="none", width="auto", max_width="100%"),
            ),
            pretrained_checkpoint := widgets.Dropdown(
                options=["last", "best"],
                description=value_show_dict["pretrained_checkpoint"],
                style={'description_width': '150px'},
                value="last",
                layout=widgets.Layout(display="none"),
            )
        ])
    )



    def _pretrained_observe(change):
        pretrained_model_name.layout.display = "none" if not change["new"] else "flex"
        pretrained_checkpoint.layout.display = "none" if not change["new"] else "flex"

    pretrained.observe(_pretrained_observe, names='value')

    # Pretrained Model Name 드롭다운 메뉴 너비 조정을 위한 CSS
    from IPython.display import HTML
    display(HTML("""
    <style>
    /* Pretrained Model Name 드롭다운 메뉴 반응형 스타일 조정 */
    .widget-dropdown select {
        min-width: 200px !important;
        max-width: 100% !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    .widget-dropdown .dropdown-menu {
        min-width: 200px !important;
        max-width: 100% !important;
        width: auto !important;
        white-space: nowrap !important;
        overflow-x: auto !important;
        box-sizing: border-box !important;
    }
    .widget-dropdown .dropdown-menu li {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    
    /* 컨테이너의 반응형 레이아웃 */
    .widget-box {
        max-width: 100% !important;
        overflow-x: auto !important;
    }
    
    /* 작은 화면에서의 추가 조정 */
    @media (max-width: 768px) {
        .widget-dropdown select {
            min-width: 150px !important;
        }
        .widget-dropdown .dropdown-menu {
            min-width: 150px !important;
        }
    }
    </style>
    """))


    ####### Model Name #####

    display(widgets.VBox([
        widgets.HTML(f"<h2>--- {value_show_dict["model_name"]} ---</h2>"),
        model_name := widgets.Text(
            value="my-model", 
            description="", 
            placeholder="Enter model name",
            layout=widgets.Layout(width="auto"),
        ),
        model_name_valid := widgets.HTML("<small></small>"),
    ]))
        
    def _model_name_observe(change):
        model_name_valid_value = ""
        try:
            validate_str_regex(change['new'], value_show_dict["model_name"], r"^[a-zA-Z0-9_.-]+$", "alphanumeric characters, _, -, .")
        except ValueError as e:
            model_name_valid_value = f"<small style='color:red'>{model_name_trans[lang]['str_regex']}</small>"
            return False
        try:
            validate_str_len(change['new'], value_show_dict["model_name"], 1, 100)
        except ValueError as e:
            model_name_valid.value = f"<small style='color:red'>{model_name_trans[lang]['str_len']}</small>"
            return False

        model_name_valid.value = model_name_valid_value
        return True

    model_name.observe(_model_name_observe, names="value")

    ###### Simulation ######

    sim_all = []
    track_id_list = []
    track_direction_list = []
    race_type_list = []
    track_img_list = []
    object_avoidance_list = []
    number_of_objects_list = []
    randomize_object_locations_list = []
    object_locations_list = []
    for sim_num in range(7):
        sim_idx = "main" if sim_num == 0 else f"sub{sim_num}"
        sim_all.append(widgets.VBox([
            widgets.HBox([
                widgets.VBox(
                    [
                        track_id := widgets.Dropdown(
                            options={f"[{"%02d"%(i+1)}] {v["track_name"]}": k for i, (k, v) in enumerate(tracks_info.items())},
                            value="2024_reinvent_champ",
                            description=value_show_dict[f"simulation.{sim_idx}.track_id"],
                            tooltip=description_trans[lang][f'simulation.{sim_idx}.track_id'],
                            layout=Layout(margin="10px 0 10px 0"),
                            style={"description_width": "100px"}
                        ),
                        track_direction := widgets.Dropdown(
                            options=["counterclockwise", "clockwise"],
                            value="counterclockwise",
                            description=value_show_dict[f"simulation.{sim_idx}.track_direction"],
                            tooltip=description_trans[lang][f'simulation.{sim_idx}.track_direction'],
                            style={"description_width": "100px"}
                        ),
                        widgets.Checkbox(
                            value=False,
                            description=value_show_dict[f"simulation.{sim_idx}.alternate_training_direction"],
                            tooltip=description_trans[lang][f'simulation.{sim_idx}.alternate_training_direction'],
                            layout=Layout(margin="0 0 10px 0"),
                        ),
                        race_type := widgets.Dropdown(
                            options={
                                "Time Trial": "time_trial",
                                "Object Avoidance": "object_avoidance"
                            },
                            value="time_trial",
                            description=value_show_dict[f"simulation.{sim_idx}.race_type"],
                            tooltip=description_trans[lang][f'simulation.{sim_idx}.race_type'],
                        ),
                    ],
                    layout=widgets.Layout(width="60%"),
                ),
                track_img := get_img_widget(
                    os.path.join(DATA_PATH, "tracks", "thumbnail", "2024_reinvent_champ.svg"),
                    layout=widgets.Layout(width="40%", max_height="180px", margin="10px")
                )
            ]),
            object_avoidance := widgets.VBox([
                widgets.HTML("<h4>Object Avoidance</h4>"),
                widgets.VBox([
                    object_type := widgets.Dropdown(
                        options={
                            "Box": "box", 
                            "DeepRacer Box": "deepracer_box",
                            "DeepRacer Car": "deepracer_car",
                            "Amazon Box": "amazon_box",
                        },
                        description="Object Type",
                        style={"description_width": "130px"},
                    ),
                    number_of_objects := widgets.Dropdown(
                        options = [1,2,3,4,5,6,7,8,9,10],
                        value = 3,
                        description="Number of Objects",
                        style={"description_width": "130px"},
                    ),
                    randomize_object_locations := widgets.Checkbox(
                        value=True,
                        description="Randomize Object Location"
                    )
                ]),
                
                object_locations := widgets.VBox([
                    widgets.HTML("<h4>Object Locations</h4>"),
                    widgets.VBox([
                        widgets.HBox([
                            widgets.HTML("Object 0", layout=widgets.Layout(width="70px")),
                            widgets.BoundedIntText(
                                value=25, min=0, max=100, step=1,
                                description='Progress (%)',
                            ),
                            widgets.Dropdown(
                                options=["inside", "outside"],
                                value="outside",
                                description='Lane:',
                            )
                        ]),
                        widgets.HBox([
                            widgets.HTML("Object 1", layout=widgets.Layout(width="70px")),
                            widgets.BoundedIntText(
                                value=50, min=0, max=100, step=1,
                                description='Progress (%)',
                            ),
                            widgets.Dropdown(
                                options=["inside", "outside"],
                                value="inside",
                                description='Lane:',
                            )
                        ]),
                        widgets.HBox([
                            widgets.HTML("Object 2", layout=widgets.Layout(width="70px")),
                            widgets.BoundedIntText(
                                value=75, min=0, max=100, step=1,
                                description='Progress (%)',
                            ),
                            widgets.Dropdown(
                                options=["inside", "outside"],
                                value="outside",
                                description='Lane:',
                            )
                        ]),
                    ])


                ])

            ])

        ]))
        object_avoidance.layout.display = "none"
        object_locations.layout.display = "none"
        track_id_list.append(track_id)
        track_direction_list.append(track_direction)
        race_type_list.append(race_type)
        track_img_list.append(track_img)
        object_avoidance_list.append(object_avoidance)
        number_of_objects_list.append(number_of_objects)
        randomize_object_locations_list.append(randomize_object_locations)
        object_locations_list.append(object_locations)

    def _update_track_img(change, widget):
        track_id = change["new"]
        track_info = tracks_info[track_id]
        track_thumbnail = track_info['thumbnail']
        widget.value = f'<img src="{DATA_URL}/tracks/thumbnail/{track_thumbnail}">'

    for track_id, track_img in zip(track_id_list, track_img_list):
        track_id.observe(lambda change, widget=track_img: _update_track_img(change, widget), names="value")

    def _update_track_direction(change, widget):
        track_id = change["new"]
        track_info = tracks_info[track_id]
        print(track_info['track_direction'])
        valid_track_direction_list = track_info['track_direction']
        widget.options = valid_track_direction_list
        if widget.value not in valid_track_direction_list:
            widget.value = valid_track_direction_list[0]

    for track_id, track_direction in zip(track_id_list, track_direction_list):
        track_id.observe(lambda change, widget=track_direction: _update_track_direction(change, widget), names="value")

    def _update_object_avoidance(change, widget):
        race_type = change["new"]
        if race_type == "object_avoidance":
            widget.layout.display = "block"
        else:
            widget.layout.display = "none"

    for race_type, object_avoidance in zip(race_type_list, object_avoidance_list):
        race_type.observe(lambda change, widget=object_avoidance: _update_object_avoidance(change, widget), names="value")

    def _update_object_location_by_randomize(change, widget):
        randomize = change["new"]
        if randomize:
            widget.layout.display = "none"
        else:
            widget.layout.display = "block"

    for object_location_randomize, object_locations in zip(randomize_object_locations_list, object_locations_list):
        object_location_randomize.observe(lambda change, widget=object_locations: _update_object_location_by_randomize(change, widget), names="value")

    def _update_object_location_by_number(change, widget):
        n_objects = change["new"]
        progress_interval = 100/(n_objects+1)
        new_object_locations = []
        for i in range(n_objects):
            new_object_locations.append(
                widgets.HBox([
                    widgets.HTML(f"Object {i}", layout=widgets.Layout(width="70px")),
                    widgets.BoundedIntText(
                        value=round(progress_interval*(i+1)), min=0, max=100, step=1,
                        description='Progress (%)',
                    ),
                    widgets.Dropdown(
                        options=["inside", "outside"],
                        value="outside" if i%2==0 else "inside",
                        description='Lane:',
                    )
                ]),
            )
        widget.children[1].children = new_object_locations

    for number_of_objects, object_locations in zip(number_of_objects_list, object_locations_list):
        number_of_objects.observe(lambda change, widget=object_locations: _update_object_location_by_number(change, widget), names="value")

    display(widgets.VBox([
        widgets.HTML("<h2>--- Simulation ---</h2>"),
        number_of_sub_simulations := widgets.Dropdown(
            options={"Only main": 0, "1": 1, "2": 2, "3": 3,"4": 4,"5": 5,"6": 6},
            value=0,
            style={'description_width': '160px'},
            layout=widgets.Layout(width="50%"),
            description=value_show_dict["simulation.number_of_sub_simulations"],
            tooltip=description_trans[lang]["simulation.number_of_sub_simulations"],
        )
    ]))


    sim_tabs = widgets.Tab(children=sim_all[:1])
    sim_tabs.set_title(0, "Main")
    display(sim_tabs)

    def _update_tabs(change):
        n_sub = change["new"]
        sim_tabs.children = sim_all[: n_sub + 1]
        for sim_num in range(n_sub+1):
            sim_tabs.set_title(sim_num, "Main" if sim_num == 0 else f"Sub {sim_num}")

    number_of_sub_simulations.observe(_update_tabs, names="value")



    ####### Vehicle #####
    display(widgets.HTML("<h2>--- Vehicle ---</h2>"))

    display(
        widgets.HBox([
            widgets.VBox([
                layout := widgets.Dropdown(
                    options = {
                        "DeepRacer": "deepracer",
                        "PhysiCar-v1": "physicar-v1"
                    },
                    value="deepracer",
                    description="Layout",
                    style={"description_width": "130px"},
                    layout=widgets.Layout(margin="10px", width="300px")
                ),
                camera := widgets.Dropdown(
                    options = [1],
                    value=1,
                    disabled=True,
                    description="Number of Cameras",
                    style={"description_width": "130px"},   
                    layout=widgets.Layout(margin="10px", width="300px")
                ),
                lidar := widgets.Dropdown(
                    options = {"Disabled":False, "Enabled": True},
                    value=False,
                    description="Lidar",
                    style={"description_width": "130px"},
                    layout=widgets.Layout(margin="10px", width="300px")
                ),
            ], layout=widgets.Layout(width="60%")),
            vehicle_img := get_img_widget(
                os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-NONE.png"),
                layout=widgets.Layout(margin="auto", max_width="150px", flex="1")
            )
        ], layout=widgets.Layout(align_items="center")),

    )

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

    def _update_vehicle_img_by_layout(change):
        if change["new"] == "deepracer":
            if lidar.value:
                img_path = os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-SECTOR_LIDAR.png")
            else:
                img_path = os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-NONE.png")
        elif change["new"] == "physicar-v1":
            img_path = os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-SECTOR_LIDAR.png")
        with open(img_path, "rb") as f:
            img_bytes = f.read()
            vehicle_img.value = img_bytes
    layout.observe(_update_vehicle_img_by_layout, names="value")

    def _update_vehicle_img_by_lidar(change):
        if layout.value == "deepracer":
            if change["new"]:
                img_path = os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-SECTOR_LIDAR.png")
            else:
                img_path = os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-NONE.png")
        elif layout.value == "physicar-v1":
            img_path = os.path.join(IMAGE_PATH, "sensor_modification", "FRONT_FACING_CAMERA-SECTOR_LIDAR.png")
        with open(img_path, "rb") as f:
            img_bytes = f.read()
            vehicle_img.value = img_bytes

    lidar.observe(_update_vehicle_img_by_lidar, names="value")

    def _update_lidar_by_layout(change):
        if change["new"] == "deepracer":
            lidar.options = {"Disabled":False, "Enabled": True}
            lidar.value = False
            lidar.disabled = False
        elif change["new"] == "physicar-v1":
            lidar.options = {"Disabled":False, "Enabled": True}
            lidar.value = True
            lidar.disabled = True

    layout.observe(_update_lidar_by_layout, names="value")

    display(widgets.VBox([
        widgets.HTML("<h3>Action Space</h3>"),
        action_space_type := widgets.Dropdown(
            options = {
                "Discrete": "discrete",
                "Continuous": "continuous"
            },
            value="discrete",
            description="Action Space Type",
            style={"description_width": "130px"},
            layout=widgets.Layout(margin="10px"),
        ),
    ]))

    display(number_of_actions := widgets.BoundedIntText(
        value=10, min=1, max=30,
        description="Number of Actions",
        style={"description_width": "130px"},
        layout=widgets.Layout(margin="10px"),
    ))

    def _update_number_of_actions_by_action_space_type(change):
        if change["new"] == "discrete":
            number_of_actions.layout.display = "flex"
        else:
            number_of_actions.layout.display = "none"

    action_space_type.observe(_update_number_of_actions_by_action_space_type, names="value")


    W_ID   = "40px"
    W_SPD  = "120px"
    W_ANG  = "120px"

    discrete_action_space = []
    discrete_speed_widget_list = []
    discrete_steering_angle_widget_list = []
    for action_idx in range(30):
        if   action_idx == 0: speed=0.5; steering_angle=-30
        elif action_idx == 1: speed=1.0; steering_angle=-30
        elif action_idx == 2: speed=0.5; steering_angle=-15
        elif action_idx == 3: speed=1.0; steering_angle=-15
        elif action_idx == 4: speed=0.5; steering_angle=0
        elif action_idx == 5: speed=1.0; steering_angle=0
        elif action_idx == 6: speed=0.5; steering_angle=15
        elif action_idx == 7: speed=1.0; steering_angle=15
        elif action_idx == 8: speed=0.5; steering_angle=30
        elif action_idx == 9: speed=1.0; steering_angle=30
        else:                 speed=1.0; steering_angle=0

        discrete_action_space.append(widgets.HBox([
            widgets.HTML(f"{action_idx}", layout=widgets.Layout(width=W_ID)),
            speed_widget := widgets.BoundedFloatText(
                value=speed, min=0.1, max=4.0, step=0.1, description='',
                style={'description_width':'0px'},
                layout=widgets.Layout(width=W_SPD)
            ),
            steering_angle_widget := widgets.BoundedFloatText(
                value=steering_angle, min=-30, max=30, step=0.5, description='',
                style={'description_width':'0px'},
                layout=widgets.Layout(width=W_ANG)
            ),
        ], layout=widgets.Layout(gap="10px", align_items="center")))
        discrete_speed_widget_list.append(speed_widget)
        discrete_steering_angle_widget_list.append(steering_angle_widget)


    continuous_action_space = [
        widgets.HTML("<b>Speed (m/s)</b>"),
        widgets.HBox([
            max_speed := widgets.BoundedFloatText(
                value=1.0, min=0.1, max=4.0, step=0.1, 
                description='Max: ',
                style={'description_width':'40px'},
            ),
            min_speed := widgets.BoundedFloatText(
                value=0.5, min=0.1, max=4.0, step=0.1, 
                description='Min: ',
                style={'description_width':'40px'},
            ),
        ]),
        widgets.HTML("<b>Steering Angle (°)</b>"),
        widgets.HBox([
            max_steering_angle := widgets.BoundedFloatText(
                value=30, min=0, max=30, step=0.5, 
                description='Max: ',
                style={'description_width':'40px'},
            ),
            min_steering_angle := widgets.BoundedFloatText(
                value=-30, min=-30, max=0, step=0.5, 
                description='Min: ',
                style={'description_width':'40px'},
            ),
        ]),
    ]


    def get_action_space_img_value(img):
        buf = BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    discrete_action_space_header = widgets.HBox([
        widgets.HTML("<b>Ids</b>",              layout=widgets.Layout(width=W_ID)),
        widgets.HTML("<b>Speed (m/s)</b>",      layout=widgets.Layout(width=W_SPD)),
        widgets.HTML("<b>Steering Angle (°)</b>", layout=widgets.Layout(width=W_ANG)),
    ], layout=widgets.Layout(gap="10px"))
    display(
        widgets.HBox([
            action_space := widgets.VBox(
                [
                    discrete_action_space_header,
                    widgets.VBox(
                        discrete_action_space[:number_of_actions.value]
                    )
                ], 
                # layout=widgets.Layout(width="50%"),
            ),
            action_space_img := widgets.Image(
                value=get_action_space_img_value(get_discrete_action_space_img([{"speed": i.children[1].value, "steering_angle": i.children[2].value} for i in discrete_action_space[:number_of_actions.value]])), 
                format="png",
                layout=widgets.Layout(width="300px", margin="auto", flex="1")
            )
        ])
    )

    def _update_discrete_action_space_by_number_of_actions(change):
        action_space.children = [
            discrete_action_space_header,
            widgets.VBox(discrete_action_space[:change["new"]])
        ]
        action_space_img.value = get_action_space_img_value(get_discrete_action_space_img([{"speed": i.children[1].value, "steering_angle": i.children[2].value} for i in discrete_action_space[:change["new"]]]))
    number_of_actions.observe(_update_discrete_action_space_by_number_of_actions, names="value")

    def _update_action_space_img_by_action_space_value(change, widget):
        if action_space_type.value == "discrete":
            widget.value = get_action_space_img_value(get_discrete_action_space_img([{"speed": i.children[1].value, "steering_angle": i.children[2].value} for i in discrete_action_space[:number_of_actions.value]]))
        elif action_space_type.value == "continuous":
            widget.value = get_action_space_img_value(get_continuous_action_space_img({"steering_angle": {"low": min_steering_angle.value,"high": max_steering_angle.value},"speed": {"low": min_speed.value,"high": max_speed.value}}))
    for speed_widget in discrete_speed_widget_list:
        speed_widget.observe(lambda change, widget=action_space_img: _update_action_space_img_by_action_space_value(change, widget), names="value")
    for steering_angle_widget in discrete_steering_angle_widget_list:
        steering_angle_widget.observe(lambda change, widget=action_space_img: _update_action_space_img_by_action_space_value(change, widget), names="value")
    min_speed.observe(lambda change, widget=action_space_img: _update_action_space_img_by_action_space_value(change, widget), names="value")
    max_speed.observe(lambda change, widget=action_space_img: _update_action_space_img_by_action_space_value(change, widget), names="value")
    min_steering_angle.observe(lambda change, widget=action_space_img: _update_action_space_img_by_action_space_value(change, widget), names="value")
    max_steering_angle.observe(lambda change, widget=action_space_img: _update_action_space_img_by_action_space_value(change, widget), names="value")

    def _update_action_space_and_img_by_action_space_type(change):
        if change["new"] == "discrete":
            action_space.children = [
                discrete_action_space_header,
                widgets.VBox(discrete_action_space[:number_of_actions.value])
            ]
            action_space_img.value = get_action_space_img_value(get_discrete_action_space_img([{"speed": i.children[1].value, "steering_angle": i.children[2].value} for i in discrete_action_space[:number_of_actions.value]]))
        elif change["new"] == "continuous":
            action_space.children = continuous_action_space
            action_space_img.value = get_action_space_img_value(get_continuous_action_space_img({"steering_angle": {"low": min_steering_angle.value,"high": max_steering_angle.value},"speed": {"low": min_speed.value,"high": max_speed.value}}))

    action_space_type.observe(_update_action_space_and_img_by_action_space_type, names="value")


    ############# Training ###########
    display(
        widgets.VBox([
            widgets.HTML(f"<h2>--- Training ---</h2>"),
            widgets.HTML(f"<h4>Algorithm</h4>"),
            algorithm := widgets.Dropdown(
                options = ["PPO"],
                value = "PPO",
                description="",
                disabled=True,
            ),
            widgets.HTML("<h4>Hyperparameters</h4>"),
            batch_size := widgets.Dropdown(
                options = [32, 64, 128, 256, 512],
                value = 64,
                description="Batch Size",
                style={'description_width': '120px'},
            ),
            discount_factor := widgets.BoundedFloatText(
                value = 0.99, min=0.0, max=0.999, step=0.001,
                description="Discount Factor",
                style={'description_width': '120px'},
            ),
            learning_rate := widgets.BoundedFloatText(
                value = 0.0003, min=0.00001, max=0.1, step=0.00001,
                description="Learning Rate",
                style={'description_width': '120px'},
            ),
            loss_type := widgets.Dropdown(
                options = {
                    "Huber": "huber",
                    "Mean Squared Error": "mean_squared_error"
                },
                value = "huber",
                description="Loss Type",
                style={'description_width': '120px'},
            ),
            entropy := widgets.BoundedFloatText(
                value = 0.01, min=0.0, max=0.1, step=0.001,
                description="Entropy",
                style={'description_width': '120px'},
            ),
            widgets.HTML("<h4>Best Model Metric</h4>"),
            best_model_metric := widgets.Dropdown(
                options = {
                    "Progress": "progress",
                    "Reward": "reward",
                },
                value = "progress",
                description="",
            ),
        ])
    )

    ############# Reward Function ###########
    reward_function_path_exists = os.path.isfile("reward_function.py")
    display(
        widgets.VBox([
            widgets.HTML(f"<h2>--- Reward Function ---</h2>"),
            reward_function_path := widgets.Text(
                value="reward_function.py", 
                description="File Path: ", 
                placeholder="Enter reward function file path",
                style={'description_width': '60px'},
            ),
            reward_function_path_output := widgets.HTML(
                value = "" if reward_function_path_exists else "<p style='color:red'>File not found</p>",
                layout=widgets.Layout(margin="0 0 0 10px")
            ),
        ])
    )

    def _update_reward_function_path_output(change):
        reward_function_path_exists = os.path.isfile(change["new"].strip())
        reward_function_path_output.value = "" if reward_function_path_exists else "<p style='color:red'>File not found</p>"
    reward_function_path.observe(_update_reward_function_path_output, names="value")

    ##################### pretrained update ##################
    from physicar.deepracer.cloud.utils import Model
    def _update_by_pretrained(change):
        if change["new"]:
            model_name.value = pretrained_model_name.value + "-clone"
            pretrained_model = Model(pretrained_model_name.value)
            pretrained_model_config = pretrained_model.get_config_training()
            vehicle_config = pretrained_model_config['vehicle']
            layout.value = vehicle_config['layout']
            layout.disabled = True
            lidar.value = vehicle_config['sensor']['lidar']
            if layout.value == "deepracer":
                lidar.disabled = True
            action_space_type.value = vehicle_config['action_space_type']
            action_space_type.disabled = True
            if vehicle_config['action_space_type'] == "discrete":
                number_of_actions.value = len(vehicle_config['action_space']['discrete'])
                number_of_actions.disabled = True
                for i, act in enumerate(vehicle_config['action_space']['discrete']):
                    discrete_action_space[i].children[1].value = act['speed']
                    discrete_action_space[i].children[2].value = act['steering_angle']
                action_space.children = [
                    discrete_action_space_header,
                    widgets.VBox(discrete_action_space[:number_of_actions.value])
                ]
            elif vehicle_config['action_space_type'] == "continuous":
                number_of_actions.value = 10
                number_of_actions.disabled = True
                min_speed.value = vehicle_config['action_space']['continuous']['speed']['low']
                max_speed.value = vehicle_config['action_space']['continuous']['speed']['high']
                min_steering_angle.value = vehicle_config['action_space']['continuous']['steering_angle']['low']
                max_steering_angle.value = vehicle_config['action_space']['continuous']['steering_angle']['high']
                action_space.children = continuous_action_space
        else:
            layout.disabled = False
            if layout.value == "deepracer":
                lidar.disabled = False
            action_space_type.disabled = False
            number_of_actions.disabled = False

    pretrained.observe(_update_by_pretrained, names='value')


    ############ get config ##############

    def get_config():
        config={}
        config["job_type"] = "training"
        config["pretrained"] = pretrained.value
        config["pretrained_checkpoint"] = pretrained_checkpoint.value
        config["model_name"] = model_name.value
        config["simulation"] = {}
        config["simulation"]["number_of_sub_simulations"] = number_of_sub_simulations.value
        for sim_num in range(number_of_sub_simulations.value + 1):
            sim_idx = "main" if sim_num == 0 else f"sub{sim_num}"
            config["simulation"][sim_idx] = {
                "track_id": sim_all[sim_num].children[0].children[0].children[0].value,
                "track_direction": sim_all[sim_num].children[0].children[0].children[1].value,
                "alternate_training_direction": sim_all[sim_num].children[0].children[0].children[2].value,
                "race_type": sim_all[sim_num].children[0].children[0].children[3].value,
                "object_avoidance": {
                    "object_type": sim_all[sim_num].children[1].children[1].children[0].value,
                    "number_of_objects": sim_all[sim_num].children[1].children[1].children[1].value,
                    "randomize_object_locations": sim_all[sim_num].children[1].children[1].children[2].value,
                    "object_locations": [
                        {
                            "progress": obj_loc.children[1].value,
                            "lane": obj_loc.children[2].value,
                        }
                        for obj_loc in sim_all[sim_num].children[1].children[2].children[1].children
                    ] if not sim_all[sim_num].children[1].children[1].children[2].value else []
                }
            }
        config["vehicle"] = {
            "layout": layout.value,
            "sensor": {
                "camera": camera.value,
                "lidar": lidar.value,
            },
            "action_space_type": action_space_type.value,
            "action_space": {
                "discrete": [
                    {
                        "speed": discrete_action_space[i].children[1].value,
                        "steering_angle": discrete_action_space[i].children[2].value,
                    }
                    for i in range(number_of_actions.value)
                ] if action_space_type.value == "discrete" else [],
                "continuous": {
                    "speed": {
                        "low": min_speed.value,
                        "high": max_speed.value,
                    },
                    "steering_angle": {
                        "low": min_steering_angle.value,
                        "high": max_steering_angle.value,
                    }
                } if action_space_type.value == "continuous" else {}
            }
        }
        config["training"] = {
            "algorithm": algorithm.value,
            "hyperparameters": {
                "batch_size": batch_size.value,
                "discount_factor": discount_factor.value,
                "learning_rate": learning_rate.value,
                "loss_type": loss_type.value,
                "entropy": entropy.value,
            },
            "best_model_metric": best_model_metric.value
        }
        return config

    ############ Start Training ##############
    display(
        widgets.VBox([
            widgets.HTML("<h2>=== Start Training ===</h2>"),
            widgets.HBox([
                start_button := widgets.Button(
                    description="Start Training", 
                    button_style='success', 
                    icon='play', 
                    layout=widgets.Layout(width="200px"), 
                    style={'description_width': 'initial', 'button_color': None, 'font_weight': 'normal'}, 
                    disabled=not (os.path.isfile("reward_function.py") and _model_name_observe({'new': model_name.value}))
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

    global training_job
    training_job = None

    def _start_button_clicked(b):
        global error, training_job
        start_button.disabled = True
        start_button_spinner.value = "<i class='fa fa-spinner fa-spin'></i>"
        error_message.value = ""
        warning_message.value = ""
        success_message.value = ""
        
        try:
            training_job = TrainingJob(
                config=get_config(), 
                reward_function=read_txt(reward_function_path.value.strip()),
                debug_reward_function=True,
                lang=lang,
            )
        except DebugRewardFunctionError as e:
            error = {
                "error_type": "DebugRewardFunctionError",
                "error_message": str(e).strip(),
                "error_line": e.error_line,
            } 
            error_message.value = f"""
            <div style='background-color: #ffe6e6; border: 1px solid #ff6b6b; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #d63031; margin: 0 0 10px 0;'><i class='fa fa-exclamation-triangle'></i> Reward Function Error</h4>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Message:</strong> {error['error_message']}</p>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Line:</strong> {error['error_line']}</p>
            </div>
            """
            start_button.disabled = False
            start_button_spinner.value = ""
            return
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
            start_button.disabled = False
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
            start_button.disabled = False
            start_button_spinner.value = ""
            return

        if training_job.warnings:
            warning_html = """
            <div style='background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #856404; margin: 0 0 10px 0;'><i class='fa fa-exclamation-circle'></i> Warnings</h4>
                <p style='margin: 5px 0; color: #856404;'>Please check the following warnings before proceeding.</p>
            """
            for i, warning in enumerate(training_job.warnings):
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
            
            start_button.layout.display = "none"
            start_button.disabled = False
            start_button_spinner.value = ""
            continue_button.layout.display = "inline-flex"
            continue_button.disabled = False
            cancel_button.layout.display = "inline-flex"
            cancel_button.disabled = False
        else:
            output_model_name = training_job.start()
            success_message.value = f"""
            <div style='background-color: #d4edda; border: 1px solid #28a745; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #155724; margin: 0 0 10px 0;'><i class='fa fa-check-circle'></i> Training Started!</h4>
                <p style='margin: 5px 0; color: #155724;'><strong>Model Name:</strong> {output_model_name}</p>
                <p style='margin: 5px 0; color: #6c757d;'>Training has started successfully.</p>
                <p style='margin: 10px 0 5px 0; color: #155724;'>
                    <a href="02_your_models.ipynb" target="_blank" 
                       style="display: inline-block; padding: 8px 16px; background-color: #007acc; 
                              color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        📊 Monitor Training Progress
                    </a>
                </p>
            </div>
            """
            start_button.disabled = False
            start_button.layout.display = "inline-flex"
            start_button_spinner.value = ""
            continue_button.disabled = True
            continue_button.layout.display = "none"
            cancel_button.disabled = True
            cancel_button.layout.display = "none"

    start_button.on_click(_start_button_clicked)

    def _continue_button_clicked(b):
        global training_job
        continue_button.disabled = True
        cancel_button.disabled = True
        cancel_button.layout.display = "none"
        continue_button_spinner.value = "<i class='fa fa-spinner fa-spin'></i>"
        warning_message.value = ""
        
        try:
            output_model_name = training_job.start()
            success_message.value = f"""
            <div style='background-color: #d4edda; border: 1px solid #28a745; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #155724; margin: 0 0 10px 0;'><i class='fa fa-check-circle'></i> Training Started!</h4>
                <p style='margin: 5px 0; color: #155724;'><strong>Model Name:</strong> {output_model_name}</p>
                <p style='margin: 10px 0 5px 0; color: #155724;'>
                    <a href="02_your_models.ipynb" target="_blank" 
                       style="display: inline-block; padding: 8px 16px; background-color: #007acc; 
                              color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        📊 Monitor Training Progress
                    </a>
                </p>
            </div>
            """
            continue_button.layout.display = "none"
            cancel_button.layout.display = "none"
            start_button.layout.display = "inline-flex"
            start_button.disabled = False
        except Exception as e:
            error_message.value = f"""
            <div style='background-color: #ffe6e6; border: 1px solid #ff6b6b; border-radius: 5px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #d63031; margin: 0 0 10px 0;'><i class='fa fa-exclamation-triangle'></i> Unexpected Error</h4>
                <p style='margin: 5px 0; color: #2d3436;'><strong>Error:</strong> {str(e)}</p>
            </div>
            """
            continue_button.disabled = False
        
        continue_button_spinner.value = ""

    def _cancel_button_clicked(b):
        # 경고 메시지와 버튼들을 숨기고 초기 상태로 되돌림
        warning_message.value = ""
        error_message.value = ""
        success_message.value = ""
        
        # 버튼 상태 초기화
        start_button.layout.display = "inline-flex"
        start_button.disabled = False
        continue_button.layout.display = "none"
        continue_button.disabled = True
        cancel_button.layout.display = "none"
        cancel_button.disabled = True

    start_button.on_click(_start_button_clicked)
    continue_button.on_click(_continue_button_clicked)
    cancel_button.on_click(_cancel_button_clicked)