# Azure VM + Nginx + Flask + Yolov4 安裝教學

#### 一、簡易說明Azure platform VM 開啟與設定
#### 二、Ubuntu 18.04安裝與更新
#### 三、CV2安裝與設定(darknet Complie使用)
#### 四、python Virtualenv 佈署
#### 五、darknet complie
#### 六、Flask設定與啟動
#### 七、Nginx 安裝與設定


## 在你開始之前

確保您具有以下內容：

- Azure帳號註冊後第一個月免費
- https://signup.azure.com/ #帳號申請


## 一、簡易說明Azure platform VM 開啟與設定
1. 登入 https://portal.azure.com/#home 後，在"首頁"選擇”新增”建立”虛擬機器”
2. 可以選免費試用版並建立主機名稱、機器所在區域、映像檔: Ubuntu、主機大小、驗證類型可以選密碼(或SSH key)及使用者姓名等，連接SSH Port 22。
3. 幾分鐘後會跳出機器啟動完成，選擇'虛擬機器'在對應自己開好的機器。
4. 在自己的虛擬機器中點入'DNS'設定名稱，建立好之後這就是之後網址的連結，IP則對應到自己的 putty進行SSH登入連結。
5. 如果putty連上機器的IP有登入密碼問題，可以在自己的虛擬機器選單中找到'重設密碼'，其次是使用CMD Azure Cli指令進行重置。[AzureVM帳密管理](https://docs.microsoft.com/zh-tw/azure/virtual-machines/extensions/vmaccess)
6. 設定連接 80port開啟[設定80port](https://docs.microsoft.com/zh-tw/azure/virtual-machines/windows/nsg-quickstart-portal)
    - Azure網頁VM設定，選擇剛才的VM，並且設定`網路` ->`輸入連接port規則`->`新增規則`，設定 `80` port是可以被對外。
    - 這邊會看到 22 port SSH已經開啟。
    - 80 port 對應http，443也可以在此先開啟對應 https(https//需要在虛擬主機中放置有效憑證，需要購買)。
7. 設定FTP連線是否正常，如果是使用FileZilla FTP軟體，需要設定傳輸協定為'SFTP Protocol'，傳輸設定選項要選'主動模式'，填入IP、帳號、密碼(同SSH帳、密)。
8. 開啟 putty 並填入SSH連線，將IP設定成虛擬主機IP，port 預設是22，登入後填入帳號、密碼，如果到這邊都沒問題則進行下一步，若有問題則去檢視連線看是否為帳密錯誤並更新。
[Azure Portal平台入口網站](https://portal.azure.com)
[Azure Docs說明文件](https://docs.microsoft.com/zh-tw/azure/virtual-machines/windows/)


##  二、Ubuntu 18.04安裝與更新
1. Putty登入後，開始設定Ubuntu安裝與更新
2. 設定虛擬記憶體，8G才比較不會當機:
    ```shell
    $sudo fallocate -l 8G /swapfile
    $sudo chmod 600 /swapfile
    $ls -lh /swapfile
    $sudo mkswap /swapfile
    $sudo swapon /swapfile
    $sudo cp /etc/fstab /etc/fstab.bak 
    $sudo echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab 
    $free -h    
    ```
3. 更新Ubuntu，需要一段時間
    ```shell
    $sudo apt-get update
    $sudo apt-get upgrade
    ```
4. 設定時區、校正時間
    ```shell
    sudo cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime
    apt-get install -y ntpdate ntp
    sudo ntpdate time.stdtime.gov.tw
    ```
5. 安裝以下軟體
    ```shell
    $sudo apt-get install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev gcc
    $sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libboost-all-dev 
    $sudo apt-get install -y python2.7-dev python3.6-dev python-dev python-numpy python3-numpy python-h5py
    $sudo apt-get install -y libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
    $sudo apt install -y libcanberra-gtk-module libcanberra-gtk3-module 
    $sudo apt install -y libdvdnav4 libdvdread4 gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libdvd-pkg 
    $sudo apt-get -y install ubuntu-restricted-extras 
    $sudo apt-get -y install libavcodec54 libav-tools ffmpeg 
    $sudo apt-get install -y libv4l-dev v4l-utils qv4l2 v4l2ucp 
    $sudo apt-get install -y curl 
    $sudo apt install liblapacke-dev libopenblas-dev libopenblas-base liblapacke-dev
    ```
6. 更新python3
    ```shell
    $sudo apt-get install -y python3-pip
    $sudo apt-get update
    $sudo pip3 install --upgrade pip
    ```
## 三、CV2安裝與設定(darknet Complie使用)
1. Opencv install 這邊使用4.4.0版:
    ```shell
    $cd $folder 
    $curl -L https://github.com/opencv/opencv/archive/4.4.0.zip -o opencv-4.4.0.zip 
    $curl -L https://github.com/opencv/opencv_contrib/archive/4.4.0.zip -o opencv_contrib-4.4.0.zip 
    $unzip opencv-4.4.0.zip 
    $unzip opencv_contrib-4.4.0.zip 
    $cd opencv-4.4.0/ 
    $mkdir release
    $cd release
    ```
2. 建立軟連結:
    ```shell
    sudo ln -s /usr/include/lapacke.h /usr/include/x86_64-linux-gnu/
    vi ~/opencv-4.4.0/cmake/OpenCVFindOpenBLAS.cmake
    ```
    - 找到 “SET(Open_BLAS_INCLUDE_SEARCH_PATHS”並且在右括弧內新增
    /usr/include/x86_64-linux-gnu/
    )
    - 找到 “SET(Open_BLAS_LIB_SEARCH_PATHS”並且在右括弧內新增
    /usr/include/x86_64-linux-gnu/
    )
3. 在~/opencv-4.4.0/relsease/目錄下執行Cmake
    ```shell    
    $cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local/opencv-4.4.0 \
    -D WITH_CUDA=OFF \
    -D WITH_IPP=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-4.4.0/modules \
    -D OPENCV_GENERATE_PKGCONFIG=ON \
    -D OPENCV_PYTHON3_VERSION=ON \
    -D BUILD_opencv_python3=ON \
    -D BUILD_opencv_python2=OFF \
    -D PYTHON3_EXECUTABLE=/usr/bin/python3.6 \
    -D PYTHON3_INCLUDE_DIR=/usr/include/python3.6m \
    -D PYTHON3_INCLUDE_DIR2=/usr/include/x86_64-linux-gnu/python3.6m \
    -D PYTHON3_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.6m.so \
    -D PYTHON_DEFAULT_EXECUTABLE=/usr/bin/python3.6 \
    -D BUILD_opencv_hdf=OFF \
    -D BUILD_EXAMPLES=OFF ..
    ```
4. 在 ~/opencv-4.4.0/release/下面執行:
    - $cat /proc/cpuinfo | grep "processor" | wc -l #可以查看你的系統多少個 CPU
    - $sudo make -j2 # Compile時間>2個小時
    - $sudo make install #安裝編譯好的opencv4
    - $sudo make uninstall #若要解除安裝在同一個目錄中執行此命令
    - 找到opencv4.pc這個檔案，在安裝目錄下的pkgconfig/目錄，將他複製到/usr/lib/pkgconfig/opencv.pc，並命名為opencv.pc
    - $cp /usr/local/opencv-4.4.0/pkgconfig/opencv4.pc /usr/lib/pkgconfig/
    - 如果沒有找到opencv.pc, 可複製下面檔案內容到路徑檔案如: '/usr/lib/pkgconfig/opencv.pc'
    ```shell
    # Package Information for pkg-config
    prefix=/usr/local/opencv-4.4.0
    exec_prefix=${prefix}
    libdir=${exec_prefix}/lib
    includedir=${prefix}/include/opencv4

    Name: OpenCV
    Description: Open Source Computer Vision Library
    Version: 4.4.0
    Libs: -L${exec_prefix}/lib -lopencv_gapi -lopencv_stitching -lopencv_aruco -lopencv_bgsegm -lopencv_bioinspired -lopencv_ccalib -lopencv_dnn_objdetect -lopencv_dnn_superres -lopencv_dpm -lopencv_highgui -lopencv_face -lopencv_freetype -lopencv_fuzzy -lopencv_hfs -lopencv_img_hash -lopencv_intensity_transform -lopencv_line_descriptor -lopencv_quality -lopencv_rapid -lopencv_reg -lopencv_rgbd -lopencv_saliency -lopencv_stereo -lopencv_structured_light -lopencv_phase_unwrapping -lopencv_superres -lopencv_optflow -lopencv_surface_matching -lopencv_tracking -lopencv_datasets -lopencv_text -lopencv_dnn -lopencv_plot -lopencv_videostab -lopencv_videoio -lopencv_xfeatures2d -lopencv_shape -lopencv_ml -lopencv_ximgproc -lopencv_video -lopencv_xobjdetect -lopencv_objdetect -lopencv_calib3d -lopencv_imgcodecs -lopencv_features2d -lopencv_flann -lopencv_xphoto -lopencv_photo -lopencv_imgproc -lopencv_core
    Libs.private: -ldl -lm -lpthread -lrt
    Cflags: -I${includedir}
    ```
5. 編修預設參數:
    - 修改後存檔
        $ vi ~/.bashrc
        ```shell
        export PKG_CONFIG_PATH=/usr/lib/pkgconfig/
        export PATH=${PKG_CONFIG_PATH}:$PATH
        ```
        執行: $ . ~/.bashrc

    - 修改後存檔
        $ sudo vi /etc/profile內容
        #在最下面，加入下面內容
        ```
        export PKG_CONFIG_PATH=/usr/lib/pkgconfig:$PKG_CONFIG_PATH
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/usr/lib 
        ```
        執行: $ . /etc/profile
    - 新增 
        $sudo vi /etc/ld.so.conf.d/opencv.conf 
        新增路徑並存檔:
        ```shell
        /usr/local/opencv-4.4.0/lib
        ```
        $sudo ldconfig
        
    - 新增第三方 Lib路徑連結Python3.6
        $cd /usr/local/lib/python3.6/dist-packages
        $sudo vi opencv.pth
        #新增一行路徑
        ```shell
        /usr/local/opencv-4.4.0/lib/python3.6/dist-packages
        ```
  

## 四、python Virtualenv 佈署

1. 安裝 Virtualenv 及 Flask 等套件
    - 安裝虛擬環境套件
    ```shell
    $ sudo pip3 install virtualenv
    ```
2. 創建虛擬目錄 (例如位於 /ap/flask )
    ```shell
    $ cd /
    $sudo mkdir ap #創建ap/目錄
    $sudo chmod 777 ap #權限修改
    $cd ap #進入ap
    $mkdir flask #創建flask目錄
    $cd flask #進入/ap/flask
    $virtualenv venv #(venv 名稱可自訂)
    $. ./venv/bin/activate #進入虛擬環境
    <venv>$python --version #版本應為>3.6
    ```
3. 在虛擬環境中繼續安裝
    ```shell
    <venv>$pip install flask
    <venv>$pip install opencv-python==4.4.0.42
    <venv>$pip install tensorflow==2.0.1
    <venv>$pip install numpy==1.16.5
    <venv>$pip install keras==2.3.1
    <venv>$pip install pillow==7.2.0
    <venv>$pip install PyQt5==5.15.0
    <venv>$pip install Cython==0.29.21
    <venv>$pip install matplotlib==3.3.1
    ```
    或者是
    ```shell
    $ pip install -r requirements.txt     
    ```
    安裝完成後檢查，確認上述的套件都已經安裝
    ```shell
    $ pip list
    ```
    
## 五、darknet complie
1. darknet是類神經網路模組架構，經訓練後可以用來做圖像辨識。
2. 在 $/ap/flask/目錄下 git darknet，指令如下:
    ```shell
    $git clone https://github.com/AlexeyAB/darknet.git
    ```
3. 下載Weight，可以先在Windows桌面下載好，再用FTP傳到Azure雲端IP，移動到資料夾/ap/flask/darknet/weights #如果weights/目錄不存在，再請 mkdir weights/
    [yolov4_weights下載](https://drive.google.com/open?id=1cewMfusmPjYWbrnuJRuKhPMwRe_b9PaT)
4. 在$/ap/flask/darknet下編輯Makefile，需要修改GPU、CUDNN等的參數, 若GPU=1表示需要有cuda. 若沒有則設為GPU=0 (Azure請預設GPU=0)
    - $vi Makefile
    ```shell
    GPU=0
    CUDNN=0
    CUDNN_HALF=0
    OPENCV=1
    LIBSO=1
    ```
5. 執行compile darknet 
    - $make -j2
    
6. 編譯完成後會有兩個檔案`darknet`可執行檔、以及`libdarknet.so` 給python呼叫用的lib so檔。
7. 完成後，退回上一層目錄至 /ap/flask，並執行:
    - $mv darknet/ app/ #將darknet/目錄名稱改為app/
8. 測試是否成功:
    先進虛擬環境
    $. /ap/flask/venv/bin/activate
    執行python
    \<venv>$python
    ```shell
    >>> import app.darknet as dn
    >>> import cv2
    ```
    如果正確無誤，則不會有任何錯誤訊息

## 六、Flask設定與啟動
1. 連線後將檔案上傳到/ap/flask目錄底下:
2. app/ #裡面為darknet+YOLOV4模型預測
3. static/ #存放yolov4 model結果的目錄
    - model_image/ # 模型預測完成會將圖片放置在此
4. templates/ #網頁目錄
5. uploads/ #user上傳圖片目錄
6. venv/ #先前建置python環境，不能將 Windows的虛擬環境上傳到Linux，會無法執行。
    **Yolov4如果有重新訓練，相關的cfg, obj.data, obj.name等都要上傳。[YOLOV4模型訓練](https://medium.com/@jennyTurtle/%E5%B0%8F%E7%99%BDtrain%E8%87%AA%E5%B7%B1%E7%9A%84yolo-v4-f23f48f85f9e)
7. 在工作目錄建立run.sh，例如 $cd /ap/flask/
    - $vi run.sh
    加入下面內容
    ```shell
    source /ap/flask/venv/bin/activate
    /ap/flask/venv/bin/python /ap/flask/image_upload.py &
    ```
8. 修改檔案權限 
    - $sudo chmod 777 run.sh
9. 開機自動啟動設定
    - $cd /etc
    - $sudo vi rc.local
    加入下面內容
    ```shell
    #!/bin/sh -e
    sh '/ap/flask/run.sh'
    exit 0
    ```
10. 修改權限:
    - $sudo chmod 755 rc.local

## 七、Nginx 安裝與設定
1. 更新:
    - $sudo apt-get update 
2. 安裝設定 Nginx:
    - $sudo apt-get install nginx
    - $cd /etc/nginx/sites-available
    - $sudo vi default
    ```shell
    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        
        # 如果有開啟 port 443，並購買 https憑證可以放在下面指定目錄，並開啟設定
        #listen 443 ssl default_server;
        #listen [::]:443 ssl default_server;
        
        # 憑證與金鑰的路徑
        #ssl_certificate /etc/nginx/ssl/nginx.crt;
        #ssl_certificate_key /etc/nginx/ssl/nginx.key;
        #
        root /var/www/html;

        server_name countpersonvm.australiacentral.cloudapp.azure.com;
        # 對應到 flask的 port
        location / {
                proxy_pass http://127.0.0.1:5000;
                proxy_set_header Host $host;
        }
    }    
    ```
3. 重新啟動 nginx
    - $sudo systemctl restart nginx.service
4. 啟動
    - $sudo systemctl start nginx.service
5. 關閉
    - $sudo systemctl stop nginx.service
6. 設置完成後重新啟動Azure VM就可以看網頁是否成功自動啟動
    - $ sudo reboot

## 程式檔案解說
- 本教案資料夾內包含以下檔案及目錄:
	- app/ # 資料來源為darknet
    - static/ # 靜態資料夾
        - model_image/ # 預測圖片結果資料夾
    - templates/ # 網頁資料夾
        - show.html # 顯示圖片網頁
        - up.html # 上傳網頁
    - upload/ # 圖片上傳資料夾
    - venv/ # python虛擬環境, 執行本教案程式務必先進虛擬環境
    - image_upload.ipynb #主程式教案說明
    - image_upload.py # 主程式
    - requirements.txt # python套件安裝檔
    - readme.md # 教案說明檔
    - run.sh # 進入虛擬環境後，並執行主程式啟動 yolov4 + Web
    - run # 進入虛擬環境
    


