package com.alvis.media.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * 静态页入口重定向。
 *
 * 背景：Spring Boot 3 里 addRedirectViewController 注册的视图控制器与 "/**" 静态资源处理器
 * 同优先级，资源处理器会抢赢匹配，导致访问 /admin 时被当成静态目录查找而抛
 * NoResourceFoundException。改用 @Controller（优先级最高）显式重定向到 index.html。
 */
@Controller
public class IndexController {

    @GetMapping({"/admin", "/admin/"})
    public String admin() {
        return "redirect:/admin/index.html";
    }

    @GetMapping("/")
    public String index() {
        return "redirect:/admin/index.html";
    }
}
