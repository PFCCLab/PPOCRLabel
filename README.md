English | [简体中文](README_ch.md)

# PPOCRLabelv3

[![PyPI - Version](https://img.shields.io/pypi/v/PPOCRLabel)](https://pypi.org/project/PPOCRLabel/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/PPOCRLabel)](https://github.com/PFCCLab/PPOCRLabel)
[![Downloads](https://static.pepy.tech/badge/PPOCRLabel)](https://github.com/PFCCLab/PPOCRLabel)

PPOCRLabelv3 is a semi-automatic graphic annotation tool suitable for OCR field, with built-in PP-OCR model to automatically detect and re-recognize data. It is written in Python3 and PyQT5, supporting rectangular box, table, irregular text and key information annotation modes. Annotations can be directly used for the training of PP-OCR detection and recognition models.

|               regular text annotation               |                table annotation                |
| :-------------------------------------------------: | :--------------------------------------------: |
|  <img src="./data/gif/steps_en.gif" width="80%"/>   | <img src="./data/gif/table.gif" width="100%"/> |
|            **irregular text annotation**            |         **key information annotation**         |
| <img src="./data/gif/multi-point.gif" width="80%"/> |  <img src="./data/gif/kie.gif" width="100%"/>  |

### Recent Update
- 2025.06:
  - Add the `Resort Bounding Box Positions` features. For usage details, please refer to the `11. Additional Feature Description` in the `2.1 Operational Steps` section below.
- 2024.11:
  - Add the `label_font_path` parameter to change the font of the label.
  - Add the `selected_shape_color` parameter to change the color of the selected label box and font.
- 2024.09:
  - Added `Re-recognition` and `Auto Save Unsaved changes` features. For usage details, please refer to the `11. Additional Feature Description` in the `2.1 Operational Steps` section below.
  - Added the parameter `--img_list_natural_sort`, which defaults to natural sorting for the left image list. After configuring this parameter, character sorting will be used to easily locate images based on character order.
  - Add 4 custom model parameters:
    - `det_model_dir`: Path to the detection model directory
    - `rec_model_dir`: Path to the recognition model directory
    - `rec_char_dict_path`: Path to the recognition model dictionary file
    - `cls_model_dir`: Path to the classification model directory
  - Added the `--bbox_auto_zoom_center` parameter, which can be enabled when there is only one bounding box in the image, automatically centering and zooming in on the bounding box.
  - Added 5 shortcut keys `z`, `x`, `c`, `v`, `b` for controlling the 4 vertices of the bounding box. For usage details, see the '11. Additional Functionality Description' in "2.1 Operating Procedures" below.
- 2022.05: Add table annotations, follow `2.2 Table Annotations` for more information (by [whjdark](https://github.com/peterh0323); [Evezerest](https://github.com/Evezerest))
- 2022.02: (by [PeterH0323](https://github.com/peterh0323))
  - Add KIE Mode by using `--kie`, for [detection + identification + keyword extraction] labeling.
  - Improve user experience: prompt for the number of files and labels, optimize interaction, and fix bugs such as only use CPU when inference
  - New functions: Support using `C` or `X` to rotate box.
- 2021.11.17:
  - Support install and start PPOCRLabel through the whl package (by [d2623587501](https://github.com/d2623587501))
  - Dataset segmentation: Divide the annotation file into training, verification and testing parts (refer to section 3.5 below, by [MrCuiHao](https://github.com/MrCuiHao))
- 2021.8.11:
  - New functions: Open the dataset folder, image rotation (Note: Please delete the label box before rotating the image) (by [Wei-JL](https://github.com/Wei-JL))
  - Added shortcut key description (Help-Shortcut Key), repaired the direction shortcut key movement function under batch processing (by [d2623587501](https://github.com/d2623587501))
- 2021.2.5: New batch processing and undo functions (by [Evezerest](https://github.com/Evezerest)):
  - **Batch processing function**: Press and hold the Ctrl key to select the box, you can move, copy, and delete in batches.
  - **Undo function**: In the process of drawing a four-point label box or after editing the box, press Ctrl+Z to undo the previous operation.
  - Fix image rotation and size problems, optimize the process of editing the mark frame (by [ninetailskim](https://github.com/ninetailskim)、 [edencfc](https://github.com/edencfc)).
- 2021.1.11: Optimize the labeling experience (by [edencfc](https://github.com/edencfc)),
  - Users can choose whether to pop up the label input dialog after drawing the detection box in "View - Pop-up Label Input Dialog".
  - The recognition result scrolls synchronously when users click related detection box.
  - Click to modify the recognition result.(If you can't change the result, please switch to the system default input method, or switch back to the original input method again)
- 2020.12.18: Support re-recognition of a single label box (by [ninetailskim](https://github.com/ninetailskim) ), perfect shortcut keys.

## 1. Installation and Run

### 1.1 Install PaddlePaddle

```bash
pip3 install --upgrade pip

# If you only have cpu on your machine, please run the following command to install
python3 -m pip install paddlepaddle -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

For more software version requirements, please refer to the instructions in [Installation Document](https://www.paddlepaddle.org.cn/install/quick) for operation.

### 1.2 Install and Run PPOCRLabel

PPOCRLabel can be started in two ways: whl package and Python script. The whl package form is more convenient to start, and the python script to start is convenient for secondary development.

> Note: By default, PPOCRLabel starts with a **Chinese** UI (`--lang ch`). To switch to **English**, you need to launch the application with the `--lang en` parameter.

#### Windows

```bash
pip install PPOCRLabel  # install

# Select label mode and run
PPOCRLabel  # [Normal mode] for [detection + recognition] labeling
PPOCRLabel --kie True # [KIE mode] for [detection + recognition + keyword extraction] labeling
```

> If you getting this error `OSError: [WinError 126] The specified module could not be found` when you install shapely on windows. Please try to download Shapely whl file using http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely.
>
> Reference: [Solve shapely installation on windows](https://stackoverflow.com/questions/44398265/install-shapely-oserror-winerror-126-the-specified-module-could-not-be-found)
>

#### Ubuntu Linux

```bash
pip3 install PPOCRLabel
pip3 install trash-cli
export QT_QPA_PLATFORM=wayland # Consider adding it to the system environment variables to avoid entering it multiple times.

# Select label mode and run
PPOCRLabel  # [Normal mode] for [detection + recognition] labeling
PPOCRLabel --kie True # [KIE mode] for [detection + recognition + keyword extraction] labeling
```

#### MacOS

```bash
pip3 install PPOCRLabel
pip3 install opencv-contrib-python-headless==4.2.0.32

# Select label mode and run
PPOCRLabel  # [Normal mode] for [detection + recognition] labeling
PPOCRLabel --kie True # [KIE mode] for [detection + recognition + keyword extraction] labeling
```

#### 1.2.2 Run PPOCRLabel by Python Script

If you modify the PPOCRLabel file (for example, specifying a new built-in model), it will be more convenient to see the results by running the Python script. If you still want to start with the whl package, you need to uninstall the whl package in the current environment and then recompile it according to the next section.

```bash
cd ./PPOCRLabel  # Switch to the PPOCRLabel directory

# Select label mode and run
python PPOCRLabel.py  # [Normal mode] for [detection + recognition] labeling
python PPOCRLabel.py --kie True # [KIE mode] for [detection + recognition + keyword extraction] labeling
```

#### 1.2.3 Build and Install the Whl Package Locally

```bash
cd ./PPOCRLabel
pip3 install -e .
```

#### 1.2.4 Pyinstaller build

```bash
cd ./PPOCRLabel
# install pyinstaller
pip install pyinstaller

# Regenerate Resources
pyrcc5 -o libs/resources.py resources.qrc

# Packaging executable programs
pyinstaller -c PPOCRLabel.py --collect-all paddleocr --collect-all pyclipper --collect-all imghdr --collect-all skimage --collect-all imgaug --collect-all scipy.io --collect-all lmdb --collect-all paddle --hidden-import=pyqt5  -p ./libs -p ./ -p ./data -p ./resources -F

# Run the executable program in dist, windows as an example
PPOCRLabel.exe --lang ch
```

## 2. Usage

### 2.1 Steps

1. Build and launch using the instructions above.

2. Click 'Open Dir' in Menu/File to select the folder of the picture.<sup>[1]</sup>

3. Click 'Auto recognition', use PP-OCR model to automatically annotate images which marked with 'X' <sup>[2]</sup>before the file name.

4. Create Box:

   4.1 Click 'Create RectBox' or press 'W' in English keyboard mode to draw a new rectangle detection box. Click and release left mouse to select a region to annotate the text area.

   4.2 Press 'Q' to enter four-point labeling mode which enables you to create any four-point shape by clicking four points with the left mouse button in succession and DOUBLE CLICK the left mouse as the signal of labeling completion.

5. After the marking frame is drawn, the user clicks "OK", and the detection frame will be pre-assigned a "TEMPORARY" label.

6. Click 're-Recognition', model will rewrite ALL recognition results in ALL detection box<sup>[3]</sup>.

7. Single click the result in 'recognition result' list to manually change inaccurate recognition results.

8. **Click "Check", the image status will switch to "√",then the program automatically jump to the next.**

9. Click "Delete Image", and the image will be deleted to the recycle bin.

10. Labeling result: the user can export the label result manually through the menu "File - Export Label", while the program will also export automatically if "File - Auto export Label Mode" is selected. The manually checked label will be stored in *Label.txt* under the opened picture folder. Click "File"-"Export Recognition Results" in the menu bar, the recognition training data of such pictures will be saved in the *crop_img* folder, and the recognition label will be saved in *rec_gt.txt*<sup>[4]</sup>.

11. Additional Feature Description
    - `File` -> `Re-recognition`: After checking, the newly annotated box content will automatically trigger the `Re-recognition` function of the current annotation box, eliminating the need to click the Re-identify button. This is suitable for scenarios where you do not want to use Automatic Annotation but prefer manual annotation, such as license plate recognition. In a single image with only one license plate, using Automatic Annotation would require deleting many additional recognized text boxes, which is less efficient than directly re-annotating.
    - `File` -> `Auto Save Unsaved changes`: By default, you need to press the `Check` button to complete the marking confirmation for the current box, which can be cumbersome. After checking, when switching to the next image (by pressing the shortcut key `D`), a prompt box asking to confirm whether to save unconfirmed markings will no longer appear. The current markings will be automatically saved and the next image will be switched, making it convenient for quick marking.
    - After selecting the bounding box, there are 5 shortcut keys available to individually control the movement of the four vertices of the bounding box, suitable for scenarios that require precise control over the positions of the bounding box vertices:
      - `z`: After pressing, the up, down, left, and right arrow keys will move the 1st vertex individually.
      - `x`: After pressing, the up, down, left, and right arrow keys will move the 2nd vertex individually.
      - `c`: After pressing, the up, down, left, and right arrow keys will move the 3rd vertex individually.
      - `v`: After pressing, the up, down, left, and right arrow keys will move the 4th vertex individually.
      - `b`: After pressing, the up, down, left, and right arrow keys will revert to the default action of moving the entire bounding box.
    - `Bottom right` -> `Resort Positions`: Clicking this will arrange the bounding boxes in order from top to bottom and left to right. This is used to address the issue of manually adjusting the order after adding rectangular labels when identifying table structures.

### 2.2 Table Annotation

The table annotation is aimed at extracting the structure of the table in a picture and converting it to Excel format,
so the annotation needs to be done simultaneously with external software to edit Excel.
In PPOCRLabel, complete the text information labeling (text and position), complete the table structure information
labeling in the Excel file, the recommended steps are:

1. Table annotation: After opening the table picture, click on the `Table Recognition` button in the upper right corner of PPOCRLabel, which will call the table recognition model in PP-Structure to automatically label
    the table and pop up Excel at the same time.

2. Change the recognition result: **label each cell** (i.e. the text in a cell is marked as a box). Right click on the box and click on `Cell Re-recognition`.
   You can use the model to automatically recognise the text within a cell.

3. Mark the table structure: for each cell contains the text, **mark as any identifier (such as `1`) in Excel**, to ensure that the merged cell structure is same as the original picture.

    > Note: If there are blank cells in the table, you also need to mark them with a bounding box so that the total number of cells is the same as in the image.

4. ***Adjust cell order:*** Click on the menu  `View` - `Show Box Number` to show the box ordinal numbers, and drag all the results under the 'Recognition Results' column on the right side of the software interface to make the box numbers are arranged from left to right, top to bottom

5. Export JSON format annotation: close all Excel files corresponding to table images, click `File`-`Export Table Label` to obtain `gt.txt` annotation results.

### 2.3 Note

[1] PPOCRLabel uses the opened folder as the project. After opening the image folder, the picture will not be displayed in the dialog. Instead, the pictures under the folder will be directly imported into the program after clicking "Open Dir".

[2] The image status indicates whether the user has saved the image manually. If it has not been saved manually it is "X", otherwise it is "√", PPOCRLabel will not relabel pictures with a status of "√".

[3] After clicking "Re-recognize", the model will overwrite ALL recognition results in the picture. Therefore, if the recognition result has been manually changed before, it may change after re-recognition.

[4] The files produced by PPOCRLabel can be found under the opened picture folder including the following, please do not manually change the contents, otherwise it will cause the program to be abnormal.

|   File name   |                         Description                          |
| :-----------: | :----------------------------------------------------------: |
|   Label.txt   | The detection label file can be directly used for PP-OCR detection model training. After the user saves 5 label results, the file will be automatically exported. It will also be written when the user closes the application or changes the file folder. |
| fileState.txt | The picture status file save the image in the current folder that has been manually confirmed by the user. |
|  Cache.cach   |    Cache files to save the results of model recognition.     |
|  rec_gt.txt   | The recognition label file, which can be directly used for PP-OCR identification model training, is generated after the user clicks on the menu bar "File"-"Export recognition result". |
|   crop_img    | The recognition data, generated at the same time with *rec_gt.txt* |



## 3. Explanation

### 3.1 Shortcut keys

| Shortcut keys            | Description                                      |
|--------------------------|--------------------------------------------------|
| Ctrl + Shift + R         | Re-recognize all the labels of the current image |
| W                        | Create a rect box                                |
| Q  or  Home              | Create a multi-points box                         |
| Ctrl + E                 | Edit label of the selected box                   |
| Ctrl + X                 | Change key class of the box when enable `--kie`  |
| Ctrl + R                 | Re-recognize the selected box                    |
| Ctrl + C                 | Copy and paste the selected box                  |
| Ctrl + B                 | Resort Bounding Box Positions |
| Ctrl + Left Mouse Button | Multi select the label box                       |
| Backspace or Delete      | Delete the selected box                          |
| Ctrl + V  or End         | Check image                                      |
| Ctrl + Shift + d         | Delete image                                     |
| D                        | Next image                                       |
| A                        | Previous image                                   |
| Ctrl++                   | Zoom in                                          |
| Ctrl--                   | Zoom out                                         |
| ↑→↓←                     | Move selected box                                |
| Z, X, C, V, B     | Move the four vertices of the selected bounding box individually|

### 3.2 Built-in Model

- Default model: PPOCRLabel uses the Chinese and English ultra-lightweight OCR model in PaddleOCR by default, supports Chinese, English and number recognition, and multiple language detection.

- Model language switching: Changing the built-in model language is supportable by clicking "PaddleOCR"-"Choose OCR Model" in the menu bar. Currently supported languages​include French, German, Korean, and Japanese.
  For specific model download links, please refer to [PaddleOCR Model List](https://github.com/PaddlePaddle/PaddleOCR/blob/release/3.0/docs/version3.x/model_list.md).

- **Custom Model**: If users want to replace the built-in model with their own inference model. Through the following code example:
 ```
 from paddleocr import PaddleOCR, PPStructureV3
  ocr = PaddleOCR(
  text_detection_model_name='{your_text_det_model_name}',
  text_detection_model_dir='{your_text_det_model_dir}',
  text_recognition_model_name='{your_text_rec_model_name}',
  text_recognition_model_dir='{your_text_rec_model_dir}',  
)

table_ocr = PPStructureV3(
  layout_detection_model_name='{your_layout_det_model_name}',
  layout_detection_model_dir='{your_layout_det_model_dir}',
  chart_recognition_model_name='{your_chart_rec_model_name}',
  chart_recognition_model_dir='{your_chart_rec_model_dir}',
  region_detection_model_name='{your_region_det_model_name}',
  region_detection_model_dir='{your_region_det_model_dir}',
  # For detailed replacement of other models, refer to the instantiation of the PPStructure class below. Simply replace the model path with the path to your own inference model.
)
 ```
 By modifying PPOCRLabel.py for [Instantiation of PaddleOCR class](https://github.com/PaddlePaddle/PaddleOCR/blob/release/3.0/paddleocr/_pipelines/ocr.py#L55) or [Instantiation of PaddleOCR class](https://github.com/PaddlePaddle/PaddleOCR/blob/release/3.0/paddleocr/_pipelines/pp_structurev3.py#L25). For example, to specify a detection model, use the following: self.ocr = PaddleOCR(use_doc_orientation_classify=False, use_textline_orientation=False, use_doc_unwarping=False, device=gpu, lang=lang). Add the parameters text_detection_model_name and text_detection_model_dir, and pass in your own model path.

### 3.3 Export Label Result

PPOCRLabel supports three ways to export Label.txt

- Automatically export: After selecting "File - Auto Export Label Mode", the program will automatically write the annotations into Label.txt every time the user confirms an image. If this option is not turned on, it will be automatically exported after detecting that the user has manually checked 5 images.

  > The automatically export mode is turned off by default

- Manual export: Click "File-Export Marking Results" to manually export the label.

- Close application export

### 3.4 Dataset division

- Enter the following command in the terminal to execute the dataset division script:

    ```
  cd ./PPOCRLabel # Change the directory to the PPOCRLabel folder
  python gen_ocr_train_val_test.py --trainValTestRatio 6:2:2 --datasetRootPath ../train_data
  ```

  Parameter Description:

  - `trainValTestRatio` is the division ratio of the number of images in the training set, validation set, and test set, set according to your actual situation, the default is `6:2:2`

  - `datasetRootPath` is the storage path of the complete dataset labeled by PPOCRLabel. The default path is `PaddleOCR/train_data` .
  ```
  |-train_data
    |-crop_img
      |- word_001_crop_0.png
      |- word_002_crop_0.jpg
      |- word_003_crop_0.jpg
      | ...
    | Label.txt
    | rec_gt.txt
    |- word_001.png
    |- word_002.jpg
    |- word_003.jpg
    | ...
  ```

### 3.5 Error message

- If paddleocr is installed with whl, it has a higher priority than calling PaddleOCR class with paddleocr.py, which may cause an exception if whl package is not updated.

- For Linux users, if you get an error starting with **objc[XXXXX]** when opening the software, it proves that your opencv version is too high. It is recommended to install version 4.2:

    ```
    pip install opencv-python==4.2.0.32
    ```
- For Linux users: If you encounter the error starting with ```qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found. ```while opening a software, follow these steps:
    ```
    pip uninstall opencv-python
    pip uninstall opencv-contrib-python
    pip install opencv-python-headless
    export QT_QPA_PLATFORM=wayland
    ```
- For Windows users: If you encounter the error ```No python win32com. Error: No module named 'win32com'``` while using table recognition, you can install the required modules by running the following commands:
    ```
    pip install premailer
    pip install pywin32
    ```
- If you get an error starting with **Missing string id **,you need to recompile resources:
    ```
    pyrcc5 -o libs/resources.py resources.qrc
    ```
- If you get an error ``` module 'cv2' has no attribute 'INTER_NEAREST'```, you need to delete all opencv related packages first, and then reinstall the 4.2.0.32  version of headless opencv
    ```
    pip install opencv-contrib-python-headless==4.2.0.32
    ```

### 4. Related

1. [Tzutalin. LabelImg. Git code (2015)](https://github.com/tzutalin/labelImg)
2. [PaddleX Text Detection/Text Recognition Task Module Data Annotation Tutorial](https://paddlepaddle.github.io/PaddleX/latest/en/data_annotations/ocr_modules/text_detection_recognition.html)
