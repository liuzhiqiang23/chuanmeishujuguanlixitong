package com.alvis.media.controller;

import com.alvis.media.base.SystemCode;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

@RestController
public class ErrorController implements org.springframework.boot.web.servlet.error.ErrorController {

    /**
     * /error 兜底：安全过滤链 sendError（如源站校验 403）、404 等会转发到这里。
     * 透传容器原始状态码（不再用 HTTP 200 包业务码，避免误导监控与排障），并给出可读消息。
     */
    @RequestMapping(value = "/error", produces = {MediaType.APPLICATION_JSON_VALUE})
    @ResponseBody
    public ResponseEntity<Map<String, Object>> error(HttpServletRequest request) {
        HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
        Object attr = request.getAttribute(RequestDispatcher.ERROR_STATUS_CODE);
        if (attr instanceof Integer code) {
            HttpStatus resolved = HttpStatus.resolve(code);
            if (resolved != null) {
                status = resolved;
            }
        }
        String message = switch (status) {
            case UNAUTHORIZED -> "登录状态已失效，请重新登录";
            case FORBIDDEN -> "没有权限访问该资源";
            case NOT_FOUND -> "资源不存在";
            default -> SystemCode.InnerError.getMessage();
        };
        Map<String, Object> error = new HashMap<>(2);
        error.put("code", status.value());
        error.put("message", message);
        return new ResponseEntity<>(error, status);
    }
}
