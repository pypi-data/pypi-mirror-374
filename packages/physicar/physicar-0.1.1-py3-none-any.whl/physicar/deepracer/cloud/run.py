import subprocess
import pickle
import os
import pandas as pd
import time
import threading
import warnings
warnings.filterwarnings(action='ignore')

from physicar.deepracer.cloud.utils import (
    MyTurn,
    read_yaml,
    write_yaml,
)
from physicar.deepracer.cloud.config_validation import (
    config_preprocessing,
    ConfigValidator,
    commit_config,
    get_warning_trans
)
from physicar.deepracer.cloud.debug_reward_function import (
    commit_reward_function,
    run_debug_reward_function
)
from physicar.deepracer.cloud.constants import DRFC_PATH, CONFIG_PATH, JOB_PATH, MODEL_PATH


def run_command(
        cmd,  
        _prefix=f"source {os.path.join(DRFC_PATH, "bin/activate.sh")}",
        _background=False,
        _capture_output=True, 
        _print=False,
        
    ):
    final_cmd = f"(\n{_prefix}\n{cmd}\n)" 

    _capture_output = False if _background else _capture_output
    _print = False if not _capture_output else _print

    if not _capture_output:
        final_cmd += " >/dev/null 2>&1"
    if _background:
        final_cmd += " &"

    # print(final_cmd)
    response = subprocess.run(
        final_cmd, 
        shell=True, 
        executable="/bin/bash",
        capture_output=_capture_output,
        text=True
    )

    if _print:
        print("STDOUT:", response.stdout)
        print("STDERR:", response.stderr)
        print("Return code:", response.returncode)
    
    return response

def stop_job(
        _prefix=f"source {os.path.join(DRFC_PATH, "bin/activate.sh")}",
        _background=False,
        _capture_output=False,
        _print=False,
    ):

    cmd = """dr-stop-training && dr-stop-evaluation && docker ps -a --format="{{.ID}} {{.Names}}" | grep -v "s3-minio" | awk '{print $1}' | xargs -r docker rm -f """
    
    response = run_command(
        cmd=cmd,
        _capture_output=_capture_output,
        _prefix=_prefix,
        _print=_print,
        _background=_background
    )
    return response


def start_training(
        stop_training=True,
        stop_test=True,
        update=True,
        upload_custom_files=True,
        overwrite=True,
        detach=True,
        
        _prefix=f"source {os.path.join(DRFC_PATH, "bin/activate.sh")}",
        _background=False,
        _capture_output=False,
        _print=False,
    ):

    cmd = ""
    if stop_training:
        cmd += "dr-stop-training && "
    if stop_test:
        cmd += "dr-stop-evaluation && "
    if stop_training or stop_test:
        cmd += """docker ps -a --format="{{.ID}} {{.Names}}" | grep -v "s3-minio" | awk '{print $1}' | xargs -r docker rm -f && """
    if update:
        cmd += "dr-update && "
    if upload_custom_files:
        cmd += "dr-upload-custom-files && "

    cmd += "dr-start-training"
    if overwrite:
        cmd += " -w"
    if detach:
        cmd += " -q"
    
    response = run_command(
        cmd=cmd,
        _capture_output=_capture_output,
        _prefix=_prefix,
        _print=_print,
        _background=_background
    )
    return response


def docker_logs(
        container_name,
        log_path,
        contain_stderr=False,

        _prefix=f"source {os.path.join(DRFC_PATH, "bin/activate.sh")}",
        _background=False,
        _capture_output=False,
        _print=False,
    ):

    cmd = f"docker logs {container_name} > {log_path}"
    if contain_stderr:
        cmd += " 2>&1"

    response = run_command(
        cmd=cmd,
        _capture_output=_capture_output,
        _prefix=_prefix,
        _print=_print,
        _background=_background
    )
    return response

def health_check_tar_gz(file_path):
    cmd = f"gzip -t {file_path}"
    response = run_command(
        cmd=cmd,
        _capture_output=True,
        _prefix="",
        _print=False,
        _background=False
    )

    if response.stderr :
        return False
    else:
        return True



def upload_car_zip(
        _prefix=f"source {os.path.join(DRFC_PATH, "bin/activate.sh")}",
        _background=False,
        _capture_output=False,
        _print=False,
    ):
    cmd = "dr-upload-car-zip -fL"

    response = run_command(
        cmd=cmd,
        _capture_output=_capture_output,
        _prefix=_prefix,
        _print=_print,
        _background=_background
    )
    return response

def start_test(
        stop_training=True,
        stop_test=True,
        detach=True,

        _prefix=f"source {os.path.join(DRFC_PATH, "bin/activate.sh")}",
        _background=False,
        _capture_output=False,
        _print=False,
    ):

    cmd = ""
    if stop_training:
        cmd += "dr-stop-training && "
    if stop_test:
        cmd += "dr-stop-evaluation && "
    if stop_training or stop_test:
        cmd += """docker ps -a --format="{{.ID}} {{.Names}}" | grep -v "s3-minio" | awk '{print $1}' | xargs -r docker rm -f && """
    
    cmd += "dr-start-evaluation"
    if detach:
        cmd += " -q"

    response = run_command(
        cmd=cmd,
        _capture_output=_capture_output,
        _prefix=_prefix,
        _print=_print,
        _background=_background
    )
    return response


def get_workers_docker_id(workers_file_path = os.path.join(DRFC_PATH, "tmp/comms.0/workers")):
    workers_file_path = os.path.abspath(os.path.expanduser(workers_file_path))
    if not os.path.exists(workers_file_path):
        return []
    with open(workers_file_path) as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
    return lines

def robomaker_port_extract(dr_sim, job_type='training'):
    if dr_sim.shape[0] > 0:
        dr_sim = dr_sim.copy()
        dr_sim['view_port'] = dr_sim['Ports'].apply(lambda x: int(x.split('->8080/tcp')[0].split(':')[-1]) if x else 0)
        if job_type == 'training':
            dr_sim['vnc_port'] = dr_sim['Ports'].apply(lambda x: int(x.split('->5900/tcp')[0].split(':')[-1]) if x else 0)
    return dr_sim

def get_df_docker_ps_all():
    response = run_command(
        cmd = "docker ps -a --format '{{.ID}};{{.Image}};{{.Command}};{{.CreatedAt}};{{.Status}};{{.Ports}};{{.Names}}'",
        _prefix="",
        _background=False,
        _capture_output=True,
    )
    output = response.stdout
    lines = output.strip().split('\n')
    data = [line.split(';') for line in lines if line.strip()]
    columns = ['ID', 'Image', 'Command', 'CreatedAt', 'Status', 'Ports', 'Names']
    df = pd.DataFrame(data, columns=columns)
    df = df.set_index('ID')
    return df

def get_df_docker_ps():
    response = run_command(
        cmd = "docker ps --format '{{.ID}};{{.Image}};{{.Command}};{{.CreatedAt}};{{.Status}};{{.Ports}};{{.Names}}'",
        _prefix="",
        _background=False,
        _capture_output=True,
    )
    output = response.stdout
    lines = output.strip().split('\n')
    data = [line.split(';') for line in lines if line.strip()]
    columns = ['ID', 'Image', 'Command', 'CreatedAt', 'Status', 'Ports', 'Names']
    df = pd.DataFrame(data, columns=columns)
    df = df.set_index('ID')
    return df

def get_df_docker_info(all=False):
    if all:
        df_docker_ps = get_df_docker_ps_all()
    else:
        df_docker_ps = get_df_docker_ps()

    df_sim_training = df_docker_ps[df_docker_ps['Names'].apply(lambda x: "deepracer-0-robomaker-" in x)]
    df_sim_training = robomaker_port_extract(df_sim_training, job_type='training')
    training_robomaker_count = df_sim_training.shape[0]
    if training_robomaker_count > 0:
        sim_id_list = ['main']
        for i in range(1, training_robomaker_count):
            sim_id_list.append(f'sim-{i}')
        df_sim_training['sim_id'] = sim_id_list


    df_sim_test = df_docker_ps[df_docker_ps['Names'].apply(lambda x: "deepracer-eval-0-robomaker-" in x)]
    df_sim_test = robomaker_port_extract(df_sim_test, job_type='evaluation')
    df_rl_coach = df_docker_ps[df_docker_ps['Names'].apply(lambda x: "deepracer-0-rl_coach-" in x)]
    df_algo = df_docker_ps[df_docker_ps['Names'].apply(lambda x: "-algo-" in x)]
    df_minio = df_docker_ps[df_docker_ps['Names'].apply(lambda x: "s3-minio-" in x)]
    return {
        'df_sim_training': df_sim_training,
        'df_sim_test': df_sim_test,
        'df_rl_coach': df_rl_coach,
        'df_algo': df_algo,
        'df_minio': df_minio
    }

def is_training():
    df_docker_info = get_df_docker_info()
    if df_docker_info['df_sim_training'].shape[0] > 0:
        return True
    else:
        return False

def is_testing():
    df_docker_info = get_df_docker_info()
    if df_docker_info['df_sim_test'].shape[0] > 0:
        return True
    else:
        return False

def is_training_or_testing():
    df_docker_info = get_df_docker_info()
    if df_docker_info['df_sim_training'].shape[0] > 0:
        return True
    elif df_docker_info['df_sim_test'].shape[0] > 0:
        return True
    else:
        return False

def minio_health_check():
    df_docker_info = get_df_docker_info()
    if df_docker_info['df_minio'].shape[0] < 1:
        return False
    else:
        return True


def training_health_check():
    commit_config_path = CONFIG_PATH
    if os.path.exists(commit_config_path) and (commit_config := read_yaml(commit_config_path)):
        if ('simulation' in commit_config) and ('number_of_sub_simulations' in commit_config['simulation']):
            robomaker_count = commit_config['simulation']['number_of_sub_simulations'] + 1
        else:
            return False
    else:
        return False
    
    df_docker_info = get_df_docker_info()
    if df_docker_info['df_sim_training'].shape[0] != robomaker_count:
        return False
    if df_docker_info['df_rl_coach'].shape[0] < 1:
        return False
    if df_docker_info['df_algo'].shape[0] < 1:
        return False
    if df_docker_info['df_minio'].shape[0] < 1:
        return False

    return True

def test_health_check():
    df_docker_info = get_df_docker_info()
    if df_docker_info['df_sim_test'].shape[0] < 1:
        return False

    return True



def load_job():
    with open(JOB_PATH, 'rb') as f:
        job = pickle.load(f)
    return job




class TrainingJob:
    def __init__(self, config, reward_function, pretrained=False, pretrained_model_name='', debug_reward_function=True, lang='en'):

        config['job_type'] = 'training'
        config['pretrained'] = pretrained
        config['pretrained_model_name'] = pretrained_model_name
        self.config = config_preprocessing(config)
        self.reward_function = reward_function
        self.warnings = []

        #### debug reward function
        if debug_reward_function:
            run_debug_reward_function(self.reward_function)
            
        #### config validation
        config_validator = ConfigValidator(config=config, lang=lang)
        self.warnings += config_validator.validate()
        self.config = config_validator.config
        self.updated_data = config_validator.updated_data

        #### check if is training/testing
        if is_training():
            self.warnings.append(get_warning_trans(target='training_in_progress', lang=lang))
        if is_testing():
            self.warnings.append(get_warning_trans(target='testing_in_progress', lang=lang))

        #### save_job
        self.save_job()

    def warning_confirm(self):
        if len(self.warnings) == 0 :
            return True
        else:
            print("============= Warnings =============", end="", flush=True)
            for warning in self.warnings:
                print(f"\n[{warning['title']}]", flush=True)
                print(f"{warning['message']}", flush=True)
            print("====================================", flush=True)
            if input("\nDo you want to continue? (y/n): ").lower() == 'y':
                return True
            else:
                return False
            
            
    def save_job(self):
        with open(JOB_PATH, 'wb') as f:
            pickle.dump(self, f)

    def start_async(self):
        self.config['commit'] = {
            "init_time": time.time(),
            "check_time": time.time(),
            "status": "initializing",
            "last_checkpoint_idx": -1,
            "best_checkpoint_idx": -1,
        }
        threading.Thread(
            target=self.start,
            kwargs={"config_commit": False},
        ).start()
        return self.config['model_name']

    def start(self, config_commit=True):
        from physicar.deepracer.cloud.utils import read_yaml
        from physicar.deepracer.cloud.utils import Model

        my_turn = MyTurn(wait=True)

        try:
            prev_commit_config = read_yaml(CONFIG_PATH)
            prev_model_name = prev_commit_config['model_name']
            prev_model = Model(prev_model_name)
            prev_model.stop_running(do_my_turn=False, wait_stop=False)
        except:
            pass

        if config_commit:
            self.config['commit'] = {
                "init_time": time.time(),
                "check_time": time.time(),
                "status": "initializing",
                "last_checkpoint_idx": -1,
                "best_checkpoint_idx": -1,
            }
        commit_config(self.config, self.updated_data)
        commit_reward_function(self.reward_function)
        start_training(
            stop_training=True,
            stop_test=True,
            update=True,
            upload_custom_files=True,
            overwrite=True,
        )
        model_folder_path = os.path.join(MODEL_PATH, self.config['model_name'])
        os.makedirs(model_folder_path, exist_ok=True)
        write_yaml(os.path.join(model_folder_path, "config.training.yml"), self.config)
        write_yaml(CONFIG_PATH, self.config)
        my_turn.close()
        return self.config['model_name']


class TestJob:
    def __init__(self, config, lang='en'):
        config['job_type'] = "test"
        self.config = config_preprocessing(config)
        
        self.warnings = []

        #### check if is training/testing
        if is_training():
            self.warnings.append(get_warning_trans(target='training_in_progress', lang=lang))
        if is_testing():
            self.warnings.append(get_warning_trans(target='testing_in_progress', lang=lang))

        #### config validation
        config_validator = ConfigValidator(config=config, lang=lang)
        self.warnings += config_validator.validate()
        self.config = config_validator.config
        self.updated_data = config_validator.updated_data

        #### save_job
        self.save_job()

    def warning_confirm(self):
        if len(self.warnings) == 0 :
            return True
        else:
            print("============= Warnings =============", flush=True)
            for warning in self.warnings:
                print(f"\n[{warning['title']}]", flush=True)
                print(f"{warning['message']}", flush=True)
            print("========================================", flush=True)
            if input("\nDo you want to continue? (y/n): ").lower() == 'y':
                return True
            else:
                return False

    def save_job(self):
        with open(JOB_PATH, 'wb') as f:
            pickle.dump(self, f)

    def start_async(self, do_my_turn=True):
        self.config['commit'] = {
            "init_time": time.time(),
            "check_time": time.time(),
            "status": "initializing",
        }
        threading.Thread(
            target=self.start,
            kwargs={"config_commit": False, "do_my_turn": do_my_turn},
        ).start()
        return self.config['model_name']

    def start(self, config_commit=True, do_my_turn=True):
        from physicar.deepracer.cloud.utils import read_yaml
        from physicar.deepracer.cloud.utils import Model
        if do_my_turn:
            my_turn = MyTurn(wait=True)

        try:
            prev_commit_config = read_yaml(CONFIG_PATH)
            prev_model_name = prev_commit_config['model_name']
            prev_model = Model(prev_model_name)
            prev_model.stop_running(do_my_turn=False, wait_stop=False)
        except:
            pass
        
        if config_commit:
            self.config['commit'] = {
                "init_time": time.time(),
                "check_time": time.time(),
                "status": "initializing",
            }
        commit_config(self.config, self.updated_data)
        start_test(
            stop_training=True,
            stop_test=True,
        )
        model_folder_path = os.path.join(MODEL_PATH, self.config['model_name'])
        # os.makedirs(model_folder_path, exist_ok=True)
        write_yaml(os.path.join(model_folder_path, "config.test.yml"), self.config)
        write_yaml(CONFIG_PATH, self.config)
        if do_my_turn:
            my_turn.close()
        return self.config['model_name']


