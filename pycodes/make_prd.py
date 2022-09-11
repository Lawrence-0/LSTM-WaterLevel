from math import sqrt
from numpy import concatenate
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from pycodes.make_data import make_data
import tensorflow as tf
import numpy as np
import keras
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

def _series_to_supervised(data, n_in = 1, n_out = 1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    agg = concat(cols, axis=1)
    agg.columns = names
    if dropnan:
        agg.dropna(inplace=True)
    return agg

def _model_training(obsvId, mode, n_in = 6):
    dataset = make_data(obsvId, mode)
    obsvNum = dataset.shape[1]
    values = dataset.values
    values = values.astype('float32')
    scaler = MinMaxScaler(feature_range = (0, 1))
    scaled = scaler.fit_transform(values)
    reframed = _series_to_supervised(scaled, n_in, 1)
    reframed.drop(reframed.columns[range(1 - obsvNum, 0)], axis = 1, inplace = True)
    values = reframed.values
    n_train_hours = 50000
    train = values[:n_train_hours, :]
    test = values[:, :]   #[n_train_hours:, :]
    train_X, train_y = train[:, :-1], train[:, -1]
    test_X, test_y = test[:, :-1], test[:, -1]
    train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
    test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
    model = Sequential()
    model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2]), return_sequences=True))
    model.add(Dense(1, activation = 'tanh'))
    model.compile(loss='mae', optimizer='adam')
    history = model.fit(train_X, train_y, epochs=50, batch_size=72, validation_data=(test_X, test_y), verbose=2, shuffle=False)
    model.save('./models/mlit_rain/' + str(obsvId) + '.h5')

def _model_predicting(obsvId, mode, n_in = 6):
    if os.path.exists('./models/mlit_rain/' + str(obsvId) + '.h5'):
        model = keras.models.load_model('./models/mlit_rain/' + str(obsvId) + '.h5')
        dataset = make_data(obsvId, mode)
        obsvNum = dataset.shape[1]
        values = dataset.values
        values = values.astype('float32')
        scaler = MinMaxScaler(feature_range = (0, 1))
        scaled = scaler.fit_transform(values)
        reframed = _series_to_supervised(scaled, n_in, 1)
        reframed.drop(reframed.columns[range(1 - obsvNum, 0)], axis = 1, inplace = True)
        values = reframed.values
        n_train_hours = 50000
        train = values[:n_train_hours, :]
        test = values[:, :]   #[n_train_hours:, :]
        train_X, train_y = train[:, :-1], train[:, -1]
        test_X, test_y = test[:, :-1], test[:, -1]
        train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
        yhat = model.predict(test_X)
        yhat = yhat[:,0]
        test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
        inv_yhat = concatenate((yhat, test_X[:, 1 - obsvNum:]), axis=1)
        inv_yhat = scaler.inverse_transform(inv_yhat[:, - obsvNum:])
        inv_yhat = inv_yhat[:,0]
        result = np.asarray([0] * n_in + list(inv_yhat))
        np.save('./models/mlit_rain/' + str(obsvId) + '.npy', result)
    else:
        _model_training(obsvId, mode, n_in)
        _model_predicting(obsvId, mode, n_in)

def _prediction_getting(obsvId, mode, n_in = 6):
    if os.path.exists('./models/mlit_rain/' + str(obsvId) + '.npy'):
        predictionData = np.load('./models/mlit_rain/' + str(obsvId) + '.npy')
    else:
        _model_predicting(obsvId, mode, n_in)
        predictionData = np.load('./models/mlit_rain/' + str(obsvId) + '.npy')
    return list(predictionData)