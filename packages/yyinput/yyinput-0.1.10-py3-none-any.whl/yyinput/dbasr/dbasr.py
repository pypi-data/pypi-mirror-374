

import json
import time
import uuid
import requests
import base64
import os
from ..recorder import RECORDER
import pyperclip
import pyautogui
import keyboard
import pygetwindow as gw
import psutil

class DBASR(object):

    def auc(self):
        # 实例化一个录音类 用于录音 
        recorder = RECORDER()
        try:
            audio_path = recorder.record("temp_recording")
            if audio_path is None:
                print("录音失败，无法继续进行语音识别")
                return
            
            self.__recognizeMode(file_path=audio_path)
            # 录音完成之后 会返回一个文件路径
            # 将录音文件提交给 火山 并返回识别结果
        except Exception as e:
            print(f"语音识别过程中发生错误: {e}")
            return

    # 辅助函数：将本地文件转换为Base64
    def __file_to_base64(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()  # 读取文件内容
            base64_data = base64.b64encode(file_data).decode('utf-8')  # Base64 编码
        return base64_data

    # recognize_task 函数
    def __recognize_task(self, file_url=None, file_path=None):
        recognize_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
        # 填入控制台获取的app id和access token
        appid = "2106894061"
        token = "-xs1nVLpnF_nBvxjv0lEYeFWIRDNy6cH"
        
        headers = {
            "X-Api-App-Key": appid,
            "X-Api-Access-Key": token,
            "X-Api-Resource-Id": "volc.bigasr.auc_turbo", 
            "X-Api-Request-Id": str(uuid.uuid4()),
            "X-Api-Sequence": "-1", 
        }

        # 检查是使用文件URL还是直接上传数据
        audio_data = None
        if file_url:
            audio_data = {"url": file_url}
        elif file_path:
            base64_data = self.__file_to_base64(file_path)  # 转换文件为 Base64
            audio_data = {"data": base64_data}  # 使用Base64编码后的数据

        if not audio_data:
            raise ValueError("必须提供 file_url 或 file_path 其中之一")

        request = {
            "user": {
                "uid": appid
            },
            "audio": audio_data,
            "request": {
                "model_name": "bigmodel",
                # "enable_itn": True,
                # "enable_punc": True,
                # "enable_ddc": True,
                # "enable_speaker_info": False,

            },
        }

        response = requests.post(recognize_url, json=request, headers=headers)
        if 'X-Api-Status-Code' in response.headers:
            # print(f'recognize task response header X-Api-Status-Code: {response.headers["X-Api-Status-Code"]}')
            # print(f'recognize task response header X-Api-Message: {response.headers["X-Api-Message"]}')
            # print(time.asctime() + " recognize task response header X-Tt-Logid: {}".format(response.headers["X-Tt-Logid"]))
            # print(f'recognize task response content is: {response.json()}\n')
            pass 
        else:
            print(f'recognize task failed and the response headers are:: {response.headers}\n')
            exit(1)
        return response

    # recognizeMode 不变
    def __recognizeMode(self, file_url=None, file_path=None):
        if not file_url and not file_path:
            print("错误: 未提供音频文件路径或URL")
            return
            
        if file_path and not os.path.exists(file_path):
            print(f"错误: 音频文件不存在: {file_path}")
            return
            
        start_time = time.time()
        # print(time.asctime() + " START!")
        try:
            recognize_response = self.__recognize_task(file_url=file_url, file_path=file_path)
        except Exception as e:
            print(f"语音识别请求失败: {e}")
            return
        code = recognize_response.headers['X-Api-Status-Code']
        logid = recognize_response.headers['X-Tt-Logid']
        if code == '20000000':  # task finished
            result = recognize_response.json()
            # 获取 并打印  recongnize_response 当中 的  result.text 内容 
            restext = result.get('result', {}).get('text', '')
            print(f"识别结果已经复制到剪贴板:\n\n {restext}\n")
            pyperclip.copy(restext)

            # 判断当前活动窗口是否为终端程序
            if self._is_terminal_focused():
                return
            else:
                # pyautogui.hotkey('ctrl', 'v')
                keyboard.press_and_release('ctrl+v')

            # print(json.dumps(result, indent=4, ensure_ascii=False))
            # print(time.asctime() + " SUCCESS! \n")
            # print(f"程序运行耗时: {time.time() - start_time:.6f} 秒")
        elif code != '20000001' and code != '20000002':  # task failed
            print(time.asctime() + " FAILED! code: {}, logid: {}".format(code, logid))
            print("headers:")
            print(recognize_response.content)

    def _is_terminal_focused(self):
        """判断当前活动窗口是否为终端程序"""
        try:
            # 获取当前活动窗口
            active_window = gw.getActiveWindow()
            if not active_window:
                return False
                
            # 获取窗口标题
            window_title = active_window.title
            
            # 在Windows上，我们需要使用不同的方法获取进程ID
            # pygetwindow的Win32Window对象没有processId属性
            # 我们可以通过窗口标题来判断是否为终端
            
            # 常见终端程序的标题关键词
            terminal_titles = [
                "命令提示符", "command prompt", "cmd", 
                "powershell", "windows powershell",
                "终端", "terminal", "bash", "wsl",
                "git bash", "mintty"
            ]
            
            # 检查窗口标题是否包含终端相关关键词
            window_title_lower = window_title.lower()
            # print(f"当前活动窗口标题: {window_title}")
            if any(title in window_title_lower for title in terminal_titles):
                return True
                
            # 额外检查：如果标题包含路径信息（通常终端会显示当前路径）
            if any(indicator in window_title_lower for indicator in ["c:\\", "d:\\", "~", "$", ">"]):
                return True
                
            return False
            
        except Exception as e:
            print(f"判断过程出错: {e}")
            return False


    def sauc(self):
        pass 
