# 飞书自建应用key
# 测试key
# APP_ID = "XXXX"
# APP_SECRET = "XXXX"
# ENCRYPT_KEY = "XXXX"
# VERIFICATION_TOKEN = "XXXX"
# 生产环境key
APP_ID = "XXXX"
APP_SECRET = "XXXX"
ENCRYPT_KEY = "XXXX"
VERIFICATION_TOKEN = "XXXX"

# 发布管理员信息
publish_admins = ["XXXX",
                  "XXXX",
                  "XXXX",
                  "XXXX",
                  "XXXX"]

# dcos url
dcos_perf = "http://XXXX/marathon/v2/apps"
dcos_uat = "http://XXXX/marathon/v2/apps"
dcos_pre = "http://XXXX/marathon/v2/apps"
dcos_pro = "http://XXXX/marathon/v2/apps"

# dcos env
dcos_env = ["perf", "uat", "pre", "pro"]

# image sync host
image_sync_host = "XXXX"
image_sync_host_user = "root"
image_sync_host_pass = "XXXX"
image_sync_shell_file = "/data/devops/publish/image_sync.sh"

# dcos api header
headers = {
    'content-type': 'application/json'
}

# prometheus pushgateway
prometheus_pushgateway = "http://XXXX:9091"

# gitlab 信息
gitlab_sit = "XXXX"
gitlab_pro = "XXXX"
gitlab_user = image_sync_host_user
gitlab_pass = image_sync_host_pass
gitlab_shell_file = "/data/sync-repo/sync_git.sh"
