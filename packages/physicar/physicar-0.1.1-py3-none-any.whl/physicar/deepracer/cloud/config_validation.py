import os
import yaml
import re
import json
import pkg_resources
import os
import json
import time
from physicar.deepracer.cloud.utils import read_yaml, write_yaml
from physicar.deepracer.cloud.constants import CAR_NAME, MODEL_PATH, TRACK_INFO_PATH, CONFIG_PATH, CONFIG_LOCK_PATH, DRFC_PATH 
from physicar.deepracer.cloud.locales.warnings import warnings_trans

def get_warning_trans(target, lang, params=None):
    lang = lang if lang in warnings_trans else "en"
    warning = warnings_trans[lang][target]
    warning_title = warning['title']
    warning_message = warning['message']
    if params:
        warning_message = warning_message.format(**params)
    return {
        "title": warning_title,
        "message": warning_message
    }

def rename_model_name(model_name):
    model_path = os.path.join(MODEL_PATH, model_name)
    if not os.path.exists(model_path):
        return model_name
    else:
        i = 1
        while True:
            new_model_name = f"{model_name}-{i}"
            new_model_path = os.path.join(MODEL_PATH, new_model_name)
            if not os.path.exists(new_model_path):
                return new_model_name
            i += 1

def deepkey_in_dict(d: dict, deepkey: list):
    child = d
    try:
        for key in deepkey:
            child = child[key]
        return True
    except :
        return False

# 모델 경로가 존재하는지 확인하는 함수
def check_model_path(model_name):
    model_path = os.path.join(MODEL_PATH, model_name)
    if not os.path.exists(model_path):
        raise ValueError(f"not found {model_path}")
    return model_path

def load_json_again(file_path, try_count=3, sleep_time=1):
    file_path = os.path.abspath(os.path.expanduser(file_path))
    for _ in range(try_count):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data
        except:
            time.sleep(sleep_time)
    raise ValueError(f"failed to load {file_path} after {try_count} tries.")
    

# 모델 파일이 정상적인지 확인하는 함수
def check_model_files(model_name):
    model_root_path = check_model_path(model_name)
    model_path = os.path.join(model_root_path, "model")
    model_file_list = os.listdir(model_path)

    model_data = {}

    model_metadata_path = os.path.join(model_path, "model_metadata.json")
    if not os.path.exists(model_metadata_path):
        raise ValueError(f"not found {model_metadata_path}")
    model_metadata = load_json_again(model_metadata_path)
    model_data['model_metadata'] = model_metadata

    model_checkpoints_path = os.path.join(model_path, "deepracer_checkpoints.json")
    if not os.path.exists(model_checkpoints_path):
        raise ValueError(f"not found {model_checkpoints_path}")
    model_checkpoints = load_json_again(model_checkpoints_path)
    model_data['model_checkpoints'] = model_checkpoints

    best_checkpoints_name = model_checkpoints['best_checkpoint']['name']
    if not f"{best_checkpoints_name}.data-00000-of-00001" in model_file_list:
        raise ValueError(f"not found {best_checkpoints_name}.data-00000-of-00001")
    if not f"{best_checkpoints_name}.index" in model_file_list:
        raise ValueError(f"not found {best_checkpoints_name}.index")
    if not f"{best_checkpoints_name}.meta" in model_file_list:
        raise ValueError(f"not found {best_checkpoints_name}.meta")

    last_checkpoints_name = model_checkpoints['last_checkpoint']['name']
    if not f"{last_checkpoints_name}.data-00000-of-00001" in model_file_list:
        raise ValueError(f"not found {last_checkpoints_name}.data-00000-of-00001")
    if not f"{last_checkpoints_name}.index" in model_file_list:
        raise ValueError(f"not found {last_checkpoints_name}.index")
    if not f"{last_checkpoints_name}.meta" in model_file_list:
        raise ValueError(f"not found {last_checkpoints_name}.meta")

    metrics_path = os.path.join(model_root_path, "metrics/")
    training_metrics_path = os.path.join(metrics_path, "TrainingMetrics.json")
    if not os.path.exists(training_metrics_path):
        raise ValueError(f"not found {training_metrics_path}")
    training_metrics = load_json_again(training_metrics_path)
    model_data['training_metrics'] = training_metrics

    ip_path = os.path.join(model_root_path, "ip/")
    hyperparameters_path = os.path.join(ip_path, "hyperparameters.json")
    if not os.path.exists(hyperparameters_path):
        raise ValueError(f"not found {hyperparameters_path}")
    hyperparameters = load_json_again(hyperparameters_path)
    model_data['hyperparameters'] = hyperparameters

    return model_data


def get_max_sub_simulation_count(cpu_count: int = None):
    cpu_count = os.cpu_count() if cpu_count is None else cpu_count
    max_sub_simulation_count = max(int((cpu_count / 2) - 2), 0)
    return max_sub_simulation_count


def deep_update(original: dict, new_data: dict) -> dict:
    for key, value in new_data.items():
        if (
            key in original 
            and isinstance(original[key], dict) 
            and isinstance(value, dict)
        ):
            deep_update(original[key], value)
        else:
            original[key] = value
    return original


def get_tracks_info():
    with open(TRACK_INFO_PATH, "r") as file:
        tracks_info = yaml.safe_load(file)
    if tracks_info:
        for track_id, track_info in tracks_info.items():
            track_info["track_direction"] = [track_direction for track_direction in track_info["npy"] if track_info["npy"][track_direction]]
    return tracks_info

def config_preprocessing(config):
    ##### locked
    config_locked = read_yaml(CONFIG_LOCK_PATH)
    deep_update(config, config_locked)

    ##### Dynamic
    ## car name
    if not deepkey_in_dict(config, ["test", "car_name"]):
        if not deepkey_in_dict(config, ["test"]):
            config['test'] = {}
        config['test']['car_name'] = CAR_NAME
    
    ## num_episodes_between_training
    if not deepkey_in_dict(config, ["training"]):
        config['training'] = {}
    if not deepkey_in_dict(config, ["training", "algorithm"]):
        config['training']['algorithm'] = "PPO"
    if not deepkey_in_dict(config, ["training", "hyperparameters"]):
        config['training']['hyperparameters'] = {}
    if not deepkey_in_dict(config, ["simulation"]):
        config['simulation'] = {}
    if not deepkey_in_dict(config, ["simulation", "number_of_sub_simulations"]):
        config['simulation']['number_of_sub_simulations'] = 0
    
    if config['training']['algorithm'] == "SAC":
        config['training']['hyperparameters']['e_greedy_value'] = 0.05
        config['training']['hyperparameters']['exploration_type'] = "additive_noise"
    else:
        config['training']['hyperparameters']['e_greedy_value'] = 1.0
        config['training']['hyperparameters']['exploration_type'] = "categorical"

    number_of_sub_simulations = int(config["simulation"]["number_of_sub_simulations"])
    if number_of_sub_simulations == 0:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 1
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 10
            config['training']['hyperparameters']['num_epochs'] = 6
    if number_of_sub_simulations == 1:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 2
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 20
            config['training']['hyperparameters']['num_epochs'] = 5
    if number_of_sub_simulations == 2:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 3
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 30
            config['training']['hyperparameters']['num_epochs'] = 4
    if number_of_sub_simulations == 3:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 4
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 40
            config['training']['hyperparameters']['num_epochs'] = 3
    if number_of_sub_simulations == 4:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 5
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 50
            config['training']['hyperparameters']['num_epochs'] = 3
    if number_of_sub_simulations == 5:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 6
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 60
            config['training']['hyperparameters']['num_epochs'] = 2
    if number_of_sub_simulations == 6:
        if config['training']['algorithm'] == "SAC":
            config['training']['hyperparameters']['num_episodes_between_training'] = 7
        else:
            config['training']['hyperparameters']['num_episodes_between_training'] = 70
            config['training']['hyperparameters']['num_epochs'] = 2
    
    return config




#### file read/write functions ####
def read_env_file(file_path: str):
    file_path = os.path.abspath(os.path.expanduser(file_path))
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return lines

def read_json_file(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def update_env(lines, var_name, new_value):
    found = False
    for i, line in enumerate(lines):
        # 공백이 있거나 주석(#) 같은 예외 처리가 필요한 경우 추가 로직
        # 여기서는 단순히 "키="로 시작하는지만 확인
        if line.startswith(f"{var_name}="):
            lines[i] = f"{var_name}={new_value}\n"
            found = True
        if not line.endswith("\n"):
            lines[i] += "\n"

    # 파일에 해당 키가 없었다면 새로 추가
    if not found:
        lines.append("")
        lines.append(f"{var_name}={new_value}\n")

def update_json(data, var_name, new_value):
    data[var_name] = new_value

def write_env_file(file_path: str, lines):
    file_path = os.path.abspath(os.path.expanduser(file_path))
    with open(file_path, 'w') as f:
        f.writelines(lines)

def write_json_file(file_path: str, data):
    file_path = os.path.abspath(os.path.expanduser(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)




#### validate functions ####
def validate_str(value, value_show):
    try :
        value = str(value)
        value = value.strip()
        return value
    except :
        raise ValueError(f"{value_show} must be a string.")
    
def validate_int(value, value_show):
    try :
        value = int(value)
        return value
    except :
        raise ValueError(f"{value_show} must be a int.")

def validate_float(value, value_show):
    try :
        value = float(value)
        return value
    except :
        raise ValueError(f"{value_show} must be a float.")

def validate_bool(value, value_show):
    try :
        value = bool(value)
        return value
    except :
        raise ValueError(f"{value_show} must be a bool.")

def validate_list(value, value_show):
    if not isinstance(value, list):
        raise ValueError(f"{value_show} must be a list.")
    return value

def validate_number_range(value: float, value_show: str, min_value, max_value: float):
    if value < min_value or value > max_value:
        raise ValueError(f"{value_show} must be between {min_value} and {max_value}.'")

def validate_last_digit(value: int, value_show: str, last_digit: int):
    if value % 10 != last_digit:
        raise ValueError(f"{value_show} must be a {last_digit} digit.")

def validate_str_len(value: str, value_show: str, min_len: int, max_len: int):
    if len(value) < min_len or len(value) > max_len:
        raise ValueError(f"{value_show} must be between {min_len} and {max_len} characters.")

def validate_str_regex(value: str, value_show: str, regex: str, regex_desc: str):
    if not re.match(regex, value):
        raise ValueError(f"{value_show} is not match {regex_desc}.")

def validate_system_performance(value: int, value_show: str):
    max_sub_simulation_count = get_max_sub_simulation_count()
    if value > max_sub_simulation_count:
        raise ValueError(f"{value_show} is too high. - max: '{max_sub_simulation_count}'")

def validate_less_than(value: float, value_show: str, compare_value: float):
    if value >= compare_value:
        raise ValueError(f"'{value_show}' must be less than high({compare_value}).")
    
def validate_list_len(value: list, value_show: str, min_len: int, max_len: int):
    if len(value) < min_len or len(value) > max_len:
        raise ValueError(f"{value_show} must be between {min_len} and {max_len} items.")

def validate_no_duplicate(value, value_show, existing_values):
    if value in existing_values:
        raise ValueError(f"{value_show}: '{value}' already exists (duplicate).")

def validate_include(value, value_show, include_values):
    include_values = list(include_values)
    if value not in include_values:
        raise ValueError(f"{value_show} must be one of {include_values}.")

def validate_same(value, value_show, compare_value):
    if value != compare_value:
        raise ValueError(f"{value_show} must be same as '{compare_value}'.")

def validate_not_same(value, value_show, compare_value):
    if value == compare_value:
        raise ValueError(f"{value_show} must be different from '{compare_value}'.")

def validate_pretrained_model_files(value, value_show):
    try :
        check_model_files(value)
    except ValueError as e:
        # 모델 파일이 존재하지 않거나 잘못된 경우
        raise ValueError(f"{value_show} must be a valid model name.\n- error: {e}")

def validate_pretrained_model_algorithm(value, value_show, pretrained_model_name):
    pretrained_model_data = check_model_files(pretrained_model_name)
    pretrained_algorithm = pretrained_model_data["model_metadata"]["training_algorithm"]
    if pretrained_algorithm == "clipped_ppo":
        pretrained_algorithm = "PPO"
    elif pretrained_algorithm == "sac":
        pretrained_algorithm = "SAC"
    else :
        raise ValueError(f"unknown pretrained algorithm: {pretrained_algorithm}")

    if value != pretrained_algorithm:
        raise ValueError(f"{value_show} must be same as pretrained algorithm ('{pretrained_algorithm}').")

def validate_pretrained_model_action_space_type(value, value_show, pretrained_model_name):
    pretrained_model_data = check_model_files(pretrained_model_name)
    pretrained_action_space_type = pretrained_model_data["model_metadata"]["action_space_type"]
    if value != pretrained_action_space_type:
        raise ValueError(f"{value_show} must be same as pretrained action space type ('{pretrained_action_space_type}').")

def validate_pretrained_model_discrete_action_space_length(value, value_show, pretrained_model_name):
    pretrained_model_data = check_model_files(pretrained_model_name)
    pretrained_action_space_type = pretrained_model_data["model_metadata"]["action_space_type"]
    if pretrained_action_space_type == "discrete":
        pretrained_discrete_action_space_length = len(pretrained_model_data["model_metadata"]["action_space"])
        if len(value) != pretrained_discrete_action_space_length:
            raise ValueError(f"{value_show} must be same as pretrained discrete action space length ('{pretrained_discrete_action_space_length}').")

def validate_pretrained_model_name_is_different(value, value_show, pretrained_model_name):
    if value == pretrained_model_name:
        raise ValueError(f"{value_show} must be different from pretrained model name ('{pretrained_model_name}').")

def commit_config(config, updated_data):
    write_env_file(os.path.join(DRFC_PATH, "system.env"), updated_data["system.env"])
    write_env_file(os.path.join(DRFC_PATH, "run.env"), updated_data["run.env"])
    for i in range(2, 8):
        write_env_file(os.path.join(DRFC_PATH, f"worker-{i}.env"), updated_data[f"worker-{i}.env"])
    write_json_file(os.path.join(DRFC_PATH, "custom_files/hyperparameters.json"), updated_data["hyperparameters.json"])
    write_json_file(os.path.join(DRFC_PATH, "custom_files/model_metadata.json"), updated_data["model_metadata.json"])
    write_yaml(CONFIG_PATH, config)
    

class ConfigValidationError(Exception):
    def __init__(self, message, config_path=None, value=None):
        # message += f"\n- config_path: '{config_path}'"
        # message += f"\n- value: '{value}'"
        super().__init__(message)
        self.config_path = config_path
        self.value = value



sim_idx_list = ["main", "sub1", "sub2", "sub3", "sub4", "sub5", "sub6"]
value_show_dict = {
    "job_type": "Job Type",
    "model_name": "Model Name",
    "pretrained": "Pretrained",
    "pretrained_model_name": "Pretrained Model Name",
    "pretrained_checkpoint": "Pretrained Checkpoint",
    "system.enable_gui": "Enable GUI",
    "system.version": "Version",
    "system.enable_main_camera": "Enable Main Camera",
    "system.enable_sub_camera": "Enable Sub Camera",
    "system.enable_kvs_camera": "Enable KVS Camera",
    "system.train_multi_config": "Train Multi Config",
    "simulation.number_of_sub_simulations": "Number of Sub Simulations",
    **{f"simulation.{sim_idx}.car_color": f"Car Color ({sim_idx})" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.track_id": "Track" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.track_direction": f"Track Direction" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.alternate_training_direction": "Alternate Training Direction" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.race_type": "Race Type" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.object_avoidance.object_type": "Object Type" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.object_avoidance.number_of_objects": "Number of Objects" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.object_avoidance.randomize_object_locations": "Randomize Object Locations" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.object_avoidance.min_distance_between_objects": "Minimum Distance Between Objects" for sim_idx in sim_idx_list},
    **{f"simulation.{sim_idx}.object_avoidance.object_locations": "Object Locations" for sim_idx in sim_idx_list},
    "vehicle.layout": "Layout",
    "vehicle.sensor.camera": "Camera",
    "vehicle.sensor.lidar": "Lidar",
    "vehicle.action_space_type": "Action Space Type",
    "vehicle.action_space.continuous": "Continuous Action Space",
    "vehicle.action_space.continuous.steering_angle.high": "Angle High",
    "vehicle.action_space.continuous.steering_angle.low": "Angle Low",
    "vehicle.action_space.continuous.speed.high": "Speed High",
    "vehicle.action_space.continuous.speed.low": "Speed Low",
    "vehicle.action_space.discrete": "Discrete Action Space",
    "vehicle.neural_network": "Neural Network",
    "vehicle.sensor.preprocess_type": "Sensor Preprocess Type",
    "training.algorithm": "Algorithm",
    "training.round_robin_advanced": "Training Round Robin Advanced",
    "training.min_evaluation_number_of_trials": "Minimum Evaluation Number of Trials",
    "training.hyperparameters.batch_size": "Batch Size",
    "training.hyperparameters.discount_factor": "Discount Factor",
    "training.hyperparameters.learning_rate": "Learning Rate",
    "training.hyperparameters.loss_type": "Loss Type",
    "training.hyperparameters.entropy": "Entropy",
    "training.hyperparameters.sac_alpha": "SAC Alpha",
    "training.hyperparameters.e_greedy_value": "E-Greedy Value",
    "training.hyperparameters.epsilon_steps": "Epsilon Steps",
    "training.hyperparameters.exploration_type": "Exploration Type",
    "training.hyperparameters.stack_size": "Stack Size",
    "training.hyperparameters.term_cond_avg_score": "Term Condition Average Score",
    "training.hyperparameters.term_cond_max_episodes": "Term Condition Max Episodes",
    "training.hyperparameters.num_episodes_between_training": "Number of experience episodes between each policy-updating iteration",
    "training.hyperparameters.num_epochs": "Epochs",
    "training.best_model_metric": "Best Model Metric",
    "auto_test_after_training": "Automatic Test After Training",
    "test.number_of_trials": "Minimum laps",
    "test.checkpoint": "Checkpoint",
    "test.penalty.is_offtrack": "Off-track penalty",
    "test.penalty.is_crashed": "Collision penalty",
    "test.max_resets": "Max Resets",
    "test.is_continuous": "Continuous Test",
    "test.save_mp4": "Save MP4",
    "test.crash_reset_behind_dist": "Distance to reset behind crash",
    "test.car_name": "Car Name",
}


class ConfigValidator:
    def __init__(self, config, lang="en", warnings=None, tracks_info=None, updated_data=None, parent=None, name=None):
        self._parent = parent
        self._name = name
        self.config = config
        self.warnings = [] if warnings is None else warnings
        self.lang = lang
        self.tracks_info = get_tracks_info() if tracks_info is None else tracks_info
        self.updated_data = {
            "system.env": read_env_file(os.path.join(DRFC_PATH, "system.env")),
            "run.env": read_env_file(os.path.join(DRFC_PATH, "run.env")),
            **{f"worker-{i}.env": read_env_file(os.path.join(DRFC_PATH, "defaults/template-worker.env")) for i in range(2, 8)},
            "hyperparameters.json": read_json_file(os.path.join(DRFC_PATH, "defaults/hyperparameters.json")),
            "model_metadata.json": read_json_file(os.path.join(DRFC_PATH, "defaults/model_metadata.json")),
        } if updated_data is None else updated_data

        if parent is None:
            if not deepkey_in_dict(self.config, ["job_type"]):
                raise Exception("'job_type' is not found in config.")
            if not deepkey_in_dict(self.config, ["model_name"]):
                raise Exception("'model_name' is not found in config.")
            if self.config['job_type'] == "training":
                if not deepkey_in_dict(self.config, ["pretrained"]):
                    self.config["pretrained"] = False
                if self.config["pretrained"]:
                    if not deepkey_in_dict(self.config, ["pretrained_checkpoint"]):
                        self.config["pretrained_checkpoint"] = "best"
                    if not deepkey_in_dict(self.config, ["pretrained_model_name"]):
                        raise Exception("'pretrained_model_name' is not found in config.training.")
                else:
                    if not deepkey_in_dict(self.config, ["training", "algorithm"]):
                        self.config["training"]["algorithm"] = "PPO"
            target_sim_idx_list = ["main"] + ([f"sub{i}" for i in range(1, int(config["simulation"]["number_of_sub_simulations"]) + 1)] if config["job_type"] == "training" else [])
            for sim_idx in target_sim_idx_list:
                if not deepkey_in_dict(self.config, ["simulation", sim_idx, "track_id"]):
                    raise Exception(f"'track_id' is not found in config.simulation.{sim_idx}.")    
                if not deepkey_in_dict(self.config, ["simulation", sim_idx, "track_direction"]):
                    self.config["simulation"][sim_idx]["track_direction"] = "counterclockwise"
                # if not deepkey_in_dict(self.config, ["simulation", sim_idx, "race_type"]):
                #     self.config["simulation"][sim_idx]["race_type"] = "time_trial"
                # if self.config["simulation"][sim_idx]["race_type"] == "object_avoidance":
                #     if not deepkey_in_dict(self.config, ["simulation", sim_idx, "object_avoidance", "object_type"]):
                #         self.config["simulation"][sim_idx]["object_avoidance"]["object_type"] = "box"
                #     if not deepkey_in_dict(self.config, ["simulation", sim_idx, "object_avoidance", "object_positions"]):
                #         self.config["simulation"][sim_idx]["object_avoidance"]["object_positions"] = [{"progress":33, "lane": "inside"}, {"progress":67, "lane": "outside"}]
                # if self.config["simulation"][sim_idx]["race_type"] == "head_to_bot":
                #     if not deepkey_in_dict(self.config, ["simulation", sim_idx, "head_to_bot", "number_of_bot"]):
                #         self.config["simulation"][sim_idx]["head_to_bot"]["number_of_bot"] = 3
                #     if not deepkey_in_dict(self.config, ["simulation", sim_idx, "head_to_bot", "bot_speed"]):
                #         self.config["simulation"][sim_idx]["head_to_bot"]["bot_speed"] = 0.5
                #     if not deepkey_in_dict(self.config, ["simulation", sim_idx, "head_to_bot", "allow_lane_change"]):
                #         self.config["simulation"][sim_idx]["head_to_bot"]["allow_lane_change"] = False
                #     if self.config["simulation"][sim_idx]["head_to_bot"]["allow_lane_change"]:
                #         if not deepkey_in_dict(self.config, ["simulation", sim_idx, "head_to_bot", "lane_change_time", "high"]):
                #             self.config["simulation"][sim_idx]["head_to_bot"]["lane_change_time"]["high"] = 5
                #         if not deepkey_in_dict(self.config, ["simulation", sim_idx, "head_to_bot", "lane_change_time", "low"]):
                #             self.config["simulation"][sim_idx]["head_to_bot"]["lane_change_time"]["low"] = 3

    def validate(self, target_data=None, target_path=None):
        # 병렬처리 하지 말것
        if target_data is None:
            target_data = self.config
        if target_path is None:
            target_path = []
        for key, value in target_data.items():
            if isinstance(value, dict):
                self.validate(value, target_path + [key])
            else:
                chain = self
                for p in (target_path + [key]):
                    chain = getattr(chain, p)
                chain(value)
        return self.warnings
    
    # def commit(self):
    #     write_env_file(os.path.join(DRFC_PATH, "system.env"), self.updated_data["system.env"])
    #     write_env_file(os.path.join(DRFC_PATH, "run.env"), self.updated_data["run.env"])
    #     for i in range(2, 8):
    #         write_env_file(os.path.join(DRFC_PATH, f"worker-{i}.env"), self.updated_data[f"worker-{i}.env"])
    #     write_json_file(os.path.join(DRFC_PATH, "custom_files/hyperparameters.json"), self.updated_data["hyperparameters.json"])
    #     write_json_file(os.path.join(DRFC_PATH, "custom_files/model_metadata.json"), self.updated_data["model_metadata.json"])
    #     write_yaml(CONFIG_PATH, self.config)
        
    def _get_full_path(self):
        names = []
        node = self
        while node and node._name:
            names.append(node._name)
            node = node._parent
        return names[::-1]  # 역순으로 뒤집어서 반환

    # 속성 접근 (객체로 반환)
    def __getattr__(self, name):
        return ConfigValidator(
            config=self.config, 
            lang=self.lang,
            warnings=self.warnings,
            updated_data=self.updated_data,
            tracks_info=self.tracks_info,
            parent=self,
            name=name,
            
        )
    

    # 메소드 접근 (함수 실행)
    def __call__(self, value):
        full_path = self._get_full_path()
        config_path = ".".join(full_path)
        try :
            if "job_type" == config_path:
                value_show = value_show_dict[config_path]
                value = validate_str(value, value_show)
                validate_include(value, value_show, ["training", "test"])
                # no update
                return
            if "model_name" == config_path:
                value_show = value_show_dict[config_path]
                value = validate_str(value, value_show)
                existing_model_names = os.listdir(MODEL_PATH)
                if self.config["job_type"] == "training":
                    # if bool(self.config["pretrained"]):
                    #     validate_pretrained_model_name_is_different(value, value_show, self.config["pretrained_model_name"].strip())
                    # else:
                    validate_str_regex(value, value_show, r"^[a-zA-Z0-9_.-]+$", "alphanumeric characters, _, -, .")
                    validate_str_len(value, value_show, 1, 100)
                    model_name = rename_model_name(value)
                    if model_name != value:
                        self.warnings.append(get_warning_trans(target='model_rename', lang=self.lang, params={"value": value, "model_name": model_name}))
                        self.config["model_name"] = model_name
                    value = model_name
                elif self.config["job_type"] == "test":
                    validate_include(value, value_show, existing_model_names)

                update_env(self.updated_data["run.env"], "DR_LOCAL_S3_MODEL_PREFIX", f"models/{value}")
                return
            if "pretrained" == config_path:
                value_show = value_show_dict[config_path]
                value = validate_bool(value, value_show)
                update_env(self.updated_data["run.env"], "DR_LOCAL_S3_PRETRAINED", value)
                return
            if "pretrained_model_name" == config_path:
                if not bool(self.config["pretrained"]):
                    return
                value_show = value_show_dict[config_path]
                value = validate_str(value, value_show)
                validate_include(value, value_show, os.listdir(MODEL_PATH))
                validate_pretrained_model_files(value, value_show)
                update_env(self.updated_data["run.env"], "DR_LOCAL_S3_PRETRAINED_PREFIX", f"models/{value}")
                return
            if "pretrained_checkpoint" == config_path:
                if not bool(self.config["pretrained"]):
                    return
                value_show = value_show_dict[config_path]
                value = validate_str(value, value_show)
                validate_include(value, value_show, ["last", "best"])
                update_env(self.updated_data["run.env"], "DR_LOCAL_S3_PRETRAINED_CHECKPOINT", value)
                return
            ######## system ########
            if config_path.startswith("system."):
                if "system.enable_gui" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_bool(value, value_show)
                    update_env(self.updated_data["system.env"], "DR_GUI_ENABLE", value)
                    return
                if "system.version" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    validate_include(value, value_show, ["5"])
                    update_json(self.updated_data["model_metadata.json"], "version", value)
                    return
                if "system.enable_main_camera" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_bool(value, value_show)
                    update_env(self.updated_data["system.env"], "DR_CAMERA_MAIN_ENABLE", value)
                    return
                if "system.enable_sub_camera" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_bool(value, value_show)
                    update_env(self.updated_data["system.env"], "DR_CAMERA_SUB_ENABLE", value)
                    return
                if "system.enable_kvs_camera" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_bool(value, value_show)
                    update_env(self.updated_data["system.env"], "DR_CAMERA_KVS_ENABLE", value)
                    return
                if "system.train_multi_config" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_bool(value, value_show)
                    update_env(self.updated_data["run.env"], "DR_TRAIN_MULTI_CONFIG", value)
                    return
                
            ######## simulation ########
            if config_path.startswith("simulation."):
                if "simulation.number_of_sub_simulations" == config_path:
                    if self.config["job_type"] != "training":
                        return
                    value_show = value_show_dict[config_path]
                    value = validate_int(value, value_show)
                    validate_number_range(value, value_show, 0, 6)
                    try :
                        validate_system_performance(value, value_show)
                    except ValueError:
                        self.warnings.append(get_warning_trans(target='simulation_count_high', lang=self.lang, params={"value": value}))
                    value_encoded = value + 1
                    update_env(self.updated_data["system.env"], "DR_WORKERS", value_encoded)
                    return
                
                for sim_idx in ["main", "sub1", "sub2", "sub3", "sub4", "sub5", "sub6"]:
                    if config_path.startswith(f"simulation.{sim_idx}."):
                        target_env_file = "run.env" if sim_idx == "main" else f"worker-{int(sim_idx[3:])+1}.env"
                        if (self.config["job_type"] == "test") and (sim_idx != "main"):
                            return
                        if sim_idx != "main":
                            if self.config["job_type"] == "test":
                                return
                            if int(sim_idx[-1]) > int(self.config["simulation"]["number_of_sub_simulations"]):
                                return
                        if f"simulation.{sim_idx}.car_color" == config_path: 
                            value_show = value_show_dict[config_path]
                            value = validate_str(value, value_show)
                            validate_include(value, value_show, ["Black", "Grey", "Blue", "Red", "Orange", "White", "Purple"])
                            target_env_file = "run.env" if sim_idx == "main" else f"worker-{int(sim_idx[3:])+1}.env"
                            update_env(self.updated_data[target_env_file], "DR_CAR_COLOR", value)
                            return
                        if f"simulation.{sim_idx}.track_id" == config_path:
                            value_show = value_show_dict[config_path]
                            value = validate_str(value, value_show)
                            validate_include(value, value_show, self.tracks_info.keys())
                            # no update (will be updated in track_direction)
                            return
                        if f"simulation.{sim_idx}.track_direction" == config_path:
                            track_id = self.config['simulation'][sim_idx]["track_id"]
                            value_show = value_show_dict[config_path]
                            value = validate_str(value, value_show)
                            track_direction_list = self.tracks_info[track_id]["track_direction"]
                            validate_include(value, value_show, track_direction_list)
                            npy_name = self.tracks_info[track_id]["npy"][value]
                            value_encoded = npy_name.split(".")[0]
                            update_env(self.updated_data[target_env_file], "DR_WORLD_NAME", value_encoded)
                            return
                        if f"simulation.{sim_idx}.alternate_training_direction" == config_path:
                            value_show = value_show_dict[config_path]
                            value = validate_bool(value, value_show)
                            update_env(self.updated_data[target_env_file], "DR_TRAIN_ALTERNATE_DRIVING_DIRECTION", value)
                            return
                        if f"simulation.{sim_idx}.race_type" == config_path:
                            value_show = value_show_dict[config_path]
                            value = validate_str(value, value_show)
                            validate_include(value, value_show, ["time_trial", "object_avoidance", "head_to_bot"])
                            value_encoded = value.upper()
                            update_env(self.updated_data[target_env_file], "DR_RACE_TYPE", value_encoded)
                            return
                        if config_path.startswith(f"simulation.{sim_idx}.object_avoidance."):
                            if not self.config["simulation"][sim_idx]["race_type"] == "object_avoidance":
                                return
                            if f"simulation.{sim_idx}.object_avoidance.object_type" == config_path:
                                value_show = value_show_dict[config_path]
                                value = validate_str(value, value_show)
                                validate_include(value, value_show, ["box", "deepracer_box", "amazon_box", "deepracer_car"])
                                if value == "deepracer_car":
                                    update_env(self.updated_data[target_env_file], "DR_OA_IS_OBSTACLE_BOT_CAR", True)
                                else :
                                    update_env(self.updated_data[target_env_file], "DR_OA_IS_OBSTACLE_BOT_CAR", False)
                                    update_env(self.updated_data[target_env_file], "DR_OA_OBSTACLE_TYPE", value + "_obstacle")
                                return
                            if f"simulation.{sim_idx}.object_avoidance.number_of_objects" == config_path:
                                value_show = value_show_dict[config_path]
                                value = validate_int(value, value_show)
                                validate_number_range(value, value_show, 1, 10)
                                update_env(self.updated_data[target_env_file], "DR_OA_NUMBER_OF_OBSTACLES", value)
                                return
                            if f"simulation.{sim_idx}.object_avoidance.randomize_object_locations" == config_path:
                                value_show = value_show_dict[config_path]
                                value = validate_bool(value, value_show)
                                update_env(self.updated_data[target_env_file], "DR_OA_RANDOMIZE_OBSTACLE_LOCATIONS", value)
                                update_env(self.updated_data[target_env_file], "DR_OA_OBJECT_POSITIONS", "")
                                return
                            if f"simulation.{sim_idx}.object_avoidance.min_distance_between_objects" == config_path:
                                value_show = value_show_dict[config_path]
                                value = validate_float(value, value_show)
                                validate_number_range(value, value_show, 0, 5)
                                update_env(self.updated_data[target_env_file], "DR_OA_MIN_DISTANCE_BETWEEN_OBSTACLES", value)
                                return
                            if f"simulation.{sim_idx}.object_avoidance.object_locations" == config_path:
                                if not self.config["simulation"][sim_idx]["object_avoidance"]["randomize_object_locations"]:
                                    value_show = value_show_dict[config_path]
                                    validate_list(value, value_show)
                                    number_of_objects = int(self.config["simulation"][sim_idx]["object_avoidance"]["number_of_objects"])
                                    value = value[:number_of_objects]
                                    for i, pos in enumerate(value):
                                        validate_float(pos["progress"], f"{value_show}-{i} Idx Progress")
                                        validate_number_range(pos["progress"], f"{value_show}-{i} Idx Progress", 0, 100)
                                        validate_str(pos["lane"], f"{value_show}-{i} Idx Lane")
                                        validate_include(pos["lane"], f"{value_show}-{i} Idx Lane", ["inside", "outside"])
                                    value_encoded = ";".join([f"{pos['progress']/100},{1 if pos['lane']=='inside' else -1}" for pos in value])
                                    value_encoded = f'"{value_encoded}"'
                                    update_env(self.updated_data[target_env_file], "DR_OA_OBJECT_POSITIONS", value_encoded)
                                return
                            
            ######## vehicle ########
            if config_path.startswith("vehicle."):
                if self.config["job_type"] == "test":
                    return
                if "vehicle.layout" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    validate_include(value, value_show, ["deepracer", "physicar-v1"])
                    # no update
                    return
                if "vehicle.sensor.camera" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_int(value, value_show)
                    validate_number_range(value, value_show, 1, 2)
                    value_encoded = self.updated_data["model_metadata.json"]["sensor"]
                    if value == 1:
                        if not "FRONT_FACING_CAMERA" in value_encoded:
                            value_encoded.append("FRONT_FACING_CAMERA")
                        if "STEREO_CAMERAS" in value_encoded:
                            value_encoded.remove("STEREO_CAMERAS")
                    else:
                        if not "STEREO_CAMERAS" in value_encoded:
                            value_encoded.append("STEREO_CAMERAS")
                        if "FRONT_FACING_CAMERA" in value_encoded:
                            value_encoded.remove("FRONT_FACING_CAMERA")
                    update_json(self.updated_data["model_metadata.json"], "sensor", value_encoded)
                    return
                if "vehicle.sensor.lidar" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_bool(value, value_show)
                    validate_number_range(value, value_show, 0, 1)
                    value_encoded = self.updated_data["model_metadata.json"]["sensor"]
                    if value :
                        if not "SECTOR_LIDAR" in value_encoded:
                            value_encoded.append("SECTOR_LIDAR")
                    else:
                        if "SECTOR_LIDAR" in value_encoded:
                            value_encoded.remove("SECTOR_LIDAR")
                    update_json(self.updated_data["model_metadata.json"], "sensor", value_encoded)
                    return
                if "vehicle.action_space_type" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    if self.config["training"]["algorithm"] == "SAC":
                        validate_include(value, value_show, ["continuous"])
                    else:
                        validate_include(value, value_show, ["continuous", "discrete"])
                    if bool(self.config["pretrained"]):
                        validate_pretrained_model_action_space_type(value, value_show, self.config["pretrained_model_name"])
                    update_json(self.updated_data["model_metadata.json"], "action_space_type", value)
                    return
                if config_path.startswith("vehicle.action_space.continuous."):
                    if self.config["vehicle"]["action_space_type"] != "continuous":
                        return
                    if "vehicle.action_space.continuous.steering_angle.high" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0, 30)
                        value_encoded = self.updated_data["model_metadata.json"]["action_space"]
                        if not isinstance(value_encoded, dict):
                            value_encoded = {"speed":{}, "steering_angle":{}}
                        value_encoded["steering_angle"]["high"] = value
                        update_json(self.updated_data["model_metadata.json"], "action_space", value_encoded)
                        return
                    if "vehicle.action_space.continuous.steering_angle.low" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, -30, 0)
                        validate_less_than(value, value_show, float(self.config["vehicle"]["action_space"]["continuous"]["steering_angle"]["high"]))
                        value_encoded = self.updated_data["model_metadata.json"]["action_space"]
                        if not isinstance(value_encoded, dict):
                            value_encoded = {"speed":{}, "steering_angle":{}}
                        value_encoded["steering_angle"]["low"] = value
                        update_json(self.updated_data["model_metadata.json"], "action_space", value_encoded)
                        return
                    if "vehicle.action_space.continuous.speed.high" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 4)
                        value_encoded = self.updated_data["model_metadata.json"]["action_space"]
                        if not isinstance(value_encoded, dict):
                            value_encoded = {"speed":{}, "steering_angle":{}}
                        value_encoded["speed"]["high"] = value
                        update_json(self.updated_data["model_metadata.json"], "action_space", value_encoded)
                        return
                    if "vehicle.action_space.continuous.speed.low" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 4)
                        validate_less_than(value, value_show, float(self.config["vehicle"]["action_space"]["continuous"]["speed"]["high"]))
                        value_encoded = self.updated_data["model_metadata.json"]["action_space"]
                        if not isinstance(value_encoded, dict):
                            value_encoded = {"speed":{}, "steering_angle":{}}
                        value_encoded["speed"]["low"] = value
                        update_json(self.updated_data["model_metadata.json"], "action_space", value_encoded)
                        return
                if "vehicle.action_space.discrete" == config_path:
                    if self.config["vehicle"]["action_space_type"] != "discrete":
                        return
                    value_show = value_show_dict[config_path]
                    value = validate_list(value, value_show)
                    validate_list_len(value, value_show, 1, 30)
                    for i, action in enumerate(value):
                        validate_int(action["steering_angle"], f"{value_show}-{i} Steering Angle")
                        validate_number_range(action["steering_angle"], f"{value_show}-{i} Steering Angle", -30, 30)
                        validate_float(action["speed"], f"{value_show}-{i} Speed")
                        validate_number_range(action["speed"], f"{value_show}-{i} Speed", 0.1, 4)
                    if bool(self.config["pretrained"]):
                        validate_pretrained_model_discrete_action_space_length(value, value_show, self.config["pretrained_model_name"])
                    update_json(self.updated_data["model_metadata.json"], "action_space", value)
                    return
                #### locked
                if "vehicle.sensor.preprocess_type" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    validate_include(value, value_show, ["grey_scale", "rgb"])
                    value_encoded = "RGB" if value == "rgb" else "GREY_SCALE"
                    update_json(self.updated_data["model_metadata.json"], "preprocess_type", value_encoded)
                    return
                if "vehicle.neural_network" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    validate_include(value, value_show, ["3-layer-cnn", "5-layer-cnn"])
                    value_encoded = "DEEP_CONVOLUTIONAL_NETWORK_SHALLOW" if value == "3-layer-cnn" else "DEEP_CONVOLUTIONAL_NETWORK"
                    update_json(self.updated_data["model_metadata.json"], "neural_network", value_encoded)
                    return
                
            ######## training ########
            if config_path.startswith("training."):
                if self.config["job_type"] != "training":
                    return
                if "training.algorithm" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    validate_include(value, value_show, ["PPO", "SAC"])
                    value_encoded = "clipped_ppo" if value == "PPO" else "sac"
                    if bool(self.config["pretrained"]):
                        validate_pretrained_model_algorithm(value, value_show, self.config["pretrained_model_name"])
                    update_json(self.updated_data["model_metadata.json"], "training_algorithm", value_encoded)
                    return
                if "training.round_robin_advanced" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_float(value, value_show)
                    validate_number_range(value, value_show, 0.0, 1.0)
                    update_env(self.updated_data["run.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    update_env(self.updated_data["worker-2.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    update_env(self.updated_data["worker-3.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    update_env(self.updated_data["worker-4.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    update_env(self.updated_data["worker-5.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    update_env(self.updated_data["worker-6.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    update_env(self.updated_data["worker-7.env"], "DR_TRAIN_ROUND_ROBIN_ADVANCE_DIST", value)
                    return
                if "training.min_evaluation_number_of_trials" == config_path:
                    # locked
                    value_show = value_show_dict[config_path]
                    value = validate_int(value, value_show)
                    validate_number_range(value, value_show, 1, 10)
                    update_env(self.updated_data["run.env"], "DR_TRAIN_MIN_EVAL_TRIALS", value)
                    return
                if config_path.startswith("training.hyperparameters."):
                    if f"training.hyperparameters.batch_size" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_include(value, value_show, [16, 32, 64, 128, 256, 512])
                        update_json(self.updated_data["hyperparameters.json"], "batch_size", value)
                        return
                    if f"training.hyperparameters.discount_factor" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 1.0)
                        update_json(self.updated_data["hyperparameters.json"], "discount_factor", value)
                        return
                    if f"training.hyperparameters.learning_rate" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 1e-8, 1e-3)
                        update_json(self.updated_data["hyperparameters.json"], "lr", value)
                        return
                    if f"training.hyperparameters.loss_type" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_str(value, value_show)
                        validate_include(value, value_show, ["huber", "mean_squared_error"])
                        update_json(self.updated_data["hyperparameters.json"], "loss_type", value)
                        return
                    if f"training.hyperparameters.entropy" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 1.0)
                        update_json(self.updated_data["hyperparameters.json"], "beta_entropy", value)
                        return
                    if f"training.hyperparameters.sac_alpha" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 1.0)
                        update_json(self.updated_data["hyperparameters.json"], "sac_alpha", value)
                        return
                    if f"training.hyperparameters.e_greedy_value" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 1.0)
                        update_json(self.updated_data["hyperparameters.json"], "e_greedy_value", value)
                        return
                    if f"training.hyperparameters.epsilon_steps" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 1000000)
                        update_json(self.updated_data["hyperparameters.json"], "epsilon_steps", value)
                        return
                    if f"training.hyperparameters.exploration_type" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_str(value, value_show)
                        validate_include(value, value_show, ["categorical", "additive_noise"])
                        update_json(self.updated_data["hyperparameters.json"], "exploration_type", value)
                        return 
                    if f"training.hyperparameters.stack_size" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 10)
                        update_json(self.updated_data["hyperparameters.json"], "stack_size", value)
                        return
                    if f"training.hyperparameters.term_cond_avg_score" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 1000000.0)
                        update_json(self.updated_data["hyperparameters.json"], "term_cond_avg_score", value)
                        return
                    if f"training.hyperparameters.term_cond_max_episodes" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 1000000)
                        update_json(self.updated_data["hyperparameters.json"], "term_cond_max_episodes", value)
                        return
                    if f"training.hyperparameters.num_episodes_between_training" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 100)
                        update_json(self.updated_data["hyperparameters.json"], "num_episodes_between_training", value)
                        return
                    if f"training.hyperparameters.num_epochs" == config_path: 
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 100)
                        update_json(self.updated_data["hyperparameters.json"], "num_epochs", value)
                        return
                if "training.best_model_metric" == config_path:
                    value_show = value_show_dict[config_path]
                    value = validate_str(value, value_show)
                    validate_include(value, value_show, ["progress", "reward"])
                    update_env(self.updated_data["run.env"], "DR_TRAIN_BEST_MODEL_METRIC", value)
                    return
                
            ######## auto test ########
            if "auto_test_after_training" == config_path:
                value_show = value_show_dict[config_path]
                value = validate_bool(value, value_show)
                # no update
                return

            ######## test ########
            if config_path.startswith("test."):
                if (self.config["job_type"] == "test") or (bool(self.config["auto_test_after_training"])):
                    if "test.number_of_trials" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 20)
                        update_env(self.updated_data["run.env"], "DR_EVAL_NUMBER_OF_TRIALS", value)
                        return
                    if "test.checkpoint" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_str(value, value_show)
                        validate_include(value, value_show, ["last", "best"])
                        update_env(self.updated_data["run.env"], "DR_EVAL_CHECKPOINT", value)
                        return
                    if "test.penalty.is_offtrack" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 60.0)
                        update_env(self.updated_data["run.env"], "DR_EVAL_OFF_TRACK_PENALTY", value)
                        return
                    if "test.penalty.is_crashed" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        validate_number_range(value, value_show, 0.0, 60.0)
                        update_env(self.updated_data["run.env"], "DR_EVAL_COLLISION_PENALTY", value)
                        return
                    #### locked & dynamic
                    if "test.max_resets" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_int(value, value_show)
                        validate_number_range(value, value_show, 1, 100)
                        update_env(self.updated_data["run.env"], "DR_EVAL_MAX_RESETS", value)
                        return
                    if "test.is_continuous" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_bool(value, value_show)
                        update_env(self.updated_data["run.env"], "DR_EVAL_IS_CONTINUOUS", value)
                        return
                    if "test.save_mp4" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_bool(value, value_show)
                        update_env(self.updated_data["run.env"], "DR_EVAL_SAVE_MP4", value)
                        return
                    if "test.crash_reset_behind_dist" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_float(value, value_show)
                        update_env(self.updated_data["run.env"], "DR_EVAL_RESET_BEHIND_DIST", value)
                        return
                    if "test.car_name" == config_path:
                        value_show = value_show_dict[config_path]
                        value = validate_str(value, value_show)
                        validate_str_len(value, value_show, 1, 100)
                        update_env(self.updated_data["run.env"], "DR_CAR_NAME", value)
                        return
                else:
                    return
                    
            ######## commit ########
            if config_path.startswith("commit."):
                return
            
        except Exception as e:
            raise ConfigValidationError(
                message=str(e),
                config_path=config_path,
                value=value
            ) 
        ######## exception ValueError ########
        raise ConfigValidationError(
            message="Invalid path",
            config_path=config_path,
            value=value
        )

