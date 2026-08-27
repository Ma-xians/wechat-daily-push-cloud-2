# 云端每日推送

这个文件夹是“电脑关机也能推送”的云端版本。

## 原理

GitHub Actions 会在云端定时运行脚本，不再依赖你的电脑开机。推送时间是北京时间周一至周五 08:30。

## 需要准备的账号

需要一个 GitHub 账号。如果没有，去 `https://github.com` 注册一个免费账号。

## 部署步骤

1. 在 GitHub 上创建一个 **Private 私有仓库**，名称可以叫 `wechat-daily-push-cloud`。
2. 把本文件夹里的内容上传到仓库：
   - `.github`
   - `content.json`
   - `push.py`
   - `README-cloud.md`
3. 进入仓库的 `Settings` -> `Secrets and variables` -> `Actions`。
4. 点击 `New repository secret`。
5. Name 填：

   ```text
   WECHAT_WEBHOOK_URL
   ```

6. Value 填你的企业微信机器人 Webhook 地址。
7. 点击 `Add secret` 保存。
8. 进入仓库的 `Actions` 页面，确认 Workflow 已经出现。
9. 可以先手动运行一次 `Daily WeChat Push`，确认能收到消息。
10. 确认成功后，停止本机定时任务，避免重复推送。

## 停止本机定时任务的命令

在 Windows PowerShell 中运行：

```text
Unregister-ScheduledTask -TaskName "CodexDailyWechatPush" -Confirm:$false
```

## 注意

- 仓库一定要设为 Private，不要公开。
- Webhook 地址只放在 GitHub Secret 里，不要写进任何普通文件。
- 如果 Webhook 泄漏，需要在企业微信里删除并重新创建“消息推送”。
