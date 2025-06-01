# AutoClickNinja
PC后台鼠标连点器
🚀 项目简介
AutoClickNinja 是一款后台静默运行的鼠标连点工具，支持：

✅ 精准后台点击 - 通过Windows消息机制实现，不影响正常鼠标使用

✅ 坐标智能获取 - 可视化选择窗口+点击/输入两种坐标获取方式

✅ 多线程控制 - 独立线程运行，F10一键启停

✅ 自定义设置 - 可调点击间隔和位置

📦 快速开始
安装依赖
bash
pip install pywin32 keyboard pygetwindow
运行程序
bash
python src/main.py
打包成EXE
bash
pyinstaller --onefile --windowed --icon=assets/icon.ico src/main.py
🎮 使用指南
选择目标窗口

点击"选择窗口"按钮，从列表中选择需要操作的程序窗口

设置点击坐标

方式1：手动输入X/Y坐标

方式2：点击"获取坐标"后，在目标窗口内点击位置自动获取

配置点击间隔

在输入框中设置点击频率（秒）

开始运行

按 F10 开始/停止后台点击

状态栏实时显示运行状态

⚙️ 技术实现
图表
代码






关键技术：

win32gui.SendMessage - 后台消息模拟点击

pygetwindow - 精准窗口控制

keyboard - 全局热键监听

📜 开源协议
MIT License - 自由修改和分发，需保留原始许可声明

🤝 贡献指南
欢迎提交PR！建议改进方向：

添加宏录制功能

支持更多点击模式（双击/右键等）

跨平台兼容性改进
