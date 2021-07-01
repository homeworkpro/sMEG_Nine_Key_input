# sMEG_Nine_Key_input
Using six-channel MEG sensor to capture MEG signal from arms and use CNN to classify finger movement. input_both.py contains a nine-key input_method.   
At first, use record.py to collect database with movement signal for each finger. Record a period of ten seconds with finger moving in 1,3,5,7,9 second. Repeat about 6 times and record 6 files for each finger. Then use jupyter notebook in train folder to train the model for each hand. Put the model into model folder. 
