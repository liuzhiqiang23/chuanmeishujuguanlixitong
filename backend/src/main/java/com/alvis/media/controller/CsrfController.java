package com.alvis.media.controller;

import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class CsrfController {

    @GetMapping("/api/csrf")
    public Map<String, String> csrfToken(CsrfToken csrfToken) {
        return Map.of("token", csrfToken.getToken());
    }
}
