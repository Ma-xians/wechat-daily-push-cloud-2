# 上传到 GitHub 的步骤

本文件夹已经是本地 Git 仓库，并已经提交好文件。现在只需要把它上传到你自己的 GitHub 私有仓库。

## 最简单的方式：使用 GitHub Desktop

1. 下载并安装 GitHub Desktop：`https://desktop.github.com`
2. 打开 GitHub Desktop，使用你的 GitHub 账号登录
3. 点击 `File` -> `Add local repository`
4. 选择本文件夹：`E:\CodexProjects\wechat-daily-push-cloud`
5. 点击 `Publish repository`
6. 勾选 `Keep this code private`，然后点击 `Publish repository`
7. 上传完成后，继续下面的“添加密钥”步骤

## 其他方式：命令提示符

先在 GitHub 网页上创建一个空的 Private 仓库，名称可以是 `wechat-daily-push-cloud`。创建时不要勾选 README、.gitignore 或 license。

然后在 PowerShell 中运行：

```text
cd E:\CodexProjects\wechat-daily-push-cloud
git remote add origin https://github.com/你的GitHub用户名/wechat-daily-push-cloud.git
git push -u origin main
```

## 添加密钥

上传完成后：

1. 打开 GitHub 仓库页面
2. 进入 `Settings` -> `Secrets and variables` -> `Actions`
3. 点击 `New repository secret`
4. Name 填：

```text
WECHAT_WEBHOOK_URL
```

5. Value 填你的企业微信机器人 Webhook 地址
6. 点击 `Add secret`

## 测试运行

1. 进入仓库的 `Actions` 页面
2. 左侧选择 `Daily WeChat Push`
3. 点击 `Run workflow`
4. 等待运行结束后，检查企业微信是否收到消息

## 云端稳定后

确认云端能正常推送后，在 Windows PowerShell 中停用本机定时任务，避免重复推送：

```text
Unregister-ScheduledTask -TaskName "CodexDailyWechatPush" -Confirm:$false
```
