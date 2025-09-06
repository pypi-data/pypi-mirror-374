import yaml
import math
import numpy as np
from PIL import Image, ImageDraw
import os
import json
import time
import shutil
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import dotenv_values, set_key
import pytz
from datetime import datetime
from zoneinfo import ZoneInfo
from physicar.deepracer.cloud.constants import(
    IMAGE_PATH,
    MODEL_PATH,
    DATA_PATH,
    CONFIG_PATH
)

def get_port_url(port:int):
    codespace_name = os.getenv("CODESPACE_NAME")
    if codespace_name:
        return f"https://{codespace_name}-{port}.app.github.dev"
    else:
        return f"http://localhost:{port}"
    
def read_yaml(yaml_file):
    yaml_file = os.path.abspath(os.path.expanduser(yaml_file))
    with open(yaml_file, 'r') as ymlfile:
        config = yaml.safe_load(ymlfile)
    return config

def write_yaml(yaml_file, config):
    yaml_file = os.path.abspath(os.path.expanduser(yaml_file))
    with open(yaml_file, 'w') as ymlfile:
        yaml.dump(config, ymlfile, default_flow_style=False)    

def read_txt(file_path):
    file_path = os.path.abspath(os.path.expanduser(file_path))
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def write_txt(file_path, content):
    file_path = os.path.abspath(os.path.expanduser(file_path))
    with open(file_path, 'w') as file:
        file.write(content)



def to_point(angle, speed):
    start=(366, 300)
    vector_factor=70
    angle_factor=2
    dist = speed * vector_factor
    rad = math.radians(angle * angle_factor + 90)
    dx = dist * math.cos(rad)
    dy = dist * math.sin(rad)
    end_x = start[0] + dx
    end_y = start[1] - dy
    return (end_x, end_y)

def get_default_action_space_img():
    img_path = os.path.join(IMAGE_PATH, "action_space.png")
    img=Image.open(img_path).convert("RGBA")
    return img

def get_discrete_action_space_img(
        action_space,
        arrow_color = (0, 0, 255),
        arrow_width = 4,
        arrow_head_length = 15,
        arrow_head_angle = 30,
    ):
    img = get_default_action_space_img()
    draw = ImageDraw.Draw(img)

    for action in action_space:
        speed = action['speed']
        steering_angle = action['steering_angle']
        
        end = to_point(steering_angle, speed)
        start = (366, 300)

        # 화살표 몸통
        draw.line([start, end], fill=arrow_color, width=arrow_width)

        # 화살표 머리
        if speed != 0:
            dx = start[0] - end[0]
            dy = start[1] - end[1]
            base_angle = math.atan2(dy, dx)  # 끝->시작 벡터 각도
            theta = math.radians(arrow_head_angle)

            x1 = end[0] + arrow_head_length * math.cos(base_angle + theta)
            y1 = end[1] + arrow_head_length * math.sin(base_angle + theta)
            x2 = end[0] + arrow_head_length * math.cos(base_angle - theta)
            y2 = end[1] + arrow_head_length * math.sin(base_angle - theta)

            draw.line([end, (x1, y1)], fill=arrow_color, width=arrow_width)
            draw.line([end, (x2, y2)], fill=arrow_color, width=arrow_width)

    return img


def get_continuous_action_space_img(
        action_space,
        fill_color=(0, 0, 255, 80),
        step_degree=1
    ):
    img = get_default_action_space_img()
    angle_low = action_space["steering_angle"]["low"]
    angle_high = action_space["steering_angle"]["high"]
    speed_low = action_space["speed"]["low"]
    speed_high = action_space["speed"]["high"]
    angle_samples = np.arange(angle_low, angle_high + 0.0001, step_degree)
    outer_points = [to_point(a, speed_high) for a in angle_samples]
    inner_points = [to_point(a, speed_low) for a in reversed(angle_samples)]
    polygon_points = outer_points + inner_points
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    draw_ol = ImageDraw.Draw(overlay, "RGBA")
    draw_ol.polygon(polygon_points, fill=fill_color)
    img.alpha_composite(overlay)

    return img



def save_training_logs(model_name):
    from physicar.deepracer.cloud.run import get_df_docker_info, docker_logs
    df_docker_info = get_df_docker_info(all=True)
    df_sim_training = df_docker_info['df_sim_training']

    log_dir = os.path.join(MODEL_PATH, model_name, "logs")
    os.makedirs(log_dir, exist_ok=True)

    for training_sim_idx in range(df_sim_training.shape[0]):
        sim_row = df_sim_training.iloc[training_sim_idx]
        sim_id = sim_row['sim_id']
        container_name = sim_row['Names']
        log_path = os.path.join(log_dir, f'{sim_id}.log')
        docker_logs(container_name, log_path, contain_stderr=True)

def cleanup_training_job(model_name):
    model_root_path = os.path.join(MODEL_PATH, model_name)
    
    ##### 불필요한 모델 가중치 삭제 
    try:
        model_path = os.path.join(model_root_path, "model")
        model_checkpoints_path = os.path.join(model_path, "deepracer_checkpoints.json")
        with open(model_checkpoints_path, "r") as f:
            model_checkpoints = json.load(f)
        neccessary_model_list = [
            "deepracer_checkpoints.json",
            "model_metadata.json",
            ".coach_checkpoint",
            ".ready",
        ]

        try:
            best_checkpoints_name = model_checkpoints['best_checkpoint']['name']
            neccessary_model_list += [
                f"{best_checkpoints_name}.data-00000-of-00001",
                f"{best_checkpoints_name}.index",
                f"{best_checkpoints_name}.meta",
                f"model_{best_checkpoints_name.split('_')[0]}.pb"
            ]
        except:
            # print("best_checkpoint not found")
            pass

        try:
            last_checkpoints_name = model_checkpoints['last_checkpoint']['name']
            neccessary_model_list += [
                f"{last_checkpoints_name}.data-00000-of-00001",
                f"{last_checkpoints_name}.index",
                f"{last_checkpoints_name}.meta",
                f"model_{last_checkpoints_name.split('_')[0]}.pb"
            ]
        except:
            # print("last_checkpoint not found")
            pass

        try:
            model_file_list = os.listdir(model_path)
            for file_name in model_file_list:
                try:
                    if file_name in neccessary_model_list:
                        continue
                    file_path = os.path.join(model_path, file_name)
                    os.remove(file_path)
                except:
                    # print(f"failed to remove {file_path}")
                    continue
        except:
            # print("model_path not found")
            pass


    except:
        pass

    ##### output 폴더 삭제
    try:
        output_path = os.path.join(model_root_path, "output")
        if os.path.exists(output_path):
            shutil.rmtree(output_path, ignore_errors=True)
    except:
        pass
    
    ##### training-simtrace
    try:
        training_simtrace_path = os.path.join(model_root_path, "training-simtrace")
        training_simtrace_main_path = os.path.join(training_simtrace_path, "main")
        # os.makedirs(training_simtrace_path, exist_ok=True)
        os.makedirs(training_simtrace_main_path, exist_ok=True)
        training_simtrace_listdir = os.listdir(training_simtrace_path)
        for file_name in training_simtrace_listdir:
            if file_name.endswith(".csv"):
                shutil.move(
                    os.path.join(training_simtrace_path, file_name),
                    os.path.join(training_simtrace_main_path, file_name)
                )

        for sim_num in range(0,10):
            sim_idx = "main" if sim_num == 0 else f"sub{sim_num}"
            target_simtrace_path = os.path.join(model_root_path, str(sim_num), "training-simtrace")
            if os.path.exists(target_simtrace_path):
                target_simtrace_listdir = os.listdir(target_simtrace_path)
                os.makedirs(os.path.join(training_simtrace_path, sim_idx), exist_ok=True)
                for file_name in target_simtrace_listdir:
                    if file_name.endswith('.csv'):
                        shutil.move(
                            os.path.join(target_simtrace_path, file_name),
                            os.path.join(training_simtrace_path, sim_idx, file_name)
                        )
                    shutil.rmtree(os.path.join(model_root_path, str(sim_num)), ignore_errors=True)
    except:
        pass


def cleanup_test_job(model_name):
    try:
        target_path = os.path.join(MODEL_PATH, model_name)
        test_raw_names = [name for name in os.listdir(target_path) if name.startswith("evaluation-20")]
        test_raw_names.sort()
        if test_raw_names:
            test_raw_name = test_raw_names[-1]
            test_name = test_raw_name.split("-")[1]
            test_simtrace_path = os.path.join(target_path, test_raw_name, "evaluation-simtrace", "0-iteration.csv")
            test_metrics_path = os.path.join(target_path, "metrics", "evaluation", f"{test_raw_name}.json")
            test_video_path = os.path.join(target_path, "mp4", "camera-pip", "0-video.mp4")
            if os.path.exists(test_simtrace_path) and os.path.exists(test_metrics_path) and os.path.exists(test_video_path):
                os.makedirs(os.path.join(target_path, "test", test_name), exist_ok=True)
                # copy to test folder
                test_simtrace_copy_path = os.path.join(target_path, "test", test_name, f"simtrace.csv")
                test_metrics_copy_path = os.path.join(target_path, "test", test_name, f"metrics.json")
                test_video_copy_path = os.path.join(target_path, "test", test_name, f"video.mp4")
                shutil.copy(test_simtrace_path, test_simtrace_copy_path)
                shutil.copy(test_metrics_path, test_metrics_copy_path)
                
                # 비디오 파일을 웹 호환 형태로 재인코딩하여 복사
                print(f"Processing video for test {test_name}...")
                reencode_video_for_web(test_video_path, test_video_copy_path)
        shutil.rmtree(os.path.join(target_path, "metrics", "evaluation"), ignore_errors=True)
        shutil.rmtree(os.path.join(target_path, "mp4"), ignore_errors=True)
        for test_raw_name in test_raw_names:
            shutil.rmtree(os.path.join(target_path, test_raw_name), ignore_errors=True)
    except:
        pass


def get_deepracer_checkpoints(model_name, retry=10):
    target_path = os.path.join(MODEL_PATH, model_name)
    deepracer_checkpoints_path = os.path.join(target_path, "model", "deepracer_checkpoints.json")
    for _ in range(retry):
        try:
            with open(deepracer_checkpoints_path, "r") as f:
                deepracer_checkpoints = json.load(f)
            return deepracer_checkpoints
        except:
            time.sleep(0.1)
    
    raise Exception(f"Failed to read {deepracer_checkpoints_path}")



def cleanup_finished_model(model_name):
    from physicar.deepracer.cloud.config_validation import check_model_files
    
    target_path = os.path.join(MODEL_PATH, model_name)

    #### training
    save_training_metrics_img(model_name)
    cleanup_training_job(model_name)
    target_training_config_path = os.path.join(target_path, f"config.training.yml")
    if os.path.exists(target_training_config_path) and (target_training_config := read_yaml(target_training_config_path)):
        target_training_status = target_training_config['commit']['status']
        if target_training_status in ["initializing", "training", "stopping"]:
            try:
                check_model_files(model_name)
                target_training_config["commit"]["status"] = "ready"
            except:
                target_training_config["commit"]["status"] = "error"
        write_yaml(target_training_config_path, target_training_config)

    #### test
    cleanup_test_job(model_name)
    target_test_config_path = os.path.join(target_path, f"config.test.yml")
    if os.path.exists(target_test_config_path) and (target_test_config := read_yaml(target_test_config_path)):
        target_test_status = target_test_config['commit']['status']
        if target_test_status in ["initializing", "testing", "stopping"]:
            target_test_config["commit"]["status"] = "done"
        write_yaml(target_test_config_path, target_test_config)

def save_training_metrics_img(model_name, ma_window=10, alpha=0.3):
    import matplotlib
    matplotlib.use("Agg")        # 파일로만 저장하는 비‑GUI 백엔드
    from matplotlib import pyplot as plt
    from matplotlib.ticker import MaxNLocator
    target_path = os.path.join(MODEL_PATH, model_name)
    try:
        target_training_config_path = os.path.join(target_path, f"config.training.yml")
        target_training_config = read_yaml(target_training_config_path)
        num_episodes_between_training = target_training_config['training']['num_episodes_between_training']
    except:
        num_episodes_between_training = 10

    try:
        deepracer_checkpoints = get_deepracer_checkpoints(model_name,retry=3)
    except:
        return
    
    last_checkpoint_idx = int(deepracer_checkpoints["last_checkpoint"]["name"].split("_")[0])
    best_checkpoint_idx = int(deepracer_checkpoints["best_checkpoint"]["name"].split("_")[0])
    training_metrics_path = os.path.join(target_path, "metrics")
    metrics_graphs_path = os.path.join(training_metrics_path, "graphs")
    os.makedirs(metrics_graphs_path, exist_ok=True)
    training_metrics_listdir = sorted([file_name for file_name in os.listdir(training_metrics_path) if file_name.endswith('.json')])

    for metrics_idx, metrics_json_name in enumerate(training_metrics_listdir):
        sim_idx = "main" if metrics_idx == 0 else f"sub{metrics_idx}"
        metrics_img_name = f"{sim_idx}.svg"
        metrics_img_path = os.path.join(metrics_graphs_path, metrics_img_name)
        last_metrics_img_name = f"{sim_idx}_{last_checkpoint_idx}.svg"
        last_metrics_img_path = os.path.join(metrics_graphs_path, last_metrics_img_name)
        if not os.path.exists(last_metrics_img_path):
            with open(os.path.join(training_metrics_path, metrics_json_name), "r") as f:
                metrics_data = json.load(f)
            best_model_metric = metrics_data['best_model_metric']
            metrics = metrics_data['metrics']
            # metrics_version = metrics_data['version']
            # print(metrics_version)

            df_metrics = pd.DataFrame(metrics)
            df_training = df_metrics[df_metrics['phase'] == 'training'].copy()
            df_evaluation = df_metrics[df_metrics['phase'] == 'evaluation'].copy()

            df_training['reward_score_ma'] = df_training['reward_score'].rolling(window=ma_window).mean()
            df_training['completion_percentage_ma'] = df_training['completion_percentage'].rolling(window=ma_window).mean()
            df_evaluation_group = df_evaluation.groupby('episode')

            # x축의 전체 범위 계산
            # x_min = 0
            # x_max = max(5, (max(df_training['episode'].max(), df_evaluation['episode'].max()) / num_episodes_between_training)+0.2)
            iterations = max(df_training['episode'].max(), df_evaluation['episode'].max()) // num_episodes_between_training
            x_min = max(0, last_checkpoint_idx - iterations)
            x_max = x_min + max(5, iterations) + 0.2

            # Subplots 생성 (공유 x축 사용)
            fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True, constrained_layout=True)

            ### reward score plot
            axes[0].scatter(x_min + df_training['episode']/num_episodes_between_training, df_training['reward_score'], alpha=alpha, c='C0')
            axes[0].plot(x_min + df_training['episode']/num_episodes_between_training, df_training['reward_score_ma'], c='C0', label='reward (training)')
            axes[0].scatter(x_min + df_evaluation['episode']/num_episodes_between_training, df_evaluation['reward_score'], alpha=alpha, c='C3')
            axes[0].plot(x_min + df_evaluation_group['episode'].first()/num_episodes_between_training, df_evaluation_group['reward_score'].mean(), c='C3', label='reward (evaluation)')

            # axes[0].set_xlabel('Iteration')
            axes[0].set_ylabel('Reward', fontsize=14, weight='bold')
            # axes[0].set_title('Reward Score')
            axes[0].xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
            axes[0].grid(which='major')

            ### completion percentage plot
            axes[1].scatter(x_min + df_training['episode']/num_episodes_between_training, df_training['completion_percentage'], alpha=alpha, c='C0')
            axes[1].plot(x_min + df_training['episode']/num_episodes_between_training, df_training['completion_percentage_ma'], c='C0', label='progress (training)')
            axes[1].scatter(x_min + df_evaluation['episode']/num_episodes_between_training, df_evaluation['completion_percentage'], alpha=alpha, c='C3')
            axes[1].plot(x_min + df_evaluation_group['episode'].first()/num_episodes_between_training, df_evaluation_group['completion_percentage'].mean(), c='C3', label='progress (evaluation)')

            axes[1].set_ylim(0, 101)  # completion percentage는 0~100 범위로 고정
            axes[1].set_xlabel('Iteration', fontsize=12)
            axes[1].set_ylabel('Progress (completion) %', fontsize=14, weight='bold')
            # axes[1].set_title('Progress (completion) Percentage')
            axes[1].xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
            axes[1].grid(which='major')

            ### best checkpoints
            # ax = axes[0] if best_model_metric == "reward" else axes[1]
            # ax.axvline(x=best_checkpoint_idx+1, linestyle='--', linewidth=1, color='red', alpha=0.7, label='best checkpoint')
            try :
                if best_model_metric == "reward":
                    best_episode = df_evaluation_group['reward_score'].mean().idxmax()
                else:  # completion_percentage
                    best_episode = df_evaluation_group['completion_percentage'].mean().idxmax()

                best_x = x_min + best_episode / num_episodes_between_training
                ax = axes[0] if best_model_metric == "reward" else axes[1]
                ax.axvline(x=best_x, linestyle='--', linewidth=1, color='red', alpha=0.7, label='best checkpoint')
            except:
                pass
            
            # x축 범위 및 공유 설정
            axes[0].set_xlim(x_min, x_max)
            axes[0].legend(loc='upper left', fontsize=12)
            axes[1].legend(loc='upper left', fontsize=12)

            plt.savefig(metrics_img_path)
            plt.savefig(last_metrics_img_path)
            # plt.show()
            plt.close(fig)

        # 불필요한 이미지 제거
        remove_img_list = [file_name for file_name in os.listdir(metrics_graphs_path) if file_name.startswith(f"{sim_idx}_") and (file_name not in [metrics_img_name, last_metrics_img_name])]
        for remove_img in remove_img_list:
            try:
                os.remove(os.path.join(metrics_graphs_path, remove_img))
            except:
                pass

def format_time(ts, time_zone="UTC"):
    return datetime.fromtimestamp(ts, ZoneInfo(time_zone)).strftime("%Y-%m-%d %H:%M:%S %Z")

def get_folder_size(path: str) -> int:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for fname in filenames:
            fp = os.path.join(dirpath, fname)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return f"{total_size / (1024**2):.1f} MBs"

def get_target_info_dict(target_model_name, time_zone="UTC"):
    model_folder_path = MODEL_PATH
    target_info_dict = {
        'ModelName': target_model_name,
        'Status': "",
        'Sensors': "",
        'Layout': "",
        'CreationTime': "",
        'Size': "",
    }
    target_model_path = os.path.join(model_folder_path, target_model_name)
    target_config_training_path = os.path.join(target_model_path, "config.training.yml")
    target_config_test_path = os.path.join(target_model_path, "config.test.yml")

    if os.path.exists(target_config_training_path) and (target_config_training := read_yaml(target_config_training_path)):
        if not target_info_dict['Status']:
            for _ in range(3):
                try:
                    target_info_dict['Status'] = target_config_training['commit']['status']
                    if os.path.exists(target_config_test_path) and (target_config_test := read_yaml(target_config_test_path)):
                        test_status = target_config_test['commit']['status']
                        if test_status in ["testing", "stopping"]:
                            target_info_dict['Status'] = test_status
                    break
                except:
                    time.sleep(0.1)
                    continue
        if not target_info_dict['Sensors']:
            for _ in range(3):
                try:
                    target_info_dict['Sensors'] = "Camera" + (", Lidar" if target_config_training['vehicle']['sensor']['lidar'] else "")
                    break
                except:
                    time.sleep(0.1)
                    continue
        if not target_info_dict['Layout']:
            for _ in range(3):
                try:
                    target_info_dict['Layout'] = target_config_training['vehicle']['layout']
                    break
                except:
                    time.sleep(0.1)
                    continue

        if not target_info_dict['CreationTime']:
            for _ in range(3):
                try:
                    target_info_dict['CreationTime'] = format_time(target_config_training['commit']['init_time'], time_zone=time_zone)
                    break
                except:
                    time.sleep(0.1)
                    continue
        if not target_info_dict['Size']:
            for _ in range(3):
                try:
                    target_info_dict['Size'] = get_folder_size(target_model_path)
                    break
                except:
                    time.sleep(0.1)
                    continue

    return target_info_dict


def get_model_list(time_zone="UTC"):
    model_folder_path = MODEL_PATH
    model_list = os.listdir(model_folder_path)
    valid_model_list = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(get_target_info_dict, target_model_name, time_zone) for target_model_name in model_list]
        for future in as_completed(futures):
            target_info_dict = future.result()
            if target_info_dict:
                valid_model_list.append(target_info_dict)
    valid_model_list = sorted(valid_model_list, key=lambda d: d["CreationTime"], reverse=True)
    return valid_model_list

def get_df_models(time_zone="UTC"):
    valid_model_list = get_model_list(time_zone=time_zone)
    df_models = pd.DataFrame(valid_model_list, columns=['ModelName', 'Status', 'Sensors', 'Layout', 'CreationTime', 'Size'])
    df_models.sort_values(by=['CreationTime'], ascending=False, inplace=True)
    df_models.set_index("ModelName", inplace=True)
    return df_models

class MyTurn:
    def __init__(self, wait=True, duration_time=30, drop_time=60):
        self.duration_time = duration_time
        self.drop_time = drop_time
        self.start_time = time.time()
        self.start_time_str = str(self.start_time)
        self.my_turn_path = os.path.join(DATA_PATH, f".myturn-{self.start_time_str}")
        self.put()
        if wait:
            self.wait()

    def _get_my_turn_arr(self):
        file_list = os.listdir(DATA_PATH)
        my_turn_list = []
        for file in file_list:
            if file.startswith('.myturn-'):
                my_turn_list.append(file.split('-')[-1])
        my_turn_arr = np.array(my_turn_list)
        my_turn_arr.sort()
        return my_turn_arr
    
    def _get_old_valid_turn(self):
        my_turn_arr = self._get_my_turn_arr()
        diff_time_arr = time.time() - my_turn_arr.astype(float)
        old_turn_arr = my_turn_arr[diff_time_arr >  self.drop_time]
        valid_turn_arr = my_turn_arr[diff_time_arr <=  self.drop_time]
        return old_turn_arr, valid_turn_arr

    def put(self):
        with open(self.my_turn_path, 'w') as f:
            pass

    def wait(self):
        while time.time() - self.start_time < self.duration_time:
            old_turn_arr, valid_turn_arr = self._get_old_valid_turn()
            for old_turn in old_turn_arr:
                self.remove(old_turn)
            if valid_turn_arr.shape[0] == 0:
                # print('no my turn!')
                break
            if valid_turn_arr[0] == self.start_time_str:
                # print('my turn!')
                break
            time.sleep(0.1)
        return self

    def remove(self, time_str):
        remove_turn_path = os.path.join(DATA_PATH, f".myturn-{time_str}")
        try:
            os.remove(remove_turn_path)
            # print(f'remove {remove_turn_path}')
        except :
            # print(f'no {remove_turn_path}')
            pass
    
    def close(self):
        self.remove(self.start_time_str)
        # print('close my turn')


def display_link(link_path, display_name=None):
    from IPython.display import HTML, display
    display(HTML(f'<a href="{link_path}">{display_name or link_path}</a>'))


def display_image(filename=None, url=None):
    from IPython.display import Image, SVG, display
    from pathlib import Path

    if filename:
        filename = Path(filename)
        if filename.suffix.lower() == ".svg":
            display(SVG(filename=str(filename)))      # ✔ SVG는 SVG 클래스로
        else:
            display(Image(filename=str(filename)))    # ✔ PNG / JPG / GIF
    elif url:
        display(Image(url=url))
    else:
        return



def get_view_url_info(quality=50):
    from physicar.deepracer.cloud.run import get_df_docker_info
    view_url_info = {"training": {}, "test": {}}
    df_docker_info = get_df_docker_info()

    df_sim_training = df_docker_info['df_sim_training']
    for sim_idx in range(df_sim_training.shape[0]):
        port = int(df_sim_training.iloc[sim_idx]['view_port'])
        port_url = get_port_url(port)
        sim_target = 'main' if sim_idx == 0 else f'sub{sim_idx}'
        view_url_info['training'][sim_target] = {
            # 'port': port,
            'front': f"{port_url}/stream?topic=/racecar/camera/zed/rgb/image_rect_color&quality={quality}",
            'chase': f"{port_url}/stream?topic=/racecar/main_camera/zed/rgb/image_rect_color&quality={quality}",
            'chase_overlay': f"{port_url}/stream?topic=/racecar/deepracer/kvs_stream&quality={quality}",
        }

    df_sim_test = df_docker_info['df_sim_test']
    if df_sim_test.shape[0] > 0:
        port = int(df_sim_test.iloc[0]['view_port'])
        port_url = get_port_url(port)
        view_url_info['test'] = {
            # 'port': port,
            'front': f"{port_url}/stream?topic=/racecar/camera/zed/rgb/image_rect_color&quality={quality}",
            'chase': f"{port_url}/stream?topic=/racecar/main_camera/zed/rgb/image_rect_color&quality={quality}",
            'chase_overlay': f"{port_url}/stream?topic=/racecar/deepracer/kvs_stream&quality={quality}",
        }

    return view_url_info



def get_training_view_url_info(model_name=None, quality=50):
    if model_name is None:
        view_url_info = get_view_url_info(quality=quality)
        return view_url_info['training']
    else:
        commit_config_path = CONFIG_PATH
        commit_config_path = os.path.abspath(os.path.expanduser(commit_config_path))
        if os.path.exists(commit_config_path) and (commit_config := read_yaml(commit_config_path)):
            if commit_config['model_name'] == model_name:
                view_url_info = get_view_url_info(quality=quality)
                return view_url_info['training']
            else:
                return {}
        else:
            return {}


def get_test_view_url_info(model_name=None, quality=50):
    if model_name is None:
        view_url_info = get_view_url_info(quality=quality)
        return view_url_info['test']
    else:
        commit_config_path = CONFIG_PATH
        commit_config_path = os.path.abspath(os.path.expanduser(commit_config_path))
        if os.path.exists(commit_config_path) and (commit_config := read_yaml(commit_config_path)):
            if commit_config['model_name'] == model_name:
                view_url_info = get_view_url_info(quality=quality)
                return view_url_info['test']
            else:
                return {}
        else:
            return {}



def health_check_test_folder(model_name, test_name):
    test_folder_path = os.path.join(MODEL_PATH, model_name, "test", test_name)
    if not os.path.exists(test_folder_path):
        # raise Exception(f"Test folder '{test_folder_path}' not found")
        return False
    if not os.path.exists(os.path.join(test_folder_path, "metrics.json")):
        # raise Exception(f"Metrics file 'metrics.json' not found in test folder '{test_folder_path}'")
        return False
    if not os.path.exists(os.path.join(test_folder_path, "simtrace.csv")):
        # raise Exception(f"Simtrace file 'simtrace.csv' not found in test folder '{test_folder_path}'")
        return False
    if not os.path.exists(os.path.join(test_folder_path, "video.mp4")):
        # raise Exception(f"Video file 'video.mp4' not found in test folder '{test_folder_path}'")
        return False
    return True

def test_format_to_folder(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y%m%d%H%M%S")

def test_format_to_date(date_str):
    return str(datetime.strptime(date_str, "%Y%m%d%H%M%S"))




class Model:
    def __init__(self, model_name):
        self.model_name = model_name

    def get_status(self):
        config_training = self.get_config_training()
        status = config_training['commit']['status']
        if config_test := self.get_config_test() :
            test_status = config_test['commit']['status']
            if test_status in ["testing", "stopping"]:
                status = test_status
        return status
    
    def create_test(self, config, lang='en'):
        from physicar.deepracer.cloud.run import TestJob
        from physicar.deepracer.cloud.config_validation import deep_update
        
        test_job = TestJob(
            config=deep_update(self.get_config_training(), config), 
            lang=lang,
        )
        return test_job

    def clone_model(self, config, reward_function, lang='en'):
        from physicar.deepracer.cloud.run import TrainingJob
        from physicar.deepracer.cloud.config_validation import deep_update
        training_job = TrainingJob(
            config=deep_update(self.get_config_training(), config), 
            reward_function=reward_function,
            pretrained=True,
            pretrained_model_name=self.model_name,
            lang=lang,
        )
        return training_job

    def get_test_list(self):
        test_list_folder = os.path.join(MODEL_PATH, self.model_name, "test")
        test_list = []
        if config_test := self.get_config_test():
            latest_test_status = config_test['commit']['status']
            if latest_test_status in ["initializing", "testing"]:
                test_list.append({"test_name":None, "status":latest_test_status})
        
        if os.path.exists(test_list_folder):
            for test_name in sorted(os.listdir(test_list_folder))[::-1]:
                if health_check_test_folder(self.model_name, test_name):
                    test_list.append({"test_name":test_name, "status":"done"})
        
        return test_list
    
    def show_test_list(self):
        from IPython.display import display
        test_list = self.get_test_list()
        df_test_list = pd.DataFrame(test_list, columns=["test_name", "status"])
        df_test_list["test_time"] = df_test_list.apply(lambda x: test_format_to_date(x["test_name"]) if x["test_name"] else None, axis=1) if df_test_list.shape[0] > 0 else []
        df_test_list = df_test_list[["status", "test_name", "test_time"]]
        display(df_test_list)

    def delete(self):
        if self.get_training_status() in ["initializing", "training"]:
            raise Exception(f"Model '{self.model_name}' is still training")
        if self.get_test_status() in ["initializing", "testing"]:
            raise Exception(f"Model '{self.model_name}' is still testing")
        
        shutil.rmtree(os.path.join(MODEL_PATH, self.model_name), ignore_errors=True)

    def get_training_view_url(self, quality=50):
        return get_training_view_url_info(model_name=self.model_name, quality=quality)
    
    def show_training_view(self, sim="main", camera="chase_overlay", quality=50):
        training_view_url_info = self.get_training_view_url(quality)
        if sim in training_view_url_info:
            training_view_url_sim_info = training_view_url_info[sim]
            if camera in training_view_url_sim_info:
                training_view_url = training_view_url_sim_info[camera]
                print(f"Training view URL: {training_view_url}")
                # display_image(url=training_view_url)
            else:
                raise Exception(f"Camera '{camera}' not found in training view URL info for model '{self.model_name}'")
        else:
            return None

    def get_test_view_url_info(self, quality=50):
        test_view_url_info = get_test_view_url_info(model_name=self.model_name, quality=quality)
        if test_view_url_info:
            return test_view_url_info
        else:
            raise Exception(f"Test view URL not found for model '{self.model_name}'")
            
    def get_model_folder_path(self):
        if not hasattr(self, "model_folder_path"):
            model_folder_path = os.path.join(MODEL_PATH, self.model_name)
            if not os.path.exists(model_folder_path):
                raise Exception(f"Model '{self.model_name}' not found")
            else:
                self.model_folder_path = model_folder_path
        return self.model_folder_path

    def get_reward_function(self):
        reward_function_path = os.path.join(self.get_model_folder_path(), "reward_function.py")
        if not os.path.exists(reward_function_path):
            raise Exception(f"Reward function for model '{self.model_name}' not found")
        else:
            return read_txt(reward_function_path)

    def get_config_training(self):
        config_training_path = os.path.join(self.get_model_folder_path(), "config.training.yml")
        if not os.path.exists(config_training_path):
            raise Exception(f"Training config for model '{self.model_name}' not found")
        else:
            return read_yaml(config_training_path)

    def get_config_test(self):
        config_test_path = os.path.join(self.get_model_folder_path(), "config.test.yml")
        if not os.path.exists(config_test_path):
            return None
        else:
            return read_yaml(config_test_path)

    def get_physical_car_model_link(self):
        physical_car_model_link = {}
        for checkpoint in ["best", "last"]:
            physical_car_model_path = os.path.join(self.get_model_folder_path(), "physical-car-model", f"{checkpoint}.tar.gz")
            if os.path.exists(physical_car_model_path):
                port_url = get_port_url(port=9000)
                physical_car_model_link[checkpoint] = f"{port_url}/bucket/models/{self.model_name}/physical-car-model/{checkpoint}.tar.gz"
        return physical_car_model_link
                

    def show_physical_car_model_link(self, checkpoint="best"):
        physical_car_model_link = self.get_physical_car_model_link()
        if checkpoint in physical_car_model_link:
            display_link(
                link_path = physical_car_model_link[checkpoint],
                display_name = f"{self.model_name}-{checkpoint}.tar.gz",
            )
        else:
            raise Exception(f"Physical car model '{checkpoint}' not found for model '{self.model_name}'")

    def get_metrics_graph_url(self):
        metrics_graph_url = {}
        for sim in ["main", "sub0", "sub1", "sub2", "sub3", "sub4", "sub5", "sub6"]:
            try:
                metrics_graph_path = os.path.join(self.get_model_folder_path(), "metrics", "graphs", f"{sim}.svg")
                if os.path.exists(metrics_graph_path):
                    port_url = get_port_url(port=9000)
                    metrics_graph_url[sim] = f"{port_url}/bucket/models/{self.model_name}/metrics/graphs/{sim}.svg"
            except:
                continue
        return metrics_graph_url


    def get_metrics_graph_path(self, sim="main"):
        metrics_graph_path = os.path.join(self.get_model_folder_path(), "metrics", "graphs", f"{sim}.svg")
        if os.path.exists(metrics_graph_path):
            return metrics_graph_path
        else:
            raise Exception(f"Metrics graph '{sim}' not found for model '{self.model_name}'")

    def show_training_graph(self, sim_idx=0):
        sim = "main" if sim_idx == 0 else f"sim{sim_idx}"
        try:
            display_image(filename=self.get_metrics_graph_path(sim))
        except:
            return None
    def get_training_status(self):
        try:
            return self.get_config_training()["commit"]["status"]
        except:
            return None

    def get_test_status(self):
        try:
            return self.get_config_test()["commit"]["status"]
        except:
            return None

    def get_last_test_status(self):
        try:
            return self.get_config_test()["commit"]["status"]
        except:
            return None

    def is_running(self):
        if self.get_training_status() in ["training", "initializing"]:
            running_info = "training"
        elif self.get_test_status() in ["testing", "initializing"]:
            running_info = "testing"
        else:
            running_info = None
        return running_info

    def stop_running(self, do_my_turn=True, wait_stop=True):
        if do_my_turn:
            my_turn = MyTurn(wait=True)
        _stop = False
        if (commit_config := read_yaml(CONFIG_PATH)) and (commit_config["model_name"] == self.model_name) and (running_info := self.is_running()):
            _stop = True
            if running_info =="training":
                from physicar.deepracer.cloud.utils import save_training_logs
                config_training = self.get_config_training()
                config_training["commit"]["status"] = "stopping"
                config_target_path = os.path.join(MODEL_PATH, self.model_name, "config.training.yml")
                write_yaml(config_target_path, config_training)
                save_training_logs(self.model_name)
            else: # elif running_info == "testing":
                config_test = self.get_config_test()
                config_test["commit"]["status"] = "stopping"
                config_target_path = os.path.join(MODEL_PATH, self.model_name, "config.test.yml")
                write_yaml(config_target_path, config_test)
        if do_my_turn:
            my_turn.close()

        if _stop and wait_stop:
            for _ in range(10):
                time.sleep(0.2)
                if not self.is_running():
                    print(f"Model '{self.model_name}'({running_info}) is stopping...")
                    break
        else:
            raise Exception(f"Model '{self.model_name}' is not running")


def delete_models(model_names):
    my_turn = MyTurn(wait=True)
    from physicar.deepracer.cloud.utils import Model
    def delete_model(model_name):
        try:
            model = Model(model_name)
            model.delete()
        except Exception as e:
            print(f"[Error] deleting model {model_name}: {e}")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(delete_model, model_name) for model_name in model_names]
    my_turn.close()


class Test:
    def __init__(self, model_name, test_name):
        self.model_name = model_name
        self.test_name = test_name
        if not health_check_test_folder(self.model_name, self.test_name):
            raise Exception(f"Model '{self.model_name}' test '{self.test_name}' not found or incomplete")
        
        self.model_folder_path = os.path.join(MODEL_PATH, self.model_name)
        self.test_folder_path = os.path.join(MODEL_PATH, self.model_name, "test", self.test_name)
    
    def get_config_test(self):
        config_test_path = os.path.join(self.model_folder_path, "config.test.yml")
        if not os.path.exists(config_test_path):
            return None
        else:
            return read_yaml(config_test_path)
        
    def get_metrics_path(self):
        metrics_path = os.path.join(self.test_folder_path, "metrics.json")
        if not os.path.exists(metrics_path):
            raise Exception(f"Metrics file '{metrics_path}' not found")
        else:
            return metrics_path
        
    def get_df_metrics(self):
        metrics_path = self.get_metrics_path()
        metrics = json.load(open(metrics_path))
        if metrics['metrics']:
            df_metrics = pd.DataFrame(metrics['metrics'])
            df_metrics['lap_time'] = df_metrics['elapsed_time_in_milliseconds'] / 1000
            df_metrics['total_lap_time'] = df_metrics['lap_time'].cumsum()
            df_metrics = df_metrics[['trial', 'total_lap_time', 'lap_time', 'off_track_count', 'crash_count']]
        else:
            df_metrics = pd.DataFrame(columns=['trial', 'total_lap_time', 'lap_time', 'off_track_count', 'crash_count'])
        return df_metrics

    def get_video_url(self):
        # Check if web-compatible version exists
        web_video_url = get_port_url(9000) + f"/bucket/models/{self.model_name}/test/{self.test_name}/video_web.mp4"
        original_video_url = get_port_url(9000) + f"/bucket/models/{self.model_name}/test/{self.test_name}/video.mp4"
        
        # Check if web version exists on filesystem
        import os
        from physicar.deepracer.cloud.constants import MODEL_PATH
        web_video_path = os.path.join(MODEL_PATH, self.model_name, "test", self.test_name, "video_web.mp4")
        
        if os.path.exists(web_video_path):
            return web_video_url
        else:
            return original_video_url
    
    def show_video_link(self):
        display_link(
            link_path = self.get_video_url(),
            display_name = f"{self.model_name}-{self.test_name}.mp4",
         )

def reencode_video_for_web(input_path, output_path):
    """
    웹 브라우저에서 재생 가능한 형태로 비디오를 재인코딩합니다.
    H.264 코덱과 웹 호환 MP4 컨테이너를 사용합니다.
    """
    import subprocess
    
    try:
        # ffmpeg를 사용하여 웹 호환 형태로 재인코딩
        # -c:v libx264: H.264 비디오 코덱 사용
        # -preset fast: 빠른 인코딩 프리셋
        # -crf 23: 품질 설정 (18-28 범위, 낮을수록 고품질)
        # -c:a aac: AAC 오디오 코덱 사용
        # -movflags +faststart: 웹 스트리밍을 위한 최적화
        # -pix_fmt yuv420p: 웹 브라우저 호환성을 위한 픽셀 포맷
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            '-pix_fmt', 'yuv420p',
            '-y',  # 출력 파일 덮어쓰기
            output_path
        ]
        
        # ffmpeg 실행
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"Video successfully re-encoded: {output_path}")
            return True
        else:
            print(f"ffmpeg error: {result.stderr}")
            # ffmpeg 실패 시 원본 파일을 그대로 복사
            shutil.copy(input_path, output_path)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Video encoding timeout for {input_path}")
        # 타임아웃 시 원본 파일을 그대로 복사
        shutil.copy(input_path, output_path)
        return False
    except FileNotFoundError:
        print("ffmpeg not found, copying original video file")
        # ffmpeg가 없는 경우 원본 파일을 그대로 복사
        shutil.copy(input_path, output_path)
        return False
    except Exception as e:
        print(f"Error during video encoding: {e}")
        # 기타 오류 시 원본 파일을 그대로 복사
        shutil.copy(input_path, output_path)
        return False

import pytz
from physicar.deepracer.cloud.constants import DATA_PATH, DEFAULT_LANG, DEFAULT_TIMEZONE, SUPPORTED_LANGUAGES, SUPPORTED_TIMEZONES, DEFAULT_LANG
def get_language():
    try:
        with open(os.path.join(DATA_PATH, "lang_code"), "r") as f:
            lang_code = f.read().strip().lower()
        if not lang_code in SUPPORTED_LANGUAGES:
            lang_code = DEFAULT_LANG
    except:
        lang_code = DEFAULT_LANG
    return lang_code

def set_language(lang_code):
    lang_code = lang_code.strip().lower()
    if not lang_code in SUPPORTED_LANGUAGES:
        lang_code = DEFAULT_LANG
    with open(os.path.join(DATA_PATH, "lang_code"), "w") as f:
        f.write(lang_code)
    return lang_code

def get_time_zone():
    try:
        with open(os.path.join(DATA_PATH, "time_zone"), "r") as f:
            time_zone = f.read().strip()
        if not time_zone in SUPPORTED_TIMEZONES:
            time_zone = DEFAULT_TIMEZONE
    except:
        time_zone = DEFAULT_TIMEZONE
    return time_zone

def set_time_zone(time_zone):
    time_zone = time_zone.strip()
    if not time_zone in SUPPORTED_TIMEZONES:
        time_zone = DEFAULT_TIMEZONE
    with open(os.path.join(DATA_PATH, "time_zone"), "w") as f:
        f.write(time_zone)
    return time_zone