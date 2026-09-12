package com.alvis.media.service;

import com.alvis.media.viewmodel.predict.PredictRequestVM;
import com.alvis.media.viewmodel.predict.PredictResultVM;

public interface PredictService {
    PredictResultVM predict(PredictRequestVM req);
}
