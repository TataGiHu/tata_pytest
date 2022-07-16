
import paramiko
import os
import pytest
from common import common

def test_soc_jpumulti():
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
        ../bin/test_ocv_jpumulti 1 opencv_nv12_4k_test.jpg 1000 1 0 > jpumulti_temp.txt;\
        cat jpumulti_temp.txt | grep Decoder0 > jpumulti_dec_log.txt;\
        cat jpumulti_dec_log.txt | awk '{a=$3}END{print a}' > soc_jpumulti.log;\
        rm -f jpumulti_temp.txt jpumulti_dec_log.txt"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in stdout.readlines():
        print(line.strip())
    for line in stderr.readlines():
        print(line.strip())
    ssh.close()
    file_path = test_path+"/log/soc_jpumulti.log"
    if not os.path.exists(file_path):
        dec_time_old = float(10000000)
    else:
        f = open(file_path, "r")
        dec_time_old = float(f.readline())
    client,sftp = common.sftpConnect(ip, user, pwd, port)
    remote_log_path = remote_path + "/pytest_daily/soc_jpumulti.log"
    local_log_path = test_path + "/log"
    common.sftpDownload(sftp, remote_log_path, local_log_path)
    common.sftpDisconnect(client)
    f = open(file_path, "r")
    dec_time_new = float(f.readline())
    if (dec_time_old == float(10000000)):
        print("Note:This should be the first time to run this sample.")
        diff = 0
    else:
        print("dec_time_old: {}".format(dec_time_old))
        diff = (dec_time_new-dec_time_old)/dec_time_old*100
    print("dec_time_new: {}".format(dec_time_new))
    print("Frame rate floating degree: {} %".format(diff))
    assert diff > -10




    