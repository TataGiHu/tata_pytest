
import paramiko
import os
import pytest
from common import common

def test_soc_jpubasic():
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
        ../bin/test_ocv_jpubasic opencv_nv12_4k_test.jpg 1 1 0 > jpubasic_temp.txt;\
        cat jpubasic_temp.txt | grep decoder > jpubasic_dec_log.txt;\
        cat jpubasic_temp.txt | grep encoder > jpubasic_enc_log.txt;\
        cat jpubasic_dec_log.txt | awk '{a=$3}END{print a}' > soc_jpubasic_dec.log;\
        cat jpubasic_enc_log.txt | awk '{a=$3}END{print a}' > soc_jpubasic_enc.log;\
        rm -f jpubasic_temp.txt jpubasic_dec_log.txt jpubasic_enc_log.txt"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in stdout.readlines():
        print(line.strip())
    for line in stderr.readlines():
        print(line.strip())
    ssh.close()
    file_path_dec = test_path+"/log/soc_jpubasic_dec.log"
    file_path_enc = test_path+"/log/soc_jpubasic_enc.log"
    if not os.path.exists(file_path_dec):
        dec_time_old = float(10000000)
    else:
        f = open(file_path_dec, "r")
        dec_time_old = float(f.readline())
    if not os.path.exists(file_path_enc):
        enc_time_old = float(10000000)
    else:
        f = open(file_path_enc, "r")
        enc_time_old = float(f.readline())
    client,sftp = common.sftpConnect(ip, user, pwd, port)
    remote_log_path_dec = remote_path + "/pytest_daily/soc_jpubasic_dec.log"
    remote_log_path_enc = remote_path + "/pytest_daily/soc_jpubasic_enc.log"
    local_log_path = test_path + "/log"
    common.sftpDownload(sftp, remote_log_path_dec, local_log_path)
    common.sftpDownload(sftp, remote_log_path_enc, local_log_path)
    common.sftpDisconnect(client)
    # decode verification
    f = open(file_path_dec, "r")
    dec_time_new = float(f.readline())
    if (dec_time_old == float(10000000)):
        print("Note:This should be the first time to run this sample.")
        diff_dec = 0
    else:
        print("dec_time_old: {}".format(dec_time_old))
        diff_dec = (dec_time_new-dec_time_old)/dec_time_old*100
    print("dec_time_new: {}".format(dec_time_new))
    print("Frame rate floating degree: {} %".format(diff_dec))
    assert diff_dec > -10
    # encode verification
    f = open(file_path_enc, "r")
    enc_time_new = float(f.readline())
    if (enc_time_old == float(10000000)):
        print("Note:This should be the first time to run this sample.")
        diff_enc = 0
    else:
        print("enc_time_old: {}".format(enc_time_old))
        diff_enc = (enc_time_new-enc_time_old)/enc_time_old*100
    print("enc_time_new: {}".format(enc_time_new))
    print("Frame rate floating degree: {} %".format(diff_enc))
    assert diff_enc > -10



    