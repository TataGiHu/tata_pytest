import paramiko
import os
import pytest
from common import common


def test_soc_videotranscode():
    test_path, params = common.readConfig()
    config = params["SOC"]
    ip = config["SOC_IP"]
    user = config["SOC_USER"]
    pwd = config["SOC_PWD"]
    port = config["SOC_PORT"]
    remote_path = config['SOC_PATH']
    cmd = "cd " + remote_path + "/data;rm -f /dev/shm/*;\
        sudo chmod 777 load.sh load_jpu.sh unload.sh unload_jpu.sh;\
        sudo ./unload.sh;sudo ./unload_jpu.sh;\
        sudo ./load.sh;sudo ./load_jpu.sh;cd ../pytest_daily;\
        ../bin/test_ff_bmcv_transcode opencv_input.mp4 ff_bmcv_transcode.mp4 I420 h264_bm 416 240 25 3000 1 0 0 > videotranscode_temp.txt;\
        cat videotranscode_temp.txt | grep fps > videotranscode_fps_log.txt;\
        cat videotranscode_fps_log.txt | awk '{sum+=$5+1}END{print sum/NR}' > soc_videotranscode.log;\
        md5sum ff_bmcv_transcode*.mp4 > soc_videotranscode_MD5.log;\
        rm -f videotranscode_temp.txt videotranscode_fps_log.txt"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in stdout.readlines():
        print(line.strip())
    for line in stderr.readlines():
        print(line.strip())
    ssh.close()
    file_path = test_path+"/log/soc_videotranscode.log"
    md5_path = test_path+"/log/soc_videotranscode_MD5.log"
    if not os.path.exists(file_path):
        fps_old = float(10000000)
    else:
        f = open(file_path, "r")
        fps_old = float(f.readline())
    if not os.path.exists(md5_path):
        md5_old = None
    else:
        f = open(md5_path, "r")
        md5_old = f.readline()
    client,sftp = common.sftpConnect(ip, user, pwd, port)
    remote_log_path = remote_path + "/pytest_daily/soc_videotranscode.log"
    remote_MD5_path = remote_path + "/pytest_daily/soc_videotranscode_MD5.log"
    local_log_path = test_path + "/log"
    common.sftpDownload(sftp, remote_log_path, local_log_path)
    common.sftpDownload(sftp, remote_MD5_path, local_log_path)
    common.sftpDisconnect(client)
    f = open(file_path, "r")
    fps_new = float(f.readline())
    if (fps_old == float(10000000)):
        print("Note:This should be the first time to run this sample.")
        diff = 0
    else:
        print("fps_old: {}".format(fps_old))
        diff = (fps_new-fps_old)/fps_old*100
    print("fps_new: {}".format(fps_new))
    print("Frame rate floating degree: {} %".format(diff))
    assert diff > -10
    f = open(md5_path, "r")
    md5_new = f.readline()
    if (md5_old == None):
        print("Note:This should be the first time to run this sample.")
    else:
        print("md5_old: {}".format(md5_old))
        print("md5_new: {}".format(md5_new))
        assert md5_new == md5_old