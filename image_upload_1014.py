# encoding:utf-8
# !/usr/bin/env python
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, make_response, send_from_directory, abort, url_for
import time
import os
#from strUtil.strUtilexe import Pic_str
import base64
from ctypes import *
import app.darknet as dn
import numpy as np
import cv2
import datetime
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['JSON_AS_ASCII'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'JPG', 'PNG', 'gif', 'GIF'])
static_dir = os.path.join(basedir, app.config['STATIC_FOLDER'])

def get_dt():
    dt = datetime.datetime.today()  # 獲得當地時間
    datetime_dt = dt.strftime("%Y/%m/%d %H:%M:%S")  # 格式化日期
    return datetime_dt
# 提取數據
def get_Meta(detections):
    meta = []
    i = 0
    for info in detections:
        if info[0] in class_names:
            # print("Meta:", detections[i][0], ", Accuracy:", detections[i][1]+"%")
            meta.append(info[0])
        else:
            info[0] = 'NoInfo'
            meta.append(info[0])
        i += 1

    get_class = {
        "dog": "",
        "bicycle": "",
        "person": "",
    }
    meta_b = set(meta)
    all_class = ""
    #global all_classify, x1, y1, x2, y2
    all_classify = ""; all_classify2 = ""
    x1 = ""; y1 = ""; x2 = ""; y2 = ""

    for each_b in meta_b:
        count = 0
        for each_a in meta:
            if each_b == each_a:
                count += 1
        #if each_b in get_class: #使用自定義
        if each_b in meta_b:
            x1 = each_b
            y1 = count
            # print(x1, y1, x2, y2)
            classify_str = each_b + ": " + str(count) + ","
            all_classify += classify_str
        if each_b in get_class:
            x2 = each_b
            y2 = count
            # print(x1, y1, x2, y2)
            classify2_str = each_b + ": " + str(count) + ","
            all_classify2 += classify2_str
        else:
            continue
    # print(all_classify)
    return all_classify, x1, y1, all_classify2, x2, y2

def ModelApp():
    global width, height, thresh, network, class_names, class_colors, darknet_image
    dn.set_gpu(0)
    app_base_dir = '/ap/flask/app'
    cfgpath = "cfg" # yolo config path
    yolocfg = 'yolov4.cfg'  # yolov4 config
    cfgdata = "coco.data" # yolov4 train/test path set
    weights = app_base_dir + "/weights/yolov4.weights_original"
    config_file = app_base_dir + "/" + cfgpath + "/" + yolocfg
    data_file = app_base_dir + "/" + cfgpath + "/" + cfgdata
    batch_size = 1
    thresh = 0.30
    network, class_names, class_colors = dn.load_network(config_file, data_file, weights, batch_size)
    width = dn.network_width(network)
    height = dn.network_height(network)
    darknet_image = dn.make_image(width, height, 3)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def upload_test():
    return render_template('up.html')

# 上傳檔案
@app.route('/up_photo', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']
    print(allowed_file(f.filename))
    user_input = request.form.get("name")
    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)

        #ext = fname.rsplit('.', 1)[1]
        #new_filename = Pic_str().create_uuid() + '.' + ext #變更檔名
        print('存檔路徑: ',os.path.join(file_dir, fname))
        f.save(os.path.join(file_dir, fname))

        for imgname in os.listdir(file_dir):
            #print('File in Folder:',[True if os.path.join(file_dir, imgname) else False])

            if imgname == fname:
                image = cv2.imread(os.path.join(file_dir, imgname))
                # image_rgb = cv2.cvtColor(image, cv2.COLOR_GBR2RGB) #jpg
                image_rgb = image
                image_resized = cv2.resize(image_rgb, (width, height), interpolation=cv2.INTER_LINEAR)
                # 取時間
                datetime_dt = get_dt()

                dn.copy_image_from_bytes(darknet_image, image_resized.tobytes())
                detections = dn.detect_image(network, class_names, darknet_image, thresh=thresh)
                image = dn.draw_boxes(detections, image_resized, class_colors)
                #--插入計算
                all_text, _x1, _y1,  all_text2, _x2, _y2,= get_Meta(detections)
                #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                _y2 = int(_y2) if _y2 != '' else 0
                index = 0
                for text in all_text2.split(","):
                    if int(_y2) >= 12 and 'person' == text.split(':')[0]:
                        cv2.putText(image, text, (11, 24 + (index * 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (250, 250, 250), 1, cv2.LINE_AA)
                        cv2.putText(image, text, (10, 25 + (index * 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                    elif int(_y2) < 12 and int(_y2) >= 8 and 'person' == text.split(':')[0]:
                        cv2.putText(image, text, (11, 24 + (index * 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (250, 250, 250), 1, cv2.LINE_AA)
                        cv2.putText(image, text, (10, 25 + (index * 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 1, cv2.LINE_AA)
                    else:
                        cv2.putText(image, text, (11, 24 + (index * 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (250, 250, 250), 1, cv2.LINE_AA)
                        cv2.putText(image, text, (10, 25 + (index * 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (250, 105, 65), 1, cv2.LINE_AA)
                    index += 1
                cv2.putText(image, datetime_dt, (width - 154, height - 19), cv2.FONT_HERSHEY_DUPLEX, 0.4,
                            (250, 250, 250), 1, cv2.LINE_AA)
                cv2.putText(image, datetime_dt, (width - 155, height - 20), cv2.FONT_HERSHEY_DUPLEX, 0.4,
                            (250, 105, 65), 1, cv2.LINE_AA)

                #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                #-------------

                #cv2.imshow('Inference', image)
                #cv2.waitKey(0) #任意鍵跳下一張
                static_img_dir = os.path.join(static_dir, 'model_image')

                Img_Save_Path = os.path.join(static_img_dir, imgname.split('.')[0]) + '_yolo.jpg'
                cv2.imwrite(Img_Save_Path, image)
                #filename = fname
                #print(os.path.join(file_dir, filename))
                if os.name == "nt":
                    output_img = Img_Save_Path.split('\\')[-2] + '/' + Img_Save_Path.split('\\')[-1] #windows
                else:
                    output_img = Img_Save_Path.split('/')[-2] + '/' + Img_Save_Path.split('/')[-1] #Linux
                all_text = all_text[:-1]
                #img_stream = open(os.path.join(file_dir, imgname.split('.')[0])+'_yolo.jpg', "rb").read() #開檔案回傳
                #img_stream = base64.b64encode(img_stream)
                #response = make_response(img_stream)
                #tmp = render_template('show.html',img_stream=img_stream)
                #response = make_response(tmp)
                #response.headers['Content-Type'] = 'image/png'
                cv2.destroyAllWindows()
                return render_template('show.html', imgfile=output_img,userinput=user_input, val1=time.time(), detection=detections, all_text = all_text)
            else:
                continue
                #return jsonify({"error": 1001, "msg": "上傳失敗"})

    else:
        return jsonify({"error": 1001, "msg": "上傳失敗"})

    return render_template('up.html')

@app.route('/download/<string:filename>', methods=['GET'])
def download(filename):

    downloadpath = os.path.join(os.getcwd(),app.config['UPLOAD_FOLDER'], filename)
    if request.method == "GET":
        if os.path.isfile(downloadpath):
            return send_from_directory(os.path.join(os.getcwd(),app.config['UPLOAD_FOLDER']), filename, as_attachment=True)
        else:
            errorinfo = {"error": 1001, "msg": "無此檔案"}
            return jsonify(errorinfo)        

# show photo
@app.route('/show/<string:filename>', methods=['GET'])
def show_photo(filename):
    try:
        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
        if request.method == 'GET':
            if filename is None:
                errorinfo = {"error": 1001, "msg": "無此檔案"}
                return jsonify(errorinfo)
            else:
                image_data = open(os.path.join(file_dir, str(filename)), "rb").read()
                response = make_response(image_data)
                response.headers['Content-Type'] = 'image/png'
                return response
        else:
            pass
    except FileNotFoundError:
        errorinfo = {"error": 1001, "msg": "無此檔案"}
        return jsonify(errorinfo)

@app.route("/notification", methods=["POST"])
def analysisimg():
    msg= 'hello world'
    res = {"status": '200', "message": msg}
    response = make_response(json.dumps(res))
    response.headers["Content-Type"] = "application/json"
    return response

if __name__ == '__main__':
    ModelApp()
    app.run(host='0.0.0.0',
      port= 5000,
      debug=True
    )
