package com.alvis.media.configuration.spring.exception;

import com.alvis.media.base.RestResponse;
import com.alvis.media.base.SystemCode;
import com.alvis.media.utility.ErrorUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.util.stream.Collectors;

@ControllerAdvice
public class ExceptionHandle {
    private final static Logger logger = LoggerFactory.getLogger(ExceptionHandle.class);

    /**
     * 兜底异常：真实 500；细节只进日志，不把内部 e.getMessage 拼给用户（避免泄漏实现细节）。
     */
    @ExceptionHandler(Exception.class)
    @ResponseBody
    public ResponseEntity<RestResponse> handler(Exception e) {
        logger.error(e.getMessage(), e);
        return new ResponseEntity<>(
                new RestResponse<>(SystemCode.InnerError.getCode(), SystemCode.InnerError.getMessage()),
                HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /** MVC 静态资源/路径不存在：真实 404 */
    @ExceptionHandler(NoResourceFoundException.class)
    @ResponseBody
    public ResponseEntity<RestResponse> handler(NoResourceFoundException e) {
        return new ResponseEntity<>(
                new RestResponse<>(HttpStatus.NOT_FOUND.value(), "资源不存在"),
                HttpStatus.NOT_FOUND);
    }

    /** 请求方法不支持：真实 405 */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    @ResponseBody
    public ResponseEntity<RestResponse> handler(HttpRequestMethodNotSupportedException e) {
        return new ResponseEntity<>(
                new RestResponse<>(HttpStatus.METHOD_NOT_ALLOWED.value(), "请求方法不支持"),
                HttpStatus.METHOD_NOT_ALLOWED);
    }

    /** 请求体不可读/参数类型不匹配：真实 400（注意不能与兜底 handler(Exception) 同签名） */
    @ExceptionHandler({HttpMessageNotReadableException.class, MethodArgumentTypeMismatchException.class})
    @ResponseBody
    public ResponseEntity<RestResponse> handleBadRequest(Exception e) {
        return new ResponseEntity<>(
                new RestResponse<>(HttpStatus.BAD_REQUEST.value(), "请求参数错误"),
                HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseBody
    public ResponseEntity<RestResponse> handler(MethodArgumentNotValidException e) {
        String errorMsg = e.getBindingResult().getAllErrors().stream().map(file -> {
            FieldError fieldError = (FieldError) file;
            return ErrorUtil.parameterErrorFormat(fieldError.getField(), fieldError.getDefaultMessage());
        }).collect(Collectors.joining());
        return new ResponseEntity<>(
                new RestResponse<>(SystemCode.ParameterValidError.getCode(), errorMsg),
                HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(BindException.class)
    @ResponseBody
    public ResponseEntity<RestResponse> handler(BindException e) {
        String errorMsg = e.getBindingResult().getAllErrors().stream().map(file -> {
            FieldError fieldError = (FieldError) file;
            return ErrorUtil.parameterErrorFormat(fieldError.getField(), fieldError.getDefaultMessage());
        }).collect(Collectors.joining());
        return new ResponseEntity<>(
                new RestResponse<>(SystemCode.ParameterValidError.getCode(), errorMsg),
                HttpStatus.BAD_REQUEST);
    }
}
