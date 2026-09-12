package com.alvis.media.controller;

import com.alvis.media.base.SystemCode;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import jakarta.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

@RestController
public class ErrorController implements org.springframework.boot.web.servlet.error.ErrorController {

    @RequestMapping(value = "/error", produces = {MediaType.APPLICATION_JSON_VALUE})
    @ResponseBody
    public ResponseEntity<Map<String, Object>> error(HttpServletRequest request) {
        Map<String, Object> error = new HashMap<>(2);
        error.put("code", SystemCode.InnerError.getCode());
        error.put("message", SystemCode.InnerError.getMessage());
        return new ResponseEntity<>(error, HttpStatus.OK);
    }
}
