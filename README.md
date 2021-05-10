# Transfer-learning
Compare performance of Fine-tuning and Feature extraction based method for Alex-Net model on CIFAR-10 

This project implelments:
transfer learning using alexnet dataset using 
    1.feature extraction method
	  2.fine tuning method

the project is implemented using google colabs
compilation and execution instruction 
1:upload the data set in the google drive
2:open the .ipynb file in colab connected with the account in which dataset was uploaded
3:change the location of the dataset in the line base_dir = '/content/drive/My Drive/data/places/' with the location where you stored the dataset. Generally you need to change after MyDrive.
4:save the code 
5:run it using runtime-run all
6:use run all this will ask for a authorization code for which the link will be given above the box where the code needs to be pasted. the link will display a code.
7:copy the code and paste it in the box and press enter.
8.it may again ask you for verification code and the steps are same as in step6 and step7
9.once done it will run completely and provide you the output.

results: accuracy
1. feature extractor : 0.73
2. fine tuning : 0.75
3. fine tuning with augmentation:0.76

This zip folder contains:
result- this folder has all the output sample images with readme file.
feature.py - program of feature extraction method
finetune.py - program of fine tuning method
fineplus.py - program of fine tuning method with dataset agumantation

system configuration: gpu enabled google colabs

