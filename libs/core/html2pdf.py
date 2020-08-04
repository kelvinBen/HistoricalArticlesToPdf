import pdfkit
import threading
import os
import time
import random

class HtmlToPdfThreads(threading.Thread):

    def __init__(self,task_queue,thread_id,thread_name):
        threading.Thread.__init__(self) 
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.task_queue = task_queue
        self.stop_flag = False

    def __get_task__(self):
        while not self.stop_flag:
            try:
                if self.task_queue.empty():
                    self.stop_flag = True
                    print("=== task kill ===")
                    break

                task = self.task_queue.get(timeout=20)
                html_path = task.get("html")
                print(html_path)
                pdf_path = task.get("pdf")
                print(pdf_path)
            
                self.__html_to_pdf__(html_path,pdf_path)

                
            except Exception as e:
                print(e)
                continue
                
                

    def __html_to_pdf__(self,html_path,pdf_path):
        """设置输出pdf的格式"""
        # options = {
        #     'page-size': 'A4',  # 默认是A4 Letter  etc
        #     'margin-top':'0.05in',   #顶部间隔
        #     'margin-right':'1in',   #右侧间隔
        #     'margin-bottom':'0.05in',   #底部间隔
        #     'margin-left':'1in',   #左侧间隔
        #     'encoding': "UTF-8",  #文本个数
        #     'dpi': '96',
        #     'image-dpi': '640',
        #     'image-quality': '94',
        #     'footer-font-size': '80',  #字体大小
        #     'no-outline': None,
        #     "zoom": '1',  # 网页放大/缩小倍数
        # # 'outline',
        # # 'outline-depth',
        # }            
    
        configuration={

        }
        print(html_path,pdf_path)
        pdfkit.from_url(html_path, pdf_path)
        

    def run(self):
        self.__get_task__()




