package com.alvis.media.configuration.spring.exception;

import com.alvis.media.base.RestResponse;
import com.alvis.media.base.SystemCode;
import com.alvis.media.utility.ErrorUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.stream.Collectors;

@ControllerAdvice
public class ExceptionHandle {
    private final static Logger logger = LoggerFactory.getLogger(ExceptionHandle.class);

    @ExceptionHandler(Exception.class)
    @ResponseBody
    public RestResponse handler(Exception e) {
        logger.error(e.getMessage(), e);
        // 返回异常摘要，便于前端直接看到真实原因（如缺列、SQL 错误等），方便排查
        String message = SystemCode.InnerError.getMessage();
        if (e.getMessage() != null && !e.getMessage().isEmpty()) {
            message = message + "：" + e.getMessage();
        }
        return new RestResponse<>(SystemCode.InnerError.getCode(), message);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseBody
    public RestResponse handler(MethodArgumentNotValidException e) {
        String errorMsg = e.getBindingResult().getAllErrors().stream().map(file -> {
            FieldError fieldError = (FieldError) file;
            return ErrorUtil.parameterErrorFormat(fieldError.getField(), fieldError.getDefaultMessage());
        }).collect(Collectors.joining());
        return new RestResponse<>(SystemCode.ParameterValidError.getCode(), errorMsg);
    }

    @ExceptionHandler(BindException.class)
    @ResponseBody
    public RestResponse handler(BindException e) {
        String errorMsg = e.getBindingResult().getAllErrors().stream().map(file -> {
            FieldError fieldError = (FieldError) file;
            return ErrorUtil.parameterErrorFormat(fieldError.getField(), fieldError.getDefaultMessage());
        }).collect(Collectors.joining());
        return new RestResponse<>(SystemCode.ParameterValidError.getCode(), errorMsg);
    }


}
