package com.alvis.media.controller;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.RestResponse;
import com.alvis.media.service.PredictService;
import com.alvis.media.viewmodel.predict.PredictRequestVM;
import com.alvis.media.viewmodel.predict.PredictResultVM;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController("PredictController")
@RequestMapping(value = "/api/predict")
@AllArgsConstructor
public class PredictController extends BaseApiController {

    private final PredictService predictService;

    @PostMapping
    public RestResponse<PredictResultVM> predict(@RequestBody PredictRequestVM req) {
        return RestResponse.ok(predictService.predict(req));
    }
}
