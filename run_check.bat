@echo off
chcp 65001
echo ==============================================
echo 正在自动安装脚本所需依赖包...
echo ==============================================
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests --upgrade
echo.
echo ==============================================
echo 依赖安装完成，正在运行号码检测脚本...
echo ==============================================
python whatsapp_check.py
echo.
echo ==============================================
echo 脚本运行结束，按任意键退出...
pause > nul
