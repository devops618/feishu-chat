import paramiko
import datetime
import pytz

from feishu_utils import *


def change_timezone(time_str, time_zone):
    dt = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
    tz = pytz.timezone(time_zone)
    dt = dt.astimezone(tz)
    return dt


def remote_shell_exec(host, user, passwd, shell_file, shell_args=""):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=22, username=user, password=passwd)
    stdin, stdout, stderr = ssh.exec_command(f"sh {shell_file} {shell_args}")
    exec_stdout = stdout.read().decode('utf8')
    exec_stderr = stderr.read().decode('utf8')
    exit_code = stdout.channel.recv_exit_status()
    ssh.close()
    return exec_stdout, exec_stderr, exit_code


def gitlab_sync(chat_id, env):
    exec_stdout, exec_stderr, exit_code = remote_shell_exec(gitlab_sit, gitlab_user, gitlab_pass, gitlab_shell_file)
    if exit_code == 0:
        if env == "pre" or env == "pro":
            exec_stdout, exec_stderr, exit_code = remote_shell_exec(gitlab_pro, gitlab_user, gitlab_pass,
                                                                    gitlab_shell_file)
            if exit_code == 0:
                content_new = common_card("git同步成功", exec_stdout)
                create_msg_req(chat_id, content_new)
            else:
                content_new = common_card("git同步失败", exec_stderr)
                create_msg_req(chat_id, content_new)
        else:
            content_new = common_card("git同步成功", exec_stdout)
            create_msg_req(chat_id, content_new)
    else:
        content_new = common_card("git同步失败", exec_stderr)
        create_msg_req(chat_id, content_new)
