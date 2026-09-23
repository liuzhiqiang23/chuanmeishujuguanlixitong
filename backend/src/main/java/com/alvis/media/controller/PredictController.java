package com.alvis.media.controller;

import com.alvis.media.base.BaseApiController;
import com.alvis.media.base.RestResponse;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.service.PredictService;
import com.alvis.media.viewmodel.predict.*;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 票房预测接口。契约见 docs/04_系统详细设计.md §5.2：
 *   I4 /api/predict（单片）、I5 /api/predict/batch（批量+留痕）、
 *   I5b /api/predict/logs（留痕分页）、I6 /api/predict/algo-compare（算法对比）。
 */
@RestController("PredictController")
@RequestMapping(value = "/api/predict")
@AllArgsConstructor
public class PredictController extends BaseApiController {

    private final PredictService predictService;

    @PostMapping
    public RestResponse<PredictResultVM> predict(@RequestBody PredictRequestVM req) {
        return RestResponse.ok(predictService.predict(req));
    }

    @PostMapping("/batch")
    public RestResponse<BatchPredictResultVM> batch(@RequestBody(required = false) BatchPredictRequestVM req) {
        int limit = req == null || req.getLimit() == null ? 1000 : req.getLimit();
        return RestResponse.ok(predictService.batchPredict(limit));
    }

    @PostMapping("/logs")
    public RestResponse<PageResult<PredictLogVM>> logs(@RequestBody(required = false) PredictLogRequestVM req) {
        return RestResponse.ok(predictService.logs(req == null ? new PredictLogRequestVM() : req));
    }

    @GetMapping("/algo-compare")
    public RestResponse<AlgoCompareVM> algoCompare() {
        return RestResponse.ok(predictService.algoCompare());
    }
}
