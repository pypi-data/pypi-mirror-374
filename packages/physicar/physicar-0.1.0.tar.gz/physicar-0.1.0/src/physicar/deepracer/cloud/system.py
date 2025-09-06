
import os
import subprocess
import glob

def convert_test_video_for_web(model_name):
    """
    Convert test video.mp4 files to web-compatible format
    """
    try:
        from physicar.deepracer.cloud.constants import MODEL_PATH
        
        model_path = os.path.join(MODEL_PATH, model_name)
        test_pattern = os.path.join(model_path, "test", "*", "video.mp4")
        video_files = glob.glob(test_pattern)
        
        print(f"Found {len(video_files)} test videos for model: {model_name}")
        
        for video_path in video_files:
            try:
                # Check if ffmpeg is available
                result = subprocess.run(['which', 'ffmpeg'], capture_output=True)
                if result.returncode != 0:
                    print(f"Warning: ffmpeg not found, skipping video conversion for {video_path}")
                    continue
                
                # Create web-compatible version
                web_video_path = video_path.replace('.mp4', '_web.mp4')
                
                # Skip if already converted and newer than original
                if os.path.exists(web_video_path):
                    original_mtime = os.path.getmtime(video_path)
                    web_mtime = os.path.getmtime(web_video_path)
                    if web_mtime >= original_mtime:
                        print(f"Web version already exists and is up to date: {web_video_path}")
                        continue
                    else:
                        print(f"Web version exists but is older, reconverting: {web_video_path}")
                
                print(f"Converting video for web compatibility: {video_path}")
                
                # Get file size for progress indication
                file_size_mb = os.path.getsize(video_path) / 1024 / 1024
                print(f"Original file size: {file_size_mb:.2f} MB")
                
                # FFmpeg command for web-compatible MP4
                cmd = [
                    'ffmpeg', '-y',  # -y to overwrite existing files
                    '-i', video_path,  # Input video
                    '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',  # Silent audio
                    '-c:v', 'libx264',  # Video codec
                    '-c:a', 'aac',      # Audio codec  
                    '-shortest',        # Match shortest stream duration
                    '-movflags', 'faststart',  # Move moov box to beginning
                    '-pix_fmt', 'yuv420p',     # Pixel format for compatibility
                    '-preset', 'fast',         # Encoding speed vs compression
                    '-crf', '23',              # Quality setting (18-28 is good range)
                    '-loglevel', 'warning',    # Reduce ffmpeg output
                    web_video_path
                ]
                
                # Run conversion with timeout
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
                conversion_time = time.time() - start_time
                
                if result.returncode == 0:
                    # Verify the converted file
                    if os.path.exists(web_video_path) and os.path.getsize(web_video_path) > 1000:
                        web_size_mb = os.path.getsize(web_video_path) / 1024 / 1024
                        print(f"Successfully converted: {web_video_path}")
                        print(f"Web file size: {web_size_mb:.2f} MB, conversion time: {conversion_time:.1f}s")
                    else:
                        print(f"Warning: Converted file seems invalid: {web_video_path}")
                        if os.path.exists(web_video_path):
                            os.remove(web_video_path)  # Remove invalid file
                else:
                    print(f"FFmpeg conversion failed for {video_path}")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                print(f"Video conversion timeout (10 min) for {video_path}")
                # Clean up partial file
                if os.path.exists(web_video_path):
                    try:
                        os.remove(web_video_path)
                    except:
                        pass
            except Exception as e:
                print(f"Error converting video {video_path}: {e}")
                
    except Exception as e:
        print(f"Error in convert_test_video_for_web: {e}")

# Import time at module level for the function above
import time

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import shutil
    import time

    print(os.getcwd())
    from physicar.deepracer.cloud.utils import (
        MyTurn,
        read_yaml,
        write_yaml,
        cleanup_training_job,
        cleanup_test_job,
        get_deepracer_checkpoints,
        save_training_metrics_img,
        cleanup_finished_model,
        save_training_logs
    )
    from physicar.deepracer.cloud.run import (
        stop_job,
        # is_training,
        # is_testing,
        training_health_check,
        test_health_check,
        upload_car_zip,
        health_check_tar_gz,
        TestJob
    )
    from physicar.deepracer.cloud.config_validation import (
        check_model_files,
    )

    from physicar.deepracer.cloud.constants import CONFIG_PATH, MODEL_PATH

    trial_num = 1
    while True:
        print(f"[{trial_num}]", end= " ")
        try:
            ########## commit config
            s_time = time.time()
            my_turn = MyTurn(wait=True)
            commit_config_path = CONFIG_PATH
            commit_config_path = os.path.abspath(os.path.expanduser(commit_config_path))

            if os.path.exists(commit_config_path) and (commit_config := read_yaml(commit_config_path)):
                target_model_name = commit_config["model_name"]
                target_path = os.path.join(MODEL_PATH, target_model_name)
                target_config_path = os.path.join(target_path, f"config.{commit_config["job_type"]}.yml")
                if os.path.exists(target_config_path):
                    target_config = read_yaml(target_config_path)
                    if not target_config:
                        target_config = commit_config
                else:
                    target_config = commit_config
                prev_check_time = target_config["commit"]["check_time"]
                target_config["commit"]["check_time"] = time.time()
                duration = target_config["commit"]["check_time"] - target_config["commit"]["init_time"]
                # print(f"duration: {duration:.2f} sec", end=" / ")
                if target_config["commit"]["status"] == "initializing":
                    if target_config["job_type"] == "training":
                        print("initializing training")
                        if training_health_check():
                            target_config["commit"]["status"] = "training"
                        else:
                            if duration > 30:
                                target_config["commit"]["status"] = "error"
                                target_config["commit"]["finish_time"] = target_config["commit"]["check_time"]
                                target_config["commit"]["duration"] = duration
                                save_training_logs(target_model_name)
                                stop_job()
                                os.makedirs(target_path, exist_ok=True)
                    elif target_config["job_type"] == "test":
                        if test_health_check():
                            target_config["commit"]["status"] = "testing"
                        else:
                            if duration > 30:
                                target_config["commit"]["status"] = "error"
                                target_config["commit"]["finish_time"] = prev_check_time
                                target_config["commit"]["duration"] = duration
                                stop_job()
                                os.makedirs(target_path, exist_ok=True)
                    write_yaml(target_config_path, target_config) if os.path.exists(target_path) else None
                    write_yaml(commit_config_path, target_config)

                elif target_config["commit"]["status"] in ["training", "stopping"]:
                    if (target_config["commit"]["status"] == "training") and training_health_check():
                        save_training_metrics_img(target_model_name)
                        deepracer_checkpoints = get_deepracer_checkpoints(target_model_name, retry=5)
                        last_checkpoint_idx = int(deepracer_checkpoints["last_checkpoint"]["name"].split("_")[0])
                        best_checkpoint_idx = int(deepracer_checkpoints["best_checkpoint"]["name"].split("_")[0])
                        if target_config["commit"]["last_checkpoint_idx"] < last_checkpoint_idx:
                            target_config["commit"]["last_checkpoint_idx"] = last_checkpoint_idx
                            last_physical_car_model_path = os.path.join(target_path, "physical-car-model", f"last.tar.gz")
                            best_physical_car_model_path = os.path.join(target_path, "physical-car-model", f"best.tar.gz")
                            for _ in range(3):
                                upload_car_zip()
                                time.sleep(1)
                                if health_check_tar_gz(last_physical_car_model_path):
                                    break
                            if last_checkpoint_idx == best_checkpoint_idx:
                                target_config["commit"]["best_checkpoint_idx"] = best_checkpoint_idx
                                if os.path.exists(last_physical_car_model_path):
                                    for _ in range(3):
                                        shutil.copy(last_physical_car_model_path, best_physical_car_model_path)
                                        time.sleep(1)
                                        if health_check_tar_gz(best_physical_car_model_path):
                                            break
                    else:
                        try:
                            check_model_files(target_config["model_name"])
                            target_config["commit"]["status"] = "ready"
                        except Exception as e:
                            print(f"check_model_files error: {e}")
                            target_config["commit"]["status"] = "error"
                        target_config["commit"]["finish_time"] = prev_check_time
                        target_config["commit"]["duration"] = target_config["commit"]["finish_time"] - target_config["commit"]["init_time"]
                        
                        if target_config["job_type"]=='training':                        
                            save_training_logs(target_model_name)
                            stop_job()
                            cleanup_training_job(target_config["model_name"])
                            save_training_metrics_img(target_model_name)
                            if (target_config["commit"]["status"] == 'ready') and target_config["auto_test_after_training"]:
                                write_yaml(target_config_path, target_config) if os.path.exists(target_path) else None
                                write_yaml(commit_config_path, target_config)
                                target_config_path = os.path.join(target_path, f"config.test.yml")
                                test_job = TestJob(target_config)
                                test_job.start(do_my_turn=False)
                            else:
                                target_model_name = None
                        else:
                            stop_job()
                            cleanup_test_job(target_model_name)
                            target_model_name = None
                    write_yaml(target_config_path, target_config) if os.path.exists(target_path) else None
                    write_yaml(commit_config_path, target_config)

                elif target_config["commit"]["status"] == "testing":
                    if not test_health_check():
                        target_config["commit"]["status"] = "done"
                        target_config["commit"]["finish_time"] = target_config["commit"]["check_time"]
                        target_config["commit"]["duration"] = target_config["commit"]["finish_time"] - target_config["commit"]["init_time"]
                        stop_job()
                        cleanup_test_job(target_model_name)
                        
                        # Convert test video for web compatibility
                        print("Converting test video for web compatibility...")
                        convert_test_video_for_web(target_model_name)
                        
                        target_model_name = None

                    write_yaml(target_config_path, target_config) if os.path.exists(target_path) else None
                    write_yaml(commit_config_path, target_config)
            else:
                target_model_name = None
        except Exception as e:
            import traceback
            print(f"commit config error: {repr(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error args: {e.args}")
            print("Full traceback:")
            traceback.print_exc()
        my_turn.close()
        f_time=time.time()
        print(f"commit config time: {f_time - s_time:.2f} sec", end=" / ")

        try:
            ############# not target_ model manage
            s_time = time.time()
            not_target_model_list = os.listdir(MODEL_PATH)
            if target_model_name in not_target_model_list:
                not_target_model_list.remove(target_model_name)

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(cleanup_finished_model, not_target_model_name) for not_target_model_name in not_target_model_list]
                for fut in as_completed(futures):
                    # print(fut.result())
                    pass
                
            f_time = time.time()
        except:
            pass
        f_time=time.time()
        print(f"not target model manage time: {f_time - s_time:.2f} sec")
        
        ######### sleep
        trial_num += 1
        time.sleep(1)