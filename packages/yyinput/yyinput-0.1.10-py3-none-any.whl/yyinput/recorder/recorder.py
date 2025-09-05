
import pyaudio
import wave
import os 
import platform
import threading
import sys
import select


class RECORDER(object):

    __linux_audio_path = os.path.expanduser("~/.ayyinput/audio/")
    __windows_audio_path = os.path.expanduser("~\\.ayyinput\\audio\\")

    def __init__(self):
        self.__audio_path = self.__linux_audio_path
        if os.name == "nt":
            self.__audio_path = self.__windows_audio_path
        if not os.path.exists(self.__audio_path):
            os.makedirs(self.__audio_path)


    def record(self, filename):
        """
        Record audio from the microphone and save it to a file.
        Recording stops when user presses Enter.

        Args:
            filename (str): The name of the file to save the audio to.
        """
        p = pyaudio.PyAudio()
        
        try:
            # 检查是否有可用的音频输入设备
            if p.get_device_count() == 0:
                print("错误: 未检测到任何音频设备")
                p.terminate()
                return None
                
            # 查找默认输入设备
            default_input_device = None
            try:
                default_input_device = p.get_default_input_device_info()
            except OSError:
                # 如果没有默认输入设备，尝试找到第一个可用的输入设备
                for i in range(p.get_device_count()):
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        default_input_device = device_info
                        break
                        
            if default_input_device is None:
                print("错误: 未找到可用的音频输入设备，请检查麦克风是否正确连接")
                p.terminate()
                return None
                
            print(f"使用音频设备: {default_input_device['name']}")
            
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            input=True,
                            input_device_index=default_input_device['index'],
                            frames_per_buffer=1024)
                            
        except OSError as e:
            print(f"音频设备错误: {e}")
            print("请检查以下事项:")
            print("1. 麦克风是否正确连接")
            print("2. 音频驱动是否正常安装")
            print("3. 系统音频设置中是否启用了麦克风")
            p.terminate()
            return None
        except Exception as e:
            print(f"初始化音频设备时发生未知错误: {e}")
            p.terminate()
            return None

        print("* 开始录音，按 shift+ctrl+space 键停止录音...")
        
        frames = []
        recording = True
        
        try:
            # 创建一个线程来监听全局快捷键
            def listen_for_hotkey():
                nonlocal recording
                try:
                    import keyboard
                    keyboard.wait('ctrl+shift+space')  # 等待用户按Ctrl+Shift+Space
                    recording = False
                except ImportError:
                    print("警告: keyboard 模块未安装，无法使用快捷键停止录音")
                    print("请手动停止程序 (Ctrl+C)")
                except Exception as e:
                    print(f"快捷键监听错误: {e}")
                    recording = False
            
            # 启动监听线程
            listener_thread = threading.Thread(target=listen_for_hotkey)
            listener_thread.daemon = True
            listener_thread.start()

            # 录音循环
            while recording:
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"录音过程中出现错误: {e}")
                    break

            print("* 录音结束")

        except KeyboardInterrupt:
            print("\n* 用户中断录音")
        except Exception as e:
            print(f"录音过程中发生错误: {e}")
        finally:
            # 确保资源被正确释放
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            p.terminate()

        # 保存音频文件
        if frames:
            try:
                wf = wave.open(self.__audio_path + filename + ".wav", 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # print(f"* 音频已保存到: {self.__audio_path + filename + '.wav'}")
                return self.__audio_path + filename + ".wav"
            except Exception as e:
                print(f"保存音频文件时出错: {e}")
                return None
        else:
            print("没有录制到音频数据")
            return None



if __name__=="__main__":
    recorder = RECORDER()
    recorder.record("test")




