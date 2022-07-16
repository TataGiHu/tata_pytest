
import paramiko
import os
import pytest
from common import common

def test_soc_vidmulti():
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
        timeout -s SIGINT 10s ../bin/test_ocv_vidmulti 1 a.264 0 0 > vidmulti_temp.txt;\
        cat vidmulti_temp.txt | tr -s \"\r\n\" \"\n\" > vidmulti_norm.txt;\
        cat vidmulti_norm.txt | grep fps > vidmulti_fps_log.txt;\
        sed -i '1d' vidmulti_fps_log.txt;\
        cat vidmulti_fps_log.txt | awk '{sum+=$6}END{print sum/NR}' > soc_vidmulti.log;\
        rm -f vidmulti_temp.txt vidmulti_norm.txt vidmulti_fps_log.txt"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in stdout.readlines():
        print(line.strip())
    for line in stderr.readlines():
        print(line.strip())
    ssh.close()
    file_path = test_path+"/log/soc_vidmulti.log"
    if not os.path.exists(file_path):
        fps_old = float(10000000)
    else:
        f = open(file_path, "r")
        fps_old = float(f.readline())
    client,sftp = common.sftpConnect(ip, user, pwd, port)
    remote_log_path = remote_path + "/pytest_daily/soc_vidmulti.log"
    local_log_path = test_path + "/log"
    common.sftpDownload(sftp, remote_log_path, local_log_path)
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




    