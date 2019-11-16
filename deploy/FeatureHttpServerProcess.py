
import os
import sys
import tornado.web
import tornado.ioloop
import tornado.httpserver
import json
import numpy as np
import cv2
import argparse
from urllib.parse import urlparse
import urllib
import ssl
import requests
import urllib3
import socket
import face_model
import logging
from multiprocessloghandler import MultiprocessLogHandler

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
np.set_printoptions(suppress=True, precision=11)

parser = argparse.ArgumentParser(description='face feature server')
# general
parser.add_argument('--image-size', default='112,112', help='')
parser.add_argument('--model', default='../models/model-r100-ii/model,0', help='path to load model.')
parser.add_argument('--ga-model', default='', help='path to load model.')
parser.add_argument('--gpu', default=-1, type=int, help='gpu id')
parser.add_argument('--det', default=0, type=int, help='mtcnn option, 1 means using R+O, 0 means detect from begining')
parser.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
parser.add_argument('--port', default=8888, type=int, help='lister to port')
parser.add_argument('--host', default="0.0.0.0", help='lister to host')
parser.add_argument('--filesvr', default="", help='http addr to filesvr')
parser.add_argument('--process', default=1, type=int, help='process num')
args = parser.parse_args()

host = (args.host, args.port)
model = face_model.FaceModel(args)

formattler = '%(asctime)s %(levelname)s %(name)s %(message)s'
fmt = logging.Formatter(formattler)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(fmt)
file_handler = MultiprocessLogHandler('mylog', when='D')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(fmt)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

#class Resquest(BaseHTTPRequestHandler):
class IndexHandler(tornado.web.RequestHandler):
    def check_origin(self,origin):
        return True
    
    def get(self,*_args,**_kwargs):
        filepath=self.get_query_argument("imgpath")
        if filepath is None:
            data = {'code': 1, 'desc': 'imgpath is required'}
            self.ext_send_response(400, 'application/json', data)
            return None
        logger.debug(filepath)
        if not filepath.startswith('http://') and not filepath.startswith('https://'):
            filepath=args.filesvr+filepath
        try:
            with requests.get(filepath,verify=False,timeout=(1,3)) as res:
                if res.status_code != 200:
                    type = 'application/json'
                    logger.warning(str(res.status_code)+" "+str(res.content)+": "+filepath)
                    self.ext_send_response(res.status_code,res.headers["Content-Type"],res.content)
                    return None
                #img = cv2.imread(res.content)
                imgarray = np.asarray(bytearray(res.content), dtype="uint8")
                if imgarray is None:
                    logger.warning("np.asarray fail: "+filepath)
                    data = {'code': 1, 'desc': 'np.asarray fail'}
                    self.ext_send_response(400, 'application/json', data)
                    return None
                image = cv2.imdecode(imgarray, cv2.IMREAD_COLOR)
                if image is None:
                    logger.warning("cv2.imdecode fail: "+filepath)
                    data = {'code': 1, 'desc': 'cv2.imdecode fail'}
                    self.ext_send_response(400, 'application/json', data)
                    return None
                del imgarray
                del res
                #cv2.imshow('URL2Image', image)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                image = model.get_input(image)
                if image is None:
                    logger.warning("face not found: "+filepath)
                    data = {'code': 1, 'desc': 'face not found'}
                    self.ext_send_response(400, 'application/json', data)
                    return None
                f1 = model.get_feature(image)
                if f1 is None:
                    logger.warning("get_feature is None: "+filepath)
                    data = {'code': 1, 'desc': 'get feature fail'}
                    self.ext_send_response(500, 'application/json', data)
                    return None
                del image
                #print(f1)
                data = {'code': 0, 'data': f1.tolist()}
                self.ext_send_response(200,'application/json', data)
                del f1
        except Exception as e:
            logger.error("UnknowException: " + str(e))
            data = {'code': 503, 'desc': 'system is busied'}
            self.ext_send_response(503, 'application/json', data)
        logger.debug("exit")

    def ext_send_response(self,status,contentType,data):
        try:
            self.set_status(status)
            self.set_header("Content-Type", contentType)
            if(isinstance(data,dict)):
                strdata = json.dumps(data,separators=(',', ':'))
                self.write(strdata.encode())
            else:
                self.write(data)
            return True
        except socket.error as e:
            logger.error("socket.error : Connection broke. Aborting" + str(e))
            return False


if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/featureserver/encode", IndexHandler),
    ], autoreload=False, debug=False, static_path="static",static_url_prefix="/featureserver/static/")
    http_server = tornado.httpserver.HTTPServer(app)
    # -----------修改----------------
    http_server.bind(args.port)
    http_server.start(args.process)
    # ------------------------------
    tornado.ioloop.IOLoop.current().start()


# curl http://localhost:8888/featureserver/encode?imgpath=https://52.83.135.192:8443/fileSvr/get/test2-api0/20191109/4a88555e3492d0e17784b7275139ec88-245458775685726208.jpg --http1.0
# curl http://localhost:8888/featureserver/encode?imgpath=http://api.yimei.ai/fileSvr/get/prd-api0/2019/1003/4eff960d76db3f499d7597985b733ef8-2251799825186516.png  --http1.0
# curl http://localhost:8888/featureserver/encode?imgpath=https://52.83.135.192:8443/fileSvr/get/test2-api0/20191112/1829d7436e3bbc7931614f6faa9f1b38-246416605683122176.png --http1.0
# curl http://localhost:8888/featureserver/encode?imgpath=test2-api0/20191112/396b63662eb00697d7d4d35af836963e-246421647077146624.jpg --http1.0
# curl http://localhost:8899/featureserver/encode?imgpath=test2-api0/20191113/0723d6298fb936de4b9ad8170dfc1986-246942072068636672.png --http1.0