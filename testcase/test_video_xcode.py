import paramiko
import os
import pytest
from common import common


def test_soc_video_xcode():
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
        ../bin/test_ocv_video_xcode opencv_input.mp4 H264enc 30 video_xcode.mp4 1 0 > soc_video_xcode.log;\
        md5sum video_xcode*.mp4 > soc_video_xcode_MD5.log"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, user, pwd)
    _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in stdout.readlines():
        print(line.strip())
    for line in stderr.readlines():
        print(line.strip())
    ssh.close()
    file_path = test_path+"/log/soc_video_xcode.log"
    md5_path = test_path+"/log/soc_video_xcode_MD5.log"
    if not os.path.exists(file_path):
        inf_old = None
    else:
        f = open(file_path, "r")
        inf_old = f.readlines()
    if not os.path.exists(md5_path):
        md5_old = None
    else:
        f = open(md5_path, "r")
        md5_old = f.readline()
    client,sftp = common.sftpConnect(ip, user, pwd, port)
    remote_log_path = remote_path + "/pytest_daily/soc_video_xcode.log"
    remote_MD5_path = remote_path + "/pytest_daily/soc_video_xcode_MD5.log"
    local_log_path = test_path + "/log"
    common.sftpDownload(sftp, remote_log_path, local_log_path)
    common.sftpDownload(sftp, remote_MD5_path, local_log_path)
    common.sftpDisconnect(client)
    f = open(file_path, "r")
    inf_new = f.readlines()
    if (inf_old == None):
        print("Note:This should be the first time to run this sample.")
    else:
        assert inf_new == inf_old
    f = open(md5_path, "r")
    md5_new = f.readline()
    if (md5_old == None):
        print("Note:This should be the first time to run this sample.")
    else:
        print("md5_old: {}".format(md5_old))
        print("md5_new: {}".format(md5_new))
        assert md5_new == md5_old