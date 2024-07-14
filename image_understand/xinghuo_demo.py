import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client


class Image_Understand:
    def __init__(self, appid, api_secret, api_key, imageunderstanding_url):
        self.appid = appid
        self.api_secret = api_secret
        self.api_key = api_key
        self.imageunderstanding_url = imageunderstanding_url
        self.answer = ""  # 初始化answer变量

    def load_image(self, image_path):
        image_data = None
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        self.text = [{"role": "user", "content": str(base64.b64encode(image_data), 'utf-8'), "content_type": "image"}]

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"

        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.imageunderstanding_url + '?' + urlencode(v)
        return url

    def on_error(self, ws, error):
        print("### error:", error)

    def on_close(self, ws, one, two):
        print(" ")

    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def run(self, ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, question=ws.question))
        ws.send(data)

    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            print(content, end="")
            self.answer += content  # 使用实例变量
            if status == 2:
                ws.close()

    def gen_params(self, appid, question):
        data = {
            "header": {
                "app_id": appid
            },
            "parameter": {
                "chat": {
                    "domain": "image",
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2028,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }
        return data

    def main(self, question):
        self.host = urlparse(self.imageunderstanding_url).netloc
        self.path = urlparse(self.imageunderstanding_url).path

        ws_param = self.create_url()
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(ws_param, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_open=self.on_open)
        ws.appid = self.appid
        ws.question = question
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def get_text(self, role, content):
        json_con = {"role": role, "content": content}
        self.text.append(json_con)
        return self.text

    def get_length(self, text):
        length = sum(len(content["content"]) for content in text)
        return length

    def check_length(self, text):
        while self.get_length(text[1:]) > 8000:
            del text[1]
        return text

    def model_of_speaking(self, image_path):
        self.load_image(image_path)
        while True:
            Input = input("\n问:")
            question = self.check_length(self.get_text("user", Input))
            self.answer = ""  # 为每个问题重置answer
            print("答:", end="")
            self.main(question)
            self.get_text("assistant", self.answer)
    
    def model_of_operating(self,images_path,request):
        answers = []
        for image_path in images_path:
            self.load_image(image_path)
            question = self.check_length(self.get_text("user", request))
            self.answer = ""
            self.main(question)
            answers.append(self.answer)
        print(answers)


        
        


if __name__ == "__main__":
    my_appid = "a649217d"  # 填写控制台中获取的 APPID 信息
    my_api_secret = "YjA1YjhkNDY1MWM3NTE4MzgwMjdhMmVk"  # 填写控制台中获取的 APISecret 信息
    my_api_key = "f4c90906cc7b73f16c88f3e15d0013c6"  # 填写控制台中获取的 APIKey 信息
    imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 云端环境的服务地址

    img_understand = Image_Understand(my_appid, my_api_secret, my_api_key, imageunderstanding_url)
    #img_understand.model_of_speaking("image_understand/test/1.jpg")
    img_understand.model_of_operating(["image_understand/test/1.jpg","image_understand/test/2.jpg"],"这是什么")


    



