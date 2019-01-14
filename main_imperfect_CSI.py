# Date: 8th Jan, 2019
# Author: Tian Lin
# Email: lint17@fudan.edu.cn
# newest modification: 13th Jan, 2019

import tensorflow as tf
tf.enable_eager_execution()    # debugging with dynamic graph
from BFNN.load_samples import *  # load the samples generated by MATLAB
from BFNN.BFNN_Model import *  # the basic construction of neural network

# type 0 in python console to train and 1 to test.
Mode = int(input('Please type 0 or 1 in the python console to choose Mode: \n 0: train  1: test \n'))

if Mode:  # test mode
    Model_path = input('copy trained model path for testing: \n')  # copy the path of the trained NN to test
    model = bfnn_model()  # construct the BFNN model
    model.load_weights(Model_path)  # load the trained weights
    hr, hi, hr_est, hi_est, noise_power = load_data_estimated_csi(Mode)  # load the perfect CSI and estimated CSI
    sample_num, Nr = hr.shape  # numbers of samples and receive antennas
    BFNN_rate = []  # create a list to save rate results of different SNRs
    for SNR in range(-20, 25, 5):
        sigma_2 = 1 / np.power(10, SNR / 10)  # generate sigma^{-2}
        # find the corresponding index of the estimated csi under this snr
        Index = np.nonzero(noise_power == sigma_2)[0]
        # find the samples under this snr
        noise_power_snr = noise_power[Index]
        hr_est_snr = hr_est[Index]
        hi_est_snr = hi_est[Index]
        hr_snr = hr[Index]
        hi_snr = hi[Index]
        signal_power = 1/ noise_power_snr  # generate the corresponding sigma^{-2}
        #  the input_imperfect_info includes estimated csi and snr
        input_imperfect_info = np.concatenate([hr_est_snr, hi_est_snr, signal_power], 1)
        input_perfect_info = np.concatenate([hr_snr, hi_snr, signal_power], 1)
        # v_RF = model.predict(input_imperfect_info)  # the phases of the obtained v_RF
        # the imperfect csi (estimated by some traditional estimation method) is fed into the BFNN to form the vRF
        # and then the perfect csi is fed into the loss function to compute the loss (the rate of the system)
        rate = model.evaluate(input_imperfect_info, input_perfect_info, batch_size=2000)
        BFNN_rate.append(-rate)  # save the result under this SNR
    print(BFNN_rate)

else:  # train mode
    hr, hi, hr_est, hi_est, noise_power = load_data_estimated_csi(Mode)  # load the perfect CSI and estimated CSI
    sample_num, Nr = hr.shape  # numbers of samples and receive antennas
    model = bfnn_model()  # construct the BFNN model
    # model.load_weights('./trained.h5') # start from trained model, for continued training or fine-tuning
    signal_power = 1/ noise_power  # generate the corresponding sigma^{-2}
    input_imperfect_info = np.concatenate([hr_est, hi_est, signal_power], 1)
    input_perfect_info = np.concatenate([hr, hi, signal_power], 1)  # the dimension of the input is 2Nt+1
    # the checkpoint is for saving the model weights with best performance of the validation set
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        './trained_models/temp_imperfect_trained.h5', monitor='val_loss', verbose=0,
        save_best_only=True, mode='min',save_weights_only=True)
    # in this scenario that assume the perfect CSI is known at the transmitter, the input_info is fed into the
    # BFNN to form the vRF, and then also fed into the loss function to compute the loss (the rate of the system)
    model.fit(input_imperfect_info, input_perfect_info, epochs=30000, batch_size=512, verbose=2,
              callbacks=[checkpoint], validation_split=0.2)







