# 이곳에 import 하지 말것

class DebugRewardFunctionError(Exception):
    def __init__(self, message, error_line=None):
        # message += f"- error_line: {error_line}"
        super().__init__(message)
        self.error_line = error_line

def commit_reward_function(reward_function_script):
    from physicar.deepracer.cloud.utils import write_txt
    from physicar.deepracer.cloud.constants import DRFC_PATH
    import os
    write_txt(
        os.path.join(DRFC_PATH, "custom_files/reward_function.py"),
        reward_function_script
    )

def run_debug_reward_function(reward_function_script, race_type="HB", action_space_type="discrete"):
    import os
    import pkg_resources
    from physicar.deepracer.cloud.run import run_command
    from physicar.deepracer.cloud.utils import write_txt
    from physicar.deepracer.cloud.constants import REWARD_FUNCTION_PATH, PARAMS_LOGS_PATH

    write_txt(REWARD_FUNCTION_PATH, reward_function_script)


    if race_type.lower().strip() in ["tt", "time_trial"]:
        race_type = "TT"
    elif race_type.lower().strip() in ["oa", "object_avoidance"]:
        race_type = "OA"
    elif race_type.lower().strip() in ["hb", "head_to_bot", "hh", "head_to_head"]:
        race_type = "HB"

    if action_space_type.lower().strip() == "discrete":
        action_space_type = "discrete"
    elif action_space_type.lower().strip() == "continuous":
        action_space_type = "continuous"

    cmd = (
        "docker run"
        " --rm"
        " --network none"
        f" -v {os.path.abspath(__file__)}:/debug_reward/debug_reward_function.py"
        f" -v {REWARD_FUNCTION_PATH}:/debug_reward/reward_function.py"
        f" -v {os.path.join(PARAMS_LOGS_PATH, f'{race_type}-{action_space_type}.pkl')}:/debug_reward/params_logs.pkl"
        " -w /debug_reward"
        " --read-only"
        " --cap-drop ALL"
        " --security-opt no-new-privileges"
        " --entrypoint python3"
        " ${DR_SIMAPP_SOURCE}:${DR_SIMAPP_VERSION}"
        " debug_reward_function.py"
    )   

    response = run_command(cmd=cmd, _capture_output=True, _background=False)

    if response.returncode != 0:
        error_str = response.stderr
        error_str = error_str.split('File "/debug_reward/reward_function.py", ')[-1]
        try:
            error_line = int(error_str.split("line ", 1)[-1].split(",")[0].split("\n")[0].strip())
        except:
            error_line = None
        raise DebugRewardFunctionError(error_str, error_line=error_line)

    return response.stdout


# 컨테이너 내에서 실행되는 프로세스
if __name__ == "__main__":
    import pickle
    import time
    try:
        from reward_function import reward_function
    except Exception as e:
        raise e
    with open("params_logs.pkl", "rb") as f:
        params_logs_deepracer_debug = pickle.load(f)
    start_time_deepracer_debug = time.time()
    for params in params_logs_deepracer_debug["params_list"]:
        params['waypoints'] = params_logs_deepracer_debug["waypoints"]

        if not isinstance(reward_function(params), float):
            raise ValueError("Reward function must return a float.")
        if time.time() - start_time_deepracer_debug > 3:
            break

