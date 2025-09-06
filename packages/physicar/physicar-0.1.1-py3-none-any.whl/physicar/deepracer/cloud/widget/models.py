def models_widget():
    import os
    current_dir = os.getcwd()
    expected_dir = os.path.expanduser("~/physicar-deepracer-for-cloud")
    if not os.path.samefile(current_dir, expected_dir):
        return None

    import os
    import threading
    import time
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
        get_continuous_action_space_img,
        Model,
        Test
    )

    lang = get_language()
    time_zone = get_time_zone()
    tracks_info = get_tracks_info()

    # Global variables for auto refresh
    auto_refresh_active = False
    timer_widget = None

    def simple_status_update():
        """Simple status update function with metrics refresh"""
        try:
            if model and auto_refresh_active:
                # Update status
                current_status = model.get_status()
                model_status.value = f"<b>[Status] {current_status}</b> (Last update: {time.strftime('%H:%M:%S')})"
                
                # Update metrics graphs without recreating widgets
                update_metrics_only()
                
                # Update test mode display if it's currently visible
                if hasattr(test_mode_display, 'layout') and test_mode_display.layout.display != 'none':
                    update_test_mode_only()
                
        except Exception as e:
            print(f"Status update error: {e}")
    
    def update_test_mode_only():
        """Update only test mode display without recreating widgets"""
        try:
            if not model:
                return
                
            # Update test mode display
            new_test_display = create_test_mode_display(model)
            test_mode_display.children = new_test_display.children
                        
        except Exception as e:
            print(f"Test mode update error: {e}")
    
    def update_metrics_only():
        """Update only metrics graphs and training views without recreating widgets"""
        try:
            if not model:
                return
                
            config_training = model.get_config_training()
            if (config_training and 
                hasattr(training_mode_display, 'children') and 
                training_mode_display.children):
                
                number_of_sub_simulations = config_training['simulation']['number_of_sub_simulations']
                
                for sim_idx in range(min(len(training_mode_display.children), number_of_sub_simulations + 1)):
                    sim_name = "main" if sim_idx == 0 else f"sim{sim_idx}"
                    
                    # Update metrics graph with cache busting
                    if metrics_graph_url := model.get_metrics_graph_url().get(sim_name, ''):
                        import time
                        cache_buster = f"t={int(time.time())}&r={os.urandom(8).hex()}"
                        metrics_graph_url += f"?{cache_buster}"
                        metrics_graph_html = f"<img src='{metrics_graph_url}' alt='No metrics graph available' style='max-width: 100%; height: auto;'/>"
                        
                        # Find and update the metrics graph widget
                        tab_content = training_mode_display.children[sim_idx]
                        if hasattr(tab_content, 'children') and len(tab_content.children) > 0:
                            hbox = tab_content.children[0]  # First HBox
                            if hasattr(hbox, 'children') and len(hbox.children) > 0:
                                metrics_widget = hbox.children[0]  # First widget is metrics
                                if hasattr(metrics_widget, 'value'):
                                    metrics_widget.value = metrics_graph_html
                    
                    # Update training views with cache busting
                    if training_view_url := model.get_training_view_url().get(sim_name, {}):
                        import time
                        cache_buster = f"t={int(time.time())}&r={os.urandom(8).hex()}"
                        front_view_html = f"""<img src='{training_view_url.get("front", "")}?{cache_buster}' alt='No training front view available' style='max-width: 100%; height: auto;'/>"""
                        chase_overlay_view_html = f"""<img src='{training_view_url.get("chase_overlay", "")}?{cache_buster}' alt='No training chase overlay view available' style='max-width: 100%; height: auto;'/>"""
                        
                        # Find and update training view widgets
                        tab_content = training_mode_display.children[sim_idx]
                        if hasattr(tab_content, 'children') and len(tab_content.children) > 0:
                            hbox = tab_content.children[0]
                            if hasattr(hbox, 'children') and len(hbox.children) > 1:
                                training_views_vbox = hbox.children[1]  # Second widget is training views
                                if hasattr(training_views_vbox, 'children') and len(training_views_vbox.children) >= 2:
                                    front_view_widget = training_views_vbox.children[0]
                                    chase_overlay_widget = training_views_vbox.children[1]
                                    if hasattr(front_view_widget, 'value'):
                                        front_view_widget.value = front_view_html
                                    if hasattr(chase_overlay_widget, 'value'):
                                        chase_overlay_widget.value = chase_overlay_view_html
                        
        except Exception as e:
            print(f"Metrics update error: {e}")
    
    def create_timer():
        """Create a timer widget for auto refresh"""
        import asyncio
        from asyncio import sleep
        
        async def refresh_loop():
            while auto_refresh_active:
                simple_status_update()
                await sleep(300)  # 300 seconds (5 minutes)
        
        def start_refresh():
            if auto_refresh_active:
                asyncio.create_task(refresh_loop())
        
        return start_refresh


    ####### Select Model #####
    def get_model_name_options():
        import time
        while True:
            try:
                model_name_options = {}
                target_model_name = None
                for model_info in get_model_list(time_zone):
                    model_name_options[f'{model_info["ModelName"]} ({model_info["Status"]})'] = model_info["ModelName"]
                    if model_info["Status"] in ["training", "testing", "initializing", "stopping"]:     
                        target_model_name = model_info["ModelName"]
                if not target_model_name and model_name_options:
                    target_model_name = list(model_name_options.values())[0]
                    
                return model_name_options, target_model_name
            except:
                time.sleep(1)
                continue

    model_name_options, target_model_name = get_model_name_options()
    if model_name_options:
        model = Model(target_model_name)
    else:
        model = None


    display(
        widgets.VBox([
            widgets.HTML(f"<h2>Select Model</h2>"),
            model_name := widgets.Dropdown(
                options=model_name_options,
                value=target_model_name,
                description="",
                style={'description_width': '0px'},
                layout=widgets.Layout(width="auto", max_width="100%"),
            ),
            widgets.HBox([
                auto_refresh_toggle := widgets.Checkbox(
                    value=True,
                    description='Auto Refresh (5min)',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='auto')
                ),
                manual_refresh_button := widgets.Button(
                    description='Manual Refresh',
                    button_style='info',
                    layout=widgets.Layout(width='auto', margin='0 0 0 10px')
                )
            ])
        ])
    )

    def _update_model(change):
        global model, refresh_thread, auto_refresh_active
        model = Model(change['new'])
        
        # Add a small delay to ensure model is properly loaded
        import time
        time.sleep(0.1)
        
        # Update model status
        model_status.value = f"<b>[Status] {model.get_status() if model else ''}</b>"
        
        # Update physical car model links
        if model:
            physical_car_model_link = model.get_physical_car_model_link()
            physical_car_model.value = f"""
                <b>[Download Physical Car Model] {' , '.join(f"<a href='{ckp_url}'>{ckp}.tar.gz</a>" for ckp, ckp_url in physical_car_model_link.items())}</b>
            """
        else:
            physical_car_model.value = "<b>[Download Physical Car Model] No model</b>"
        
        # Update training mode display (simulation tabs)
        if model:
            new_training_sims = []
            config_training = model.get_config_training()
            if config_training:
                number_of_sub_simulations = config_training['simulation']['number_of_sub_simulations']
                
                for sim_idx in range(7):
                    sim_name = "main" if sim_idx == 0 else f"sim{sim_idx}"
                    config_sim_key = "main" if sim_idx == 0 else f"sub{sim_idx}"  # Actual config keys are sub1, sub2, ...
                    
                    # Update metrics graph with stronger cache busting
                    if metrics_graph_url := model.get_metrics_graph_url().get(sim_name, ''):
                        # Use timestamp and random hex for stronger cache busting
                        import time
                        cache_buster = f"t={int(time.time())}&r={os.urandom(8).hex()}"
                        metrics_graph_url += f"?{cache_buster}"
                        metrics_graph_html = f"<img src='{metrics_graph_url}' alt='No metrics graph available' style='max-width: 100%; height: auto;' onload='console.log(\"Metrics loaded: {sim_name}\")' onerror='console.log(\"Metrics failed: {sim_name}\")'/>"
                    else:
                        metrics_graph_html = "<p>No metrics graph available</p>"
                    
                    # Update training views with stronger cache busting
                    if training_view_url := model.get_training_view_url().get(sim_name, {}):
                        import time
                        cache_buster = f"t={int(time.time())}&r={os.urandom(8).hex()}"
                        front_view_html = f"""<img src='{training_view_url.get("front", "")}?{cache_buster}' alt='No training front view available' style='max-width: 100%; height: auto;' onload='console.log("Front view loaded: {sim_name}")' onerror='console.log("Front view failed: {sim_name}")'/>"""
                        chase_overlay_view_html = f"""<img src='{training_view_url.get("chase_overlay", "")}?{cache_buster}' alt='No training chase overlay view available' style='max-width: 100%; height: auto;' onload='console.log("Chase view loaded: {sim_name}")' onerror='console.log("Chase view failed: {sim_name}")'/>"""
                    else:
                        front_view_html = "<p>No training front view available</p>"
                        chase_overlay_view_html = "<p>No training chase overlay view available</p>"
                    
                    # Update simulation info - use correct config key
                    if config_sim_key in config_training['simulation']:
                        sim_config = config_training['simulation'][config_sim_key]
                        if isinstance(sim_config, dict) and 'race_type' in sim_config:
                            if sim_config['race_type'] == 'object_avoidance':
                                if not sim_config['object_avoidance']['randomize_object_locations']:
                                    object_locations_html = "<li><b>Object Locations:</b></li>"
                                    object_locations_html += "<ul>"
                                    for loc in sim_config['object_avoidance']['object_locations']:
                                        object_locations_html += f"<li>progress: {loc['progress']}, lane: {loc['lane']}</li>"
                                    object_locations_html += "</ul>"
                                else:
                                    object_locations_html = ""
                                object_avoidance_html = f"""
                                <ul>
                                    <li><b>Object Type:</b> {sim_config['object_avoidance']['object_type']}</li>
                                    <li><b>Number of Objects:</b> {sim_config['object_avoidance']['number_of_objects']}</li>
                                    <li><b>Randomize Object Locations:</b> {sim_config['object_avoidance']['randomize_object_locations']}</li>
                                    {object_locations_html}
                                </ul>
                                """
                            else:
                                object_avoidance_html = ""
                            sim_info_html = f"""
                            <ul>
                                <li><b>Track Name:</b> {tracks_info[sim_config['track_id']]['track_name']}</li>
                                <li><b>Track Direction:</b> {sim_config['track_direction']}</li>
                                <li><b>Alternate Training Direction:</b> {sim_config['alternate_training_direction']}</li>
                                <li><b>Race Type:</b> {sim_config['race_type']}</li>
                                {object_avoidance_html}
                            </ul>
                            """
                        else:
                            sim_info_html = f"<p>No simulation info available (config exists but invalid structure for {config_sim_key})</p>"
                    else:
                        sim_info_html = f"<p>No simulation info available (key {config_sim_key} not found)</p>"
                    
                    # Create new simulation tab
                    new_training_sims.append(widgets.VBox([
                        widgets.HBox([
                            widgets.HTML(
                                metrics_graph_html,
                                layout=Layout(width='61%', min_width='305px', max_width='610px')
                            ),
                            widgets.VBox([
                                widgets.HTML(front_view_html),
                                widgets.HTML(chase_overlay_view_html),
                            ], layout=Layout(width='39%', min_width='195px', max_width='390px')),
                        ]),
                        widgets.HBox([
                            widgets.HTML(sim_info_html)
                        ])
                    ]))
                
                # Update training mode display children and titles
                training_mode_display.children = new_training_sims[:number_of_sub_simulations+1]
                for idx in range(len(training_mode_display.children)):
                    sim_name = "Main" if idx == 0 else f"Sim{idx}"
                    training_mode_display.set_title(idx, sim_name)
        
        # Update vehicle info
        if model:
            config_training = model.get_config_training()
            if config_training:
                if config_training['vehicle']['action_space_type'] == 'discrete':
                    action_space_html = "<ul>"
                    for action in config_training['vehicle']['action_space']['discrete']:
                        action_space_html += f"<li>speed: {action['speed']}, steering_angle: {action['steering_angle']}</li>"
                    action_space_html += "</ul>"
                elif config_training['vehicle']['action_space_type'] == 'continuous':
                    action_space_html = f"""
                    <ul>
                        <li>steering_angle: min: {config_training['vehicle']['action_space']['continuous']['steering_angle']['low']}, max: {config_training['vehicle']['action_space']['continuous']['steering_angle']['high']}</li>
                        <li>speed: min: {config_training['vehicle']['action_space']['continuous']['speed']['low']}, max: {config_training['vehicle']['action_space']['continuous']['speed']['high']}</li>
                    </ul>
                    """
                vehicle_info.value = f"""
                    <h3>Vehicle Info</h3>
                    <ul>
                        <li><b>Layout:</b> {config_training['vehicle']['layout']}</li>
                        <li><b>Sensor:</b></li>
                            <ul>
                                <li><b>Camera:</b> {config_training['vehicle']['sensor']['camera']}</li>
                                <li><b>Lidar:</b> {config_training['vehicle']['sensor']['lidar']}</li>
                            </ul>
                        <li><b>Action Space:</b></li>
                            {action_space_html}
                    </ul>
                """
            else:
                vehicle_info.value = """
                    <h3>Vehicle Info</h3>
                    <p>No vehicle info available</p>
                """
        else:
            vehicle_info.value = """
                <h3>Vehicle Info</h3>
                <p>No model selected</p>
            """
        
        # Update reward function
        if model:
            reward_function_str = model.get_reward_function()
            reward_function.value = f"""
                <h3>Reward Function</h3>
                <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto;">{reward_function_str}</pre>
            """
        else:
            reward_function.value = """
                <h3>Reward Function</h3>
                <p>No reward function available</p>
            """
        
        # Switch to Training mode when model changes
        mode_type.value = 'Training'
        
        # Update test mode display when model changes
        if model:
            new_test_display = create_test_mode_display(model)
            test_mode_display.children = new_test_display.children
        training_mode_display.layout.display = ''
        test_mode_display.layout.display = 'none'
        
        # Restart auto refresh if enabled
        if auto_refresh_active:
            pass  # Will be handled at the end
    
    def _toggle_auto_refresh(change):
        global auto_refresh_active
        auto_refresh_active = change['new']
    
    def _manual_refresh(button):
        """Manual refresh using the same method as auto refresh"""
        simple_status_update()
        print("Manual refresh completed")
    model_name.observe(_update_model, names='value')
    auto_refresh_toggle.observe(_toggle_auto_refresh, names='value')
    manual_refresh_button.on_click(_manual_refresh)



    training_mode_display = widgets.Tab()
    training_sims = []
    for sim_idx in range(7):
        sim_name = "main" if sim_idx == 0 else f"sim{sim_idx}"
        config_sim_key = "main" if sim_idx == 0 else f"sub{sim_idx}"  # Actual config keys are sub1, sub2, ...
        
        if model :
            if metrics_graph_url:= model.get_metrics_graph_url().get(sim_name, ''):
                metrics_graph_url += f"?t={os.urandom(4).hex()}"
                metrics_graph_html = f"<img src='{metrics_graph_url}' alt='No mertrics graph available' style='max-width: 100%; height: auto;'/>"
            else:
                metrics_graph_html = "<p>No mertrics graph available</p>"
            if training_view_url:= model.get_training_view_url().get(sim_name, {}):
                front_view_html = f"""<img src='{training_view_url.get("front", "")}' alt='No training front view available' style='max-width: 100%; height: auto;'/>"""
                chase_overlay_view_html = f"""<img src='{training_view_url.get("chase_overlay", "")}' alt='No training chase overlay view available' style='max-width: 100%; height: auto;'/>"""
            else:
                front_view_html = "<p>No training front view available</p>"
                chase_overlay_view_html = "<p>No training chase overlay view available</p>"

            if config_training := model.get_config_training():
                if config_sim_key in config_training['simulation']:
                    sim_config = config_training['simulation'][config_sim_key]
                    if isinstance(sim_config, dict) and 'race_type' in sim_config:
                        if sim_config['race_type'] == 'object_avoidance':
                            if not sim_config['object_avoidance']['randomize_object_locations']:
                                object_locations_html = "<li><b>Object Locations:</b></li>"
                                object_locations_html += "<ul>"
                                for loc in sim_config['object_avoidance']['object_locations']:
                                    object_locations_html += f"<li>progress: {loc['progress']}, lane: {loc['lane']}</li>"
                                object_locations_html += "</ul>"
                            else:
                                object_locations_html = ""
                            object_avoidance_html = f"""
                            <ul>
                                <li><b>Object Type:</b> {sim_config['object_avoidance']['object_type']}</li>
                                <li><b>Number of Objects:</b> {sim_config['object_avoidance']['number_of_objects']}</li>
                                <li><b>Randomize Object Locations:</b> {sim_config['object_avoidance']['randomize_object_locations']}</li>
                                {object_locations_html}
                            </ul>
                            """
                        else :
                            object_avoidance_html = ""
                        sim_info_html = f"""
                        <ul>
                            <li><b>Track Name:</b> {tracks_info[sim_config['track_id']]['track_name']}</li>
                            <li><b>Track Direction:</b> {sim_config['track_direction']}</li>
                            <li><b>Alternate Training Direction:</b> {sim_config['alternate_training_direction']}</li>
                            <li><b>Race Type:</b> {sim_config['race_type']}</li>
                            {object_avoidance_html}
                        </ul>
                        """
                    else:
                        sim_info_html = f"<p>No simulation info available (config exists but invalid structure for {config_sim_key})</p>"
                else:
                    sim_info_html = f"<p>No simulation info available (key {config_sim_key} not found)</p>"
                
        else:
            metrics_graph_html = "<p>No mertrics graph available</p>"
            front_view_html = "<p>No training front view available</p>"
            chase_overlay_view_html = "<p>No training chase overlay view available</p>"
            sim_info_html = "<p>No model selected</p>"
        training_sims.append(widgets.VBox([
            widgets.HBox([
                metrics_graph := widgets.HTML(
                    metrics_graph_html,
                    layout = Layout(width='61%', min_width='305px', max_width='610px')
                    ),
                training_view := widgets.VBox([
                    front_view := widgets.HTML(front_view_html),
                    chase_overlay_view := widgets.HTML(chase_overlay_view_html),
                ], layout = Layout(width='39%', min_width='195px', max_width='390px')),
            ]),
            widgets.HBox([
                sim_info := widgets.HTML(sim_info_html)
                
            ])
        ]))

    model_training_config = model.get_config_training()
    number_of_sub_simulations = model_training_config['simulation']['number_of_sub_simulations']
    training_mode_display.children = training_sims[:number_of_sub_simulations+1]
    for idx in range(len(training_mode_display.children)):
        sim_name = "Main" if idx == 0 else f"Sim{idx}"
        training_mode_display.set_title(idx, sim_name)


    if model:
        physical_car_model_link = model.get_physical_car_model_link()
        physical_car_model = widgets.HTML(value=f"""
            <b>[Download Physical Car Model] {' , '.join(f"<a href='{ckp_url}'>{ckp}.tar.gz</a>" for ckp, ckp_url in physical_car_model_link.items())}</b>
        """)
    else:
        physical_car_model = widgets.HTML(value=f"""
            <b>[Download Physical Car Model] No model</b>
        """)

    if model:
        config_training = model.get_config_training()
        if config_training:
            if config_training['vehicle']['action_space_type'] == 'discrete':
                action_space_html = "<ul>"
                for action in config_training['vehicle']['action_space']['discrete']:
                    action_space_html += f"<li>speed: {action['speed']}, steering_angle: {action['steering_angle']}</li>"
                action_space_html += "</ul>"
            elif config_training['vehicle']['action_space_type'] == 'continuous':
                action_space_html = f"""
                <ul>
                    <li>steering_angle: min: {config_training['vehicle']['action_space']['continuous']['steering_angle']['low']}, max: {config_training['vehicle']['action_space']['continuous']['steering_angle']['high']}</li>
                    <li>speed: min: {config_training['vehicle']['action_space']['continuous']['speed']['low']}, max: {config_training['vehicle']['action_space']['continuous']['speed']['high']}</li>
                </ul>
                """
            vehicle_info = widgets.HTML(value=f"""
                <h3>Vehicle Info</h3>
                <ul>
                    <li><b>Layout:</b> {config_training['vehicle']['layout']}</li>
                    <li><b>Sensor:</b></li>
                        <ul>
                            <li><b>Camera:</b> {config_training['vehicle']['sensor']['camera']}</li>
                            <li><b>Lidar:</b> {config_training['vehicle']['sensor']['lidar']}</li>
                        </ul>
                    <li><b>Action Space:</b></li>
                        {action_space_html}
                    

                </ul>
            """)
        else:
            vehicle_info = widgets.HTML(value=f"""
                <h3>Vehicle Info</h3>
                <p>No vehicle info available</p>
            """)

    if model:
        reward_function_str = model.get_reward_function()
        reward_function = widgets.HTML(value=f"""
            <h3>Reward Function</h3>
            <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto;">{reward_function_str}</pre>
        """)
    else:
        reward_function = widgets.HTML(value=f"""
            <h3>Reward Function</h3>
            <p>No reward function available</p>
        """)


    # Helper function to format test name
    def format_test_name(test_name):
        """Convert 20250905102412 to localized time format based on user's timezone"""
        if not test_name or len(test_name) != 14:
            return test_name
        try:
            from datetime import datetime, timezone, timedelta
            
            # Parse the timestamp (assume UTC)
            year = int(test_name[0:4])
            month = int(test_name[4:6])
            day = int(test_name[6:8])
            hour = int(test_name[8:10])
            minute = int(test_name[10:12])
            second = int(test_name[12:14])
            
            # Create datetime object in UTC
            utc_dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
            
            # Simple timezone conversion with common offsets
            timezone_offsets = {
                'UTC': 0,
                'US/Eastern': -5, 'US/Central': -6, 'US/Mountain': -7, 'US/Pacific': -8,
                'Europe/London': 0, 'Europe/Berlin': 1, 'Europe/Paris': 1,
                'Asia/Tokyo': 9, 'Asia/Seoul': 9, 'Asia/Shanghai': 8,
                'Asia/Kolkata': 5.5, 'Asia/Dubai': 4,
                'Australia/Sydney': 10, 'Australia/Melbourne': 10
            }
            
            offset_hours = timezone_offsets.get(time_zone, 0)
            # Handle half-hour offsets
            if isinstance(offset_hours, float):
                hours = int(offset_hours)
                minutes = int((offset_hours - hours) * 60)
                local_tz = timezone(timedelta(hours=hours, minutes=minutes))
            else:
                local_tz = timezone(timedelta(hours=offset_hours))
            
            local_dt = utc_dt.astimezone(local_tz)
            
            # Format to readable string with timezone abbreviation
            tz_name = time_zone.split('/')[-1] if '/' in time_zone else time_zone
            return local_dt.strftime(f"%Y-%m-%d %H:%M:%S ({tz_name})")
            
        except Exception as e:
            # Fallback to original format if conversion fails
            try:
                year = test_name[0:4]
                month = test_name[4:6]
                day = test_name[6:8]
                hour = test_name[8:10]
                minute = test_name[10:12]
                second = test_name[12:14]
                return f"{year}-{month}-{day} {hour}:{minute}:{second} UTC"
            except:
                return test_name

    # Test mode display creation
    def create_test_mode_display(current_model=None):
        """Create test mode display with test selection and details"""
        if not current_model:
            return widgets.VBox([
                widgets.HTML("<h3>No model selected</h3>")
            ])
        
        try:
            test_list = current_model.get_test_list()
            
            # Include both completed tests and currently testing tests
            available_tests = []
            for test in test_list:
                if test.get('test_name'):  # Completed tests
                    available_tests.append(test)
                elif test.get('status') == 'testing':  # Currently testing
                    available_tests.append(test)
            
            if not available_tests:
                return widgets.VBox([
                    widgets.HTML("<h3>No tests available</h3>")
                ])
            
            # Create test selection options
            test_options = {}
            for test_info in available_tests:
                test_name = test_info.get('test_name')
                status = test_info['status']
                
                if test_name:  # Completed test
                    formatted_name = format_test_name(test_name)
                    display_name = f"{formatted_name} ({status})"
                    test_options[display_name] = test_name
                else:  # Currently testing
                    display_name = f"Currently Testing... ({status})"
                    test_options[display_name] = None  # Use None as identifier for testing
            
            # Test selector - changed from Select to Dropdown
            test_selector = widgets.Dropdown(
                options=test_options,
                value=list(test_options.values())[0] if test_options else None,
                description='Tests:',
                style={'description_width': 'initial'},
                layout=widgets.Layout(width='100%')
            )
            
            # Initialize with first test
            selected_test_name = list(test_options.values())[0] if test_options else None
            
            # Test details widgets
            test_metrics_display = widgets.HTML("Loading test metrics...")
            test_video_display = widgets.HTML("Loading test video...")
            test_simulation_display = widgets.HTML("Loading simulation info...")
            test_settings_display = widgets.HTML("Loading test settings...")
            
            def update_test_details(test_name):
                """Update test details for selected test"""
                if test_name is None:  # Currently testing
                    test_metrics_display.value = """
                        <h4>Currently Testing</h4>
                        <p>Test is in progress, please wait.<br>
                        Results will be available once the test is completed.</p>
                    """
                    test_video_display.value = """
                        <h4>Test Video</h4>
                        <p>Test video will be available after test completion.</p>
                    """
                    test_simulation_display.value = """
                        <h4>Test Simulation</h4>
                        <p>Test simulation information will be available after test completion.</p>
                    """
                    test_settings_display.value = """
                        <h4>Test Settings</h4>
                        <p>Test settings information will be available after test completion.</p>
                    """
                    return
                    
                if not test_name:
                    return
                    
                try:
                    test = Test(current_model.model_name, test_name)
                    
                    # Get test metrics
                    try:
                        df_metrics = test.get_df_metrics()
                        if df_metrics is not None and not df_metrics.empty:
                            metrics_html = df_metrics.to_html(classes='table table-striped', table_id='metrics-table')
                            test_metrics_display.value = f"""
                                <h4>Test Metrics</h4>
                                <div style="max-height: 300px; overflow-y: auto;">
                                    {metrics_html}
                                </div>
                            """
                        else:
                            test_metrics_display.value = "<h4>Test Metrics</h4><p>No metrics available</p>"
                    except Exception as e:
                        test_metrics_display.value = f"<h4>Test Metrics</h4><p>Error loading metrics: {e}</p>"
                    
                    # Get test video
                    try:
                        video_url = test.get_video_url()
                        if video_url:
                            test_video_display.value = f"""
                                <h4>Test Video</h4>
                                <video controls style="max-width: 100%; height: auto;">
                                    <source src="{video_url}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                            """
                        else:
                            test_video_display.value = "<h4>Test Video</h4><p>No video available</p>"
                    except Exception as e:
                        test_video_display.value = f"<h4>Test Video</h4><p>Error loading video: {e}</p>"
                    
                    # Get test configuration
                    try:
                        test_config = test.get_config_test()
                        
                        # Test simulation info
                        if 'simulation' in test_config and 'main' in test_config['simulation']:
                            sim_config = test_config['simulation']['main']
                            
                            object_avoidance_html = ""
                            if sim_config.get('race_type') == 'object_avoidance' and 'object_avoidance' in sim_config:
                                oa_config = sim_config['object_avoidance']
                                if not oa_config.get('randomize_object_locations', True):
                                    object_locations_html = "<li><b>Object Locations:</b></li><ul>"
                                    for loc in oa_config.get('object_locations', []):
                                        object_locations_html += f"<li>progress: {loc.get('progress', 'N/A')}, lane: {loc.get('lane', 'N/A')}</li>"
                                    object_locations_html += "</ul>"
                                else:
                                    object_locations_html = ""
                                    
                                object_avoidance_html = f"""
                                <li><b>Object Avoidance:</b></li>
                                <ul>
                                    <li><b>Object Type:</b> {oa_config.get('object_type', 'N/A')}</li>
                                    <li><b>Number of Objects:</b> {oa_config.get('number_of_objects', 'N/A')}</li>
                                    <li><b>Min Distance:</b> {oa_config.get('min_distance_between_objects', 'N/A')}</li>
                                    <li><b>Randomize Locations:</b> {oa_config.get('randomize_object_locations', 'N/A')}</li>
                                    {object_locations_html}
                                </ul>
                                """
                            
                            track_name = tracks_info.get(sim_config.get('track_id', ''), {}).get('track_name', sim_config.get('track_id', 'Unknown'))
                            
                            test_simulation_display.value = f"""
                                <h4>Test Simulation</h4>
                                <ul>
                                    <li><b>Race Type:</b> {sim_config.get('race_type', 'N/A')}</li>
                                    {object_avoidance_html}
                                </ul>
                            """
                        else:
                            test_simulation_display.value = "<h4>Test Simulation</h4><p>No simulation info available</p>"
                        
                        # Test settings
                        if 'test' in test_config:
                            test_settings = test_config['test']
                            penalty_html = ""
                            if 'penalty' in test_settings:
                                penalty = test_settings['penalty']
                                penalty_html = f"""
                                <li><b>Penalties:</b></li>
                                <ul>
                                    <li><b>Crashed:</b> {penalty.get('is_crashed', 'N/A')}</li>
                                    <li><b>Off-track:</b> {penalty.get('is_offtrack', 'N/A')}</li>
                                </ul>
                                """
                            
                            test_settings_display.value = f"""
                                <h4>Test Settings</h4>
                                <ul>
                                    <li><b>Checkpoint:</b> {test_settings.get('checkpoint', 'N/A')}</li>
                                    <li><b>Number of Trials:</b> {test_settings.get('number_of_trials', 'N/A')}</li>
                                    {penalty_html}
                                </ul>
                            """
                        else:
                            test_settings_display.value = "<h4>Test Settings</h4><p>No test settings available</p>"
                            
                    except Exception as e:
                        test_simulation_display.value = f"<h4>Test Simulation</h4><p>Error loading simulation info: {e}</p>"
                        test_settings_display.value = f"<h4>Test Settings</h4><p>Error loading test settings: {e}</p>"
                        
                except Exception as e:
                    test_metrics_display.value = f"<p>Error loading test details: {e}</p>"
                    test_video_display.value = ""
                    test_simulation_display.value = ""
                    test_settings_display.value = ""
            
            # Update details for initial test
            if selected_test_name:
                update_test_details(selected_test_name)
            
            # Test selector change handler
            def on_test_change(change):
                selected_test = change['new']
                update_test_details(selected_test)
            
            test_selector.observe(on_test_change, names='value')
            
            # Layout
            return widgets.VBox([
                test_selector,
                widgets.HBox([
                    widgets.VBox([
                        test_metrics_display
                    ], layout=widgets.Layout(width='60%', padding='0 5px 0 0')),
                    widgets.VBox([
                        test_video_display
                    ], layout=widgets.Layout(width='40%', padding='0 0 0 5px'))
                ]),
                widgets.HBox([
                    widgets.VBox([
                        test_simulation_display
                    ], layout=widgets.Layout(width='50%', padding='0 5px 0 0')),
                    widgets.VBox([
                        test_settings_display
                    ], layout=widgets.Layout(width='50%', padding='0 0 0 5px'))
                ])
            ])
            
        except Exception as e:
            return widgets.VBox([
                widgets.HTML(f"<h3>Error loading tests: {e}</h3>")
            ])

    test_mode_display = widgets.VBox([
        create_test_mode_display(model)
    ], layout = widgets.Layout(display="none"))

    common_display = widgets.VBox([
        widgets.VBox([])
    ])



    display(
        main_display := widgets.VBox([
            model_status := widgets.HTML(
                value=f"<b>[Status] {model.get_status() if model else ''}</b>"
            ),
            physical_car_model,
            mode_type := widgets.ToggleButtons(
                options=['Training', 'Test'],
                value='Training',
                description="Mode ",
                disabled=False,
                button_style='',
            ),
            
            training_mode_display,
            test_mode_display,
            vehicle_info,
            reward_function
        ])
    )
    def _update_mode(change):
        if change['new'] == 'Training':
            training_mode_display.layout.display = ''
            test_mode_display.layout.display = 'none'
        else:
            training_mode_display.layout.display = 'none'
            test_mode_display.layout.display = ''
    mode_type.observe(_update_mode, names='value')

    # Start auto refresh timer if enabled
    if auto_refresh_toggle.value:
        auto_refresh_active = True
        start_timer = create_timer()
        start_timer()


