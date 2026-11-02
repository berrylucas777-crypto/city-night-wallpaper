# 🌃 City Night Wallpaper

只选 Pexels 真实城市摄影，让 Mac 桌面在全球都市间旅行。偏好高机位、霓虹、摩天大楼、密集灯光和蓝调夜色。

Codex Skill 负责搜索、检查照片和轮换城市；命令行负责下载、适配屏幕、应用壁纸和记录历史。无需 Pexels API key，不生成 AI 图片。

## 一行安装 Skill

需要 macOS、Node.js 18+ / npm、Python 3，以及能浏览网页和查看图片的 Codex。

```sh
npx --yes --package=github:berrylucas777-crypto/city-night-wallpaper city-night-wallpaper install-skill
```

打开新的 Codex 对话，输入：

> 用 $city-night-wallpaper 为我换一张东京雨夜壁纸，只用 Pexels 的真实摄影。

也可以把本仓库地址交给 Codex，请它安装根目录中的 Skill。

没有 Node.js？用 Python 安装：

```sh
git clone https://github.com/berrylucas777-crypto/city-night-wallpaper.git
cd city-night-wallpaper
python3 wallpaper.py install-skill
```

安装器尊重 CODEX_HOME，默认安装到 ~/.codex/skills/city-night-wallpaper。已有同名 Skill 时停止，不覆盖。

## npx 命令行

```sh
npx --yes --package=github:berrylucas777-crypto/city-night-wallpaper city-night-wallpaper screen
npx --yes --package=github:berrylucas777-crypto/city-night-wallpaper city-night-wallpaper history
```

包无 npm 依赖、无安装钩子，直接运行随包分发的 Python 命令。包名尚未发布到 npm registry，不能简写成 npx city-night-wallpaper。

命令行不会自行搜索、判断真假摄影或筛选画面。先打开 Pexels 照片页面，查看拍摄信息，确认横向高分辨率且无文字、水印、Logo、明显畸变，再执行：

```sh
python3 wallpaper.py apply \
  'https://www.pexels.com/photo/skyscraper-with-spire-in-city-downtown-7078504/' \
  --city 'New York' --mood 'blue hour' \
  --photographer 'Laura Tancredi' --reviewed
```

apply 命令也可作为 npx 入口参数。--reviewed 表示调用者或 Agent 已目视检查照片，它不执行 AI 检测。

- screen：读取主屏幕真实分辨率。
- history：查看已成功应用的照片、城市和天气/时间氛围。
- apply ... --download-only：只下载和验证尺寸，不改壁纸、不写轮换历史。
- apply ... --allow-repeat：明确允许重复照片，默认拒绝重复。
- --data-dir PATH：放在子命令前，覆盖默认数据目录。

默认数据保存在 ~/Library/Application Support/city-night-wallpaper/，保留图片及 history.json，不上传用户历史。只从 images.pexels.com 下载，有大小和时间限制；下载失败、尺寸不符或系统回读不符都会报错。

屏幕适配采用 Pexels CDN 等比居中裁切，Agent 必须选择比例接近的横图，避免大面积裁边或裁掉主体。macOS 可能提示 Automation 权限，需要允许调用环境控制 System Events。对系统暴露的桌面使用同一张主屏比例图片，不承诺覆盖未激活 Spaces 或独立锁屏画面。首版不支持 Windows/Linux 设置壁纸。

## 每周自动换

安装 Skill 后，在支持定时任务的 Agent 应用中提出：

> 每周一上午 9 点用 $city-night-wallpaper 换壁纸。只用 Pexels 真实摄影；在纽约、多伦多、伦敦、巴黎、东京、香港间轮换，也可加入上海、迪拜、新加坡、芝加哥、首尔。偏好高机位和电影感夜色。参考历史避免重复城市与天气/时间氛围。设置成功后告诉我城市、摄影师和图片页面链接。

让宿主应用创建并确认定时任务。工具本身不安装后台进程；固定照片的 apply 命令不具备自动筛图轮换能力。运行时电脑需可访问网络并允许修改桌面。

## 开发与验证

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 wallpaper.py screen
```

测试覆盖来源 URL、审核前置条件、异步系统确认、重复防护、下载模式无副作用、失败不记录成功和 Skill 安装。照片来源与画面质量仍需真实页面和视觉检查。

## 许可

代码采用 MIT。照片不随包分发，下载图片遵循 [Pexels License](https://www.pexels.com/license/)。本项目与 Pexels 无隶属关系。

## npm 12 调用说明

npm 12 默认关闭 Git 来源安装。如果出现 EALLOWGIT，在这一条命令中显式允许本仓库安装：

```sh
npx --yes --allow-git=all --package=github:berrylucas777-crypto/city-night-wallpaper city-night-wallpaper install-skill
```

该选项仅作用于这次命令，不修改全局 npm 配置。本包没有额外依赖。
