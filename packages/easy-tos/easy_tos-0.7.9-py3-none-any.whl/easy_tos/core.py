import tos 
import os
from typing import List, Dict
import io
from PIL import Image
import numpy as np
import json 
import subprocess
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import pandas as pd
import shutil
import traceback
from .parallel import multi_thread_tasks, multi_process_tasks
import re
from tos.utils import SizeAdapter
import math
from .utils import write_list_to_txt

def _valid_tos_path(path):
    """
    Check if the given path is a valid Terms of Service (TOS) file path.

    Args:
    path (str): The path to be checked.

    Returns:
    bool: True if the path is a valid TOS file path, False otherwise.
    """
    if not path.startswith("tos://"):
        raise ValueError(f"tos path should start with 'tos://'")
        
    if path.endswith("/"):
        raise ValueError(f"tos path should not end with '/'")
    return True


def _split_tospath(path):
    """
    Split the given TOS file path into its components.

    Args:
    path (str): The TOS file path to be split.

    Returns:
    tuple: A tuple containing the bucket name, prefix, and file name.
    """
    path = path.replace("tos://", "")
    path = path.split("/")
    bucket_name = path[0]
    prefix = "/".join(path[1:-1])
    file_name = path[-1]
    return bucket_name, prefix, file_name


def parse_size(input_string):
    # Regular expression to match the size pattern (e.g., 335.55GB, 4500MB, etc.)
    size_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(MB|GB|TB|KB|B)')

    # Search for the pattern in the input string
    match = size_pattern.search(input_string)
    
    # If a match is found, return the size as a float and the unit
    if match:
        size_value = float(match.group(1))
        size_unit = match.group(2)
        return size_value, size_unit
    else:
        return "Size not found"


def check_tos_dirsize(tos_dir, config):
    tos_du_command_str = f"{config['tosutil_path']} du \
                            -bf=human-readable -d \
                            {tos_dir}"
    result = subprocess.run(tos_du_command_str, shell=True, capture_output=True, text=True)
    
    return parse_size(list(filter(lambda x: x.startswith("STAN"), result.stdout.split('\n')))[0])
    
    
def check_tos_file_size(tos_file, config):
    tos_du_command_str = f"{config['tosutil_path']} du \
                            -bf=human-readable \
                            {tos_file}"
    result = subprocess.run(tos_du_command_str, shell=True, capture_output=True, text=True)
    return parse_size(list(filter(lambda x: x.startswith("STAN"), result.stdout.split('\n')))[0])

   
def check_tos_path_exist(tos_path, config):
    _valid_tos_path(tos_path)
    bucket_name, prefix, file_name = _split_tospath(tos_path)
    object_key = f"{prefix}/{file_name}"
    try:
        # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
        client = tos.TosClientV2(config["ak"], config["sk"], config["endpoint"], config["region"])
        # 获取对象元数据
        result = client.head_object(bucket_name, object_key)
        return True
    except tos.exceptions.TosClientError as e:
        # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
        print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
    except tos.exceptions.TosServerError as e:
        if e.status_code == 404:
            return False
        else:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
    except Exception as e:
        print('fail with unknown error: {}'.format(e))
    # Check if the file exists
    
    
def list_all_files_under_tos_dir(tos_dir, config, save2txt = False, custom_save_path = None, verbose = True):
    """
    List all files under the given prefix in the specified bucket.

    Args:
    tos_dir (str): The directory path in the
    """
    output_list = []
    if not tos_dir.startswith("tos://"):
        raise ValueError(f"tos dir should start with 'tos://'")
    if not tos_dir.endswith("/"):
        raise ValueError(f"tos dir should end with '/'")
    bucket_name, prefix, _ = _split_tospath(tos_dir)
    prefix = f"{prefix}/"
    try:
        client = tos.TosClientV2(config["ak"], config["sk"], config["endpoint"], config["region"])
        # 1. 列举根目录下文件和子目录
        is_truncated = True
        count = 0
        next_continuation_token = ''
        while is_truncated:
            count += 1
            if verbose:
                print(f"{count * 1000} objects have been found!", end="\r")
            out = client.list_objects_type2(bucket_name, prefix=prefix, continuation_token=next_continuation_token)
            # print(out, out.__dict__)
            is_truncated = out.is_truncated
            next_continuation_token = out.next_continuation_token

            # contents中返回了根目录下的对象
            for content in out.contents:
                output_list.append(content.key)
        if verbose:
            print()
            print("All files have been listed!")
        
    except tos.exceptions.TosClientError as e:
        # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
        print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
    except tos.exceptions.TosServerError as e:
        # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
        print('fail with server error, code: {}'.format(e.code))
        # request id 可定位具体问题，强烈建议日志中保存
        print('error with request id: {}'.format(e.request_id))
        print('error with message: {}'.format(e.message))
        print('error with http code: {}'.format(e.status_code))
        print('error with ec: {}'.format(e.ec))
        print('error with request url: {}'.format(e.request_url))
    except Exception as e:
        print('fail with unknown error: {}'.format(e))
        
    out = list(filter(lambda x: not x.endswith("/"), output_list))
    if verbose:
        print(f"Total number of files: {len(out)}")
    if save2txt:
        if custom_save_path is None:
            save_path = "all_files.txt"
        else:
            save_path = custom_save_path
        write_list_to_txt(out, save_path)
    return out


def list_all_subdirs_under_prefix(tos_dir, config, save2txt = False, custom_save_path = None, verbose = True):
    """
    List all subdirectories under the given prefix in the specified bucket.

    Args:
    tos_dir (str): The directory path in the bucket. Example: tos://bucket_name/prefix/
    config (dict): A dictionary containing configuration settings.
    save2txt (bool, optional): Whether to save the subdirectories to a text file. Defaults to False.
    custom_save_path (str, optional): The custom path to save the text file. Defaults to None.

    Returns:
    list: A list of subdirectories under the given prefix.

    Raises:
    ValueError: If the tos_dir is empty or None.
    """
    if not tos_dir.startswith("tos://"):
        raise ValueError(f"tos dir should start with 'tos://'")
    if not tos_dir.endswith("/"):
        raise ValueError(f"tos dir should end with '/'")
    output_list = []
    try:
        client = tos.TosClientV2(config["ak"], config["sk"], config["endpoint"], config["region"])
        bucket_name, prefix, file_name = _split_tospath(tos_dir)
        prefix = f"{prefix}/"
        # 1. 列举根目录下文件和子目录
        is_truncated = True
        count = 0
        next_continuation_token = ''
        while is_truncated:
            count += 1
            if verbose:
                print(f"{count * 1000} objects have been found!", end="\r")
            out = client.list_objects_type2(bucket_name, delimiter="/", prefix=prefix, continuation_token=next_continuation_token)
            # print(out, out.__dict__)
            is_truncated = out.is_truncated
            next_continuation_token = out.next_continuation_token

            for file_prefix in out.common_prefixes:
                output_list.append(file_prefix.prefix)
        if verbose:
            print()
            print("All subdirs have been listed!")
    except tos.exceptions.TosClientError as e:
        # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
        print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
    except tos.exceptions.TosServerError as e:
        # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
        print('fail with server error, code: {}'.format(e.code))
        # request id 可定位具体问题，强烈建议日志中保存
        print('error with request id: {}'.format(e.request_id))
        print('error with message: {}'.format(e.message))
        print('error with http code: {}'.format(e.status_code))
        print('error with ec: {}'.format(e.ec))
        print('error with request url: {}'.format(e.request_url))
    except Exception as e:
        print('fail with unknown error: {}'.format(e))
    if verbose:
        print(f"Total number of subdirs: {len(output_list)}")
    
    if save2txt:
        if custom_save_path is None:
            save_path = "all_dirs.txt"
        else:
            save_path = custom_save_path
        write_list_to_txt(output_list, save_path)
    
    return output_list


def multi_thread_check_tos_file_exists(tos_filepaths, config):
    """
    Check if the Terms of Service (TOS) file exists at the specified filepath.

    Args:
    tos_filepaths (list): A list of TOS filepaths to be checked.
    config (dict): A dictionary containing configuration settings.

    Returns:
    dict: A dictionary containing the filepaths and their existence status.

    Raises:
    ValueError: If the tos_filepath is empty or None.
    """
    results = {}
    print(f"Checking {len(tos_filepaths)} files...")
    success_count = 0
    fail_count = 0 
    with tqdm(total=len(tos_filepaths)) as pbar:
        with ThreadPoolExecutor() as executor:
            future_to_path = {}
            for tos_filepath in tos_filepaths:
                future_to_path[executor.submit(check_tos_path_exist, tos_filepath, config)] = tos_filepath
                
            for future in as_completed(future_to_path):
                tos_filepath = future_to_path[future]
                try:
                    result = future.result()
                except Exception as exc:
                    print(f'{tos_filepath} generated an exception: {exc}')
                else:
                    if result:
                        success_count += 1
                    else:
                        fail_count += 1
                    results[tos_filepath] = result
                pbar.update(1)
                pbar.set_postfix_str(f"Exists: {success_count}, Missing: {fail_count}")
    return results



def read_tos_data_stream_multithread(
    tos_path: str,
    config: dict,
    jobs: int = 32,
    part_size: int = 8 * 1024 * 1024,  # 8MB
    verbose: bool = False,
) -> io.BytesIO:
    """
    Multi-threaded download of a TOS object into memory (BytesIO).

    :param tos_path: e.g. "tos://bucket-name/path/to/file"
    :param config: dict with {ak, sk, endpoint, region}
    :param jobs: max concurrent threads
    :param part_size: chunk size in bytes
    :return: BytesIO containing the file
    """

    client = tos.TosClientV2(
        config["ak"], config["sk"], config["endpoint"], config["region"]
    )
    _valid_tos_path(tos_path)
    bucket_name, prefix, file_name = _split_tospath(tos_path)
    object_key = f"{prefix}/{file_name}" if prefix else file_name

    if verbose:
        print(f"bucket_name: {bucket_name}, object_key: {object_key}")

    # 1. Get object size
    head = client.head_object(bucket_name, object_key)
    total_size = head.content_length
    if total_size is None or total_size == 0:
        raise ValueError(f"Invalid object size: {total_size}")
    if verbose:
        print(f"Object size: {total_size} bytes")

    # 2. Calculate ranges
    num_parts = math.ceil(total_size / part_size)
    ranges = [
        (i * part_size, min((i + 1) * part_size - 1, total_size - 1), i)
        for i in range(num_parts)
    ]
    if verbose:
        print(f"Downloading in {num_parts} parts, {part_size} bytes each")

    # Preallocate buffer
    buffer = bytearray(total_size)

    # 3. Worker
    def download_range(start, end, idx):
        try:
            resp = client.get_object(
                bucket_name, object_key, range_start=int(start), range_end=int(end)
            )
            if hasattr(resp, "read"):  # stream-like
                data = resp.read()
            else:  # iterable fallback
                data = b"".join(chunk for chunk in resp)

            buffer[start : start + len(data)] = data

            if verbose:
                print(f"Part {idx} ({start}-{end}) done")
            return idx
        except Exception as e:
            print(f"Part {idx} failed: {e}")
            return None

    # 4. Run threads
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [executor.submit(download_range, s, e, i) for s, e, i in ranges]
        for fut in as_completed(futures):
            fut.result()

    # 5. Wrap in BytesIO
    file_stream = io.BytesIO(buffer)
    file_stream.seek(0)

    if verbose:
        print(f"Download completed: {len(buffer)} bytes in memory")

    return file_stream



# READ FROM TOS VIA STREAM
def read_tos_data_stream(tos_path: str, config: dict):
    if not tos_path.startswith("tos://"):
        raise ValueError("tos_path should start with 'tos://'")
    
    bucket_name, prefix, filename = _split_tospath(tos_path)
    object_key = f"{prefix}/{filename}" if prefix else filename
    try:
        client = tos.TosClientV2(config["ak"], config["sk"], config["endpoint"], config["region"])
        response = client.get_object(bucket_name, object_key)
        bytes_io = io.BytesIO(response.read())
        return bytes_io
    except Exception as e:
        raise RuntimeError(f"Error reading data stream from TOS: {e}")
    
    
def read_tos_tensor(tos_path: str, config: dict):
    import torch
    tensor_stream = read_tos_data_stream(tos_path, config)
    tensor = torch.load(tensor_stream, map_location='cpu')
    return tensor
    
    
def read_tos_csv(tos_path: str, config: dict):    
    if not tos_path.endswith(".csv"):
        raise ValueError(f"tos_path should end with '.csv'")

    data_stream = read_tos_data_stream(tos_path, config)
    df = pd.read_csv(data_stream)
    return df


def read_tos_txt(tos_path: str, config: dict):
    if not tos_path.endswith(".txt"):
        raise ValueError(f"tos_save_path should end with '.txt'")

    data_stream = read_tos_data_stream(tos_path, config)
    txt = data_stream.read().decode('utf-8')
    return txt


def read_tos_glb_via_trimesh(tos_path: str, config: dict):
    if not tos_path.endswith(".glb"):
        raise ValueError(f"tos_save_path should end with '.glb'")

    data_stream = read_tos_data_stream(tos_path, config)
    mesh = trimesh.load(data_stream, file_type='glb', force='scene')
    return mesh


def read_tos_glb_via_gltf(tos_path: str, config: dict):
    from pygltflib import GLTF2
    if not tos_path.endswith(".glb"):
        raise ValueError(f"tos_save_path should end with '.glb'")
    
    data_stream = read_tos_data_stream(tos_path, config)
    gltf = GLTF2.load_from_bytes(data_stream)
    return gltf


def read_tos_json(tos_path: str, config: dict):
    if not tos_path.endswith(".json"):
        raise ValueError(f"tos_save_path should end with '.json'")
    
    data_stream = read_tos_data_stream(tos_path, config)
    json_data = json.load(data_stream)
    return json_data
        
        
def read_tos_img(tos_path: str, config: dict):
    data_stream = read_tos_data_stream(tos_path, config)
    image = Image.open(data_stream)
    return image

def read_tos_npz(tos_path: str, config: dict):
    data_stream = read_tos_data_stream(tos_path, config)
    npz_data = np.load(data_stream)
    return npz_data
    
    
    
# SAVE TO TOS VIA STREAM
def save_stream_to_tos(stream: io.BytesIO, tos_save_path: str, config: dict, error_msg: str = None):
    stream.seek(0)
    if not tos_save_path.startswith("tos://"):
        raise ValueError(f"tos_save_path should start with 'tos://'")
    bucket_name, prefix, filename = _split_tospath(tos_save_path)
    if prefix == "":
        object_key = filename
    else:
        object_key = f"{prefix}/{filename}"
    try:
        client = tos.TosClientV2(config["ak"], config["sk"], config["endpoint"], config["region"])
        client.put_object(bucket_name, object_key, content=stream)
    except Exception as e:
        if error_msg is None:
            error_msg = f"Error uploading stream: {e}"
        raise RuntimeError(error_msg)
        
        
def save_tensor2tos(feature, tos_save_path: str, config: dict):
    if not tos_save_path.startswith("tos://"):
        raise ValueError(f"tos_save_path should start with 'tos://'")
    import torch
    tensor_buffer = io.BytesIO()
    torch.save(feature, tensor_buffer)
    tensor_buffer.seek(0) # reset the pointer to the start of the stream
    save_stream_to_tos(tensor_buffer, tos_save_path, config, error_msg=f"Error uploading tensor: shape={feature.shape}")


def save_array2tos(array: np.ndarray, tos_save_path: str, config: dict):
    
    if not tos_save_path.startswith("tos://"):
        raise ValueError("tos_save_path should start with 'tos://'")

    array_buffer = io.BytesIO()
    np.save(array_buffer, array)
    array_buffer.seek(0)
    save_stream_to_tos(array_buffer, tos_save_path, config, error_msg=f"Error uploading numpy array: shape={array.shape}")


def save_dict2tos_json(data_dict: dict, tos_save_path: str, config: dict):
    if not tos_save_path.startswith("tos://"):
        raise ValueError(f"tos_save_path should start with 'tos://'")
    
    json_data = json.dumps(data_dict)
    json_buffer = io.BytesIO()
    json_buffer.write(json_data.encode())
    json_buffer.seek(0)
    save_stream_to_tos(json_buffer, tos_save_path, config, error_msg=f"Error uploading json: shape={data_dict}")


def save_pil_img2tos(image: Image.Image, tos_path: str, config: dict, quality: int = 85, optimize: bool = False):
    if not tos_path.startswith("tos://"):
        raise ValueError(f"tos_path should start with 'tos://'")
    
    if not tos_path.endswith(".jpg") and not tos_path.endswith(".png"):
        raise ValueError(f"tos_path should end with '.jpg' or '.png'")
    
    img_buffer = io.BytesIO()
    if tos_path.endswith(".png"):
        image.save(img_buffer, format="PNG")
    elif tos_path.endswith(".jpg"):
        image.save(img_buffer, format="JPEG", quality=quality, optimize=optimize)
    else:
        raise ValueError(f"tos_path should end with '.jpg' or '.png'")
    img_buffer.seek(0)
    save_stream_to_tos(img_buffer, tos_save_path, config, error_msg=f"Error uploading img to tos: {tos_path}")


def save_string(str_data: str, tos_save_path: str, config: dict):
    if not tos_save_path.startswith("tos://"):
        raise ValueError(f"tos_save_path should start with 'tos://'")
    stream = io.StringIO()
    stream.write(str_data)
    stream.seek(0)
    save_stream_to_tos(stream, tos_save_path, config, error_msg=f"Error uploading str: {str_data}")


def _set_tosutil_config(config):
    if not os.path.exists(config['tosutil_path']):
        raise ValueError(f"tosutil_path does not exist: {config['tosutil_path']}")

    if not os.path.exists("~/.tosutilconfig"):
        print("tosutil has not been set!")
        config_set_command_str = f"{config['tosutil_path']} config \
                                    -i {config['ak']} \
                                    -k {config['sk']} \
                                    -e {config['endpoint']} \
                                    -re {config['region']}"
        config_result = subprocess.run(config_set_command_str, shell=True, capture_output=True, text=True)
        print(config_result)
        print("-----------------------------------------------")

def download_dir_via_tosutil(tos_dir: str, local_dir: str, config: dict, flat: bool = False, jobs: int = 96, chunk_jobs: int = 96, verbose: bool = True):
    if flat:
        transfer_command_str = f'{config["tosutil_path"]} cp \
                                -flat -r -u -p {jobs} -j {chunk_jobs} \
                                "{tos_dir}" "{local_dir}"'
    else:
        transfer_command_str = f'{config["tosutil_path"]} cp \
                                -r -u -p {jobs} -j {chunk_jobs} \
                                "{tos_dir}" "{local_dir}"'
    result = subprocess.run(transfer_command_str, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error downloading {tos_dir} to {local_dir}: {result.stderr}")
        if verbose:
            print(result)
    return result.returncode

def download_file_via_tos_sdk(tos_path, local_path, config, verbose=True):
    bucket_name, prefix, tos_filename = _split_tospath(tos_path)
    object_key = f"{prefix}/{tos_filename}"
    try:
        # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
        client = tos.TosClientV2(config['ak'],config['sk'], config['endpoint'], config['region'])
        # 若 file_name 为目录则将对象下载到此目录下, 文件名为对象名
        client.get_object_to_file(bucket_name, object_key, local_path)
    except tos.exceptions.TosClientError as e:
        # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
        print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
    except tos.exceptions.TosServerError as e:
        # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
        print('fail with server error, code: {}'.format(e.code))
        # request id 可定位具体问题，强烈建议日志中保存
        print('error with request id: {}'.format(e.request_id))
        print('error with message: {}'.format(e.message))
        print('error with http code: {}'.format(e.status_code))
        print('error with ec: {}'.format(e.ec))
        print('error with request url: {}'.format(e.request_url))
    except Exception as e:
        print('fail with unknown error: {}'.format(e))

def download_file_via_tosutil(tos_path, local_path, config, jobs=96, chunk_jobs=96, verbose=True):
    if not os.path.exists(config['tosutil_path']):
        raise ValueError(f"tosutil_path does not exist: {config['tosutil_path']}")
    
    transfer_command_str = f'{config["tosutil_path"]} cp \
                            -u -p {jobs} -j {chunk_jobs} \
                            "{tos_path}" "{local_path}"'
    result = subprocess.run(transfer_command_str, shell=True, capture_output=True, text=True)   
    if os.path.exists(local_path):
        return 0
    else:
        print(f"Error downloading {tos_path} to {local_path}: {result.stderr}")
        if verbose:
            print(result)
        return -1


def upload_dir_via_tosutil(local_dir, tos_dir, config, flat=False, jobs=96, chunk_jobs=96, verbose=True):
    
    if not os.path.exists(config['tosutil_path']):
        raise ValueError(f"tosutil_path does not exist: {config['tosutil_path']}")
    if not os.path.exists(local_dir):
        raise ValueError(f"local_path does not exist: {local_dir}")
    if flat:
        transfer_command_str = f'{config["tosutil_path"]} cp \
                                -flat -r -u -p {jobs} -j {chunk_jobs} \
                                "{local_dir}" "{tos_dir}"'
    else:
        transfer_command_str = f'{config["tosutil_path"]} cp \
                                -r -u -p {jobs} -j {chunk_jobs} \
                                "{local_dir}" "{tos_dir}"'
    result = subprocess.run(transfer_command_str, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error uploading {local_dir} to {tos_dir}: {result.stderr}")
        if verbose:
            print(result)
    return result.returncode


def upload_file_via_tosutil(local_path, tos_path, config, jobs=96, chunk_jobs=96, verbose=True):
    if not os.path.exists(config['tosutil_path']):
        raise ValueError(f"tosutil_path does not exist: {config['tosutil_path']}")
    if not os.path.exists(local_path):
        raise ValueError(f"local_path does not exist: {local_path}")
    
    transfer_command_str = f'{config["tosutil_path"]} cp \
                            -u -p {jobs} -j {chunk_jobs} \
                            "{local_path}" "{tos_path}"'
    result = subprocess.run(transfer_command_str, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error uploading {local_path} to {tos_path}: {result.stderr}")
        if verbose:
            print(result)
    return result.returncode

def upload_data2tos_stream(
    data,
    tos_path: str,
    config: dict,
    part_size: int = 5 * 1024 * 1024,
    pil_format: str = "JPEG",  # default format for PIL images
):
    import torch
    import pickle
    """
    Upload any type of data to TOS using multipart upload, from memory buffer.

    Args:
        data: Can be bytes, str, BytesIO, torch tensor/state_dict, PIL Image, or any picklable object.
        tos_path (str): TOS path like "tos://bucket-name/path/to/file"
        config (dict): Dict with keys: ak, sk, endpoint, region
        part_size (int): Each multipart chunk size (default 500MB)
        pil_format (str): Format when saving PIL Image (default "JPEG")
    """
    client = tos.TosClientV2(
        config["ak"], config["sk"], config["endpoint"], config["region"]
    )

    _valid_tos_path(tos_path)
    bucket_name, prefix, file_name = _split_tospath(tos_path)
    object_key = f"{prefix}/{file_name}" if prefix else file_name

    print(f"Uploading to {bucket_name}/{object_key}")

    # --- Convert input into BytesIO ---
    buffer = io.BytesIO()

    if isinstance(data, bytes):
        buffer.write(data)
    elif isinstance(data, str):
        buffer.write(data.encode("utf-8"))
    elif isinstance(data, io.BytesIO):
        buffer = data
    elif isinstance(data, torch.Tensor):
        torch.save(data, buffer)
    elif isinstance(data, torch.nn.Module):
        torch.save(data.state_dict(), buffer)
    elif isinstance(data, dict):
        torch.save(data, buffer)
    elif isinstance(data, Image.Image):
        data.save(buffer, format=pil_format)
    else:
        pickle.dump(data, buffer)
    buffer.seek(0, io.SEEK_END)
    total_size = buffer.tell()
    buffer.seek(0)

    # --- Multipart upload ---
    multi_result = client.create_multipart_upload(bucket_name, object_key)
    upload_id = multi_result.upload_id
    if upload_id is None:
        raise ValueError(f"Upload ID is None")
    parts = []

    part_number = 1
    offset = 0
    while offset < total_size:
        num_to_upload = min(part_size, total_size - offset)
        buffer.seek(offset)
        part = client.upload_part(
            bucket_name, object_key, upload_id, part_number,
            content=SizeAdapter(buffer, num_to_upload, init_offset=offset)
        )
        parts.append(part)
        offset += num_to_upload
        part_number += 1

    client.complete_multipart_upload(bucket_name, object_key, upload_id, parts)
    print(f"Upload completed: {tos_path}")


def upload_data2tos_stream_multithread(
    data,
    tos_path: str,
    config: dict,
    part_size: int = 50 * 1024 * 1024,  # 50 MB default
    pil_format: str = "JPEG",
    max_workers: int = 32,  # number of parallel uploads
):
    import torch
    import pickle
    """
    Upload any type of data to TOS using **parallel multipart upload** from memory.
    """
    client = tos.TosClientV2(
        config["ak"], config["sk"], config["endpoint"], config["region"]
    )

    _valid_tos_path(tos_path)
    bucket_name, prefix, file_name = _split_tospath(tos_path)
    object_key = f"{prefix}/{file_name}" if prefix else file_name

    # --- Convert data to BytesIO ---
    buffer = io.BytesIO()

    if isinstance(data, bytes):
        buffer.write(data)
    elif isinstance(data, str):
        buffer.write(data.encode("utf-8"))
    elif isinstance(data, io.BytesIO):
        buffer = data
    elif isinstance(data, torch.Tensor):
        torch.save(data, buffer)
    elif isinstance(data, torch.nn.Module):
        torch.save(data.state_dict(), buffer)
    elif isinstance(data, dict):
        torch.save(data, buffer)
    elif isinstance(data, Image.Image):
        data.save(buffer, format=pil_format)
    else:
        pickle.dump(data, buffer)

    buffer.seek(0, io.SEEK_END)
    total_size = buffer.tell()
    buffer.seek(0)

    # --- Create multipart upload ---
    multi_result = client.create_multipart_upload(bucket_name, object_key)
    upload_id = multi_result.upload_id
    if upload_id is None:
        raise ValueError("Upload ID is None")

    # --- Prepare parts info ---
    parts_info = []
    offset = 0
    part_number = 1
    while offset < total_size:
        num_to_upload = min(part_size, total_size - offset)
        parts_info.append((part_number, offset, num_to_upload))
        offset += num_to_upload
        part_number += 1

    # --- Upload parts in parallel ---
    uploaded_parts = [None] * len(parts_info)  # preserve order
    def upload_part_task(info):
        part_number, offset, size = info
        buf_copy = io.BytesIO(buffer.getbuffer())  # create independent buffer for thread
        buf_copy.seek(offset)
        return part_number, client.upload_part(
            bucket_name, object_key, upload_id, part_number,
            content=SizeAdapter(buf_copy, size, init_offset=offset)
        )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(upload_part_task, info) for info in parts_info]
        for fut in as_completed(futures):
            part_number, part_result = fut.result()
            uploaded_parts[part_number - 1] = part_result

    # --- Complete multipart upload ---
    client.complete_multipart_upload(bucket_name, object_key, upload_id, uploaded_parts)



def download_files_under_tos_dir(target_tos_dir, uids, local_save_dir, file_type, config, jobs=96, chunk_jobs=96, verbose=True):
    
    target_tos_paths = [f"{target_tos_dir}/{uid}.{file_type}" for uid in uids]
    local_save_paths = [f"{local_save_dir}/{uid}.{file_type}" for uid in uids]
    
    tasks = list(zip(target_tos_paths, local_save_paths))
    def download_task(task):
        tos_path, local_path = task
        download_file_via_tosutil(tos_path, local_path, config, jobs=jobs, chunk_jobs=chunk_jobs, verbose=verbose)
    multi_thread_tasks(tasks, download_task)
    
    
def download_dirs_under_tos_dir(target_tos_dir, uids, local_save_dir, config, jobs=96, chunk_jobs=96, verbose=True):
    target_tos_dirs = [f"{target_tos_dir}/{uid}" for uid in uids]
    local_save_dirs = [f"{local_save_dir}/{uid}" for uid in uids]
    
    tasks = list(zip(target_tos_dirs, local_save_dirs))
    def download_task(task):
        tos_dir, local_dir = task
        download_dir_via_tosutil(tos_dir, local_dir, config, jobs=jobs, chunk_jobs=chunk_jobs, verbose=verbose)
    multi_thread_tasks(tasks, download_task)
    
    
    
    
    
    
    
    
    


    

    
    