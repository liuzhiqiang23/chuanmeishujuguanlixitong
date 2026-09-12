package com.alvis.media.base;

import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.resource.ResourceHttpRequestHandler;

import jakarta.servlet.http.HttpServletRequest;
import java.nio.file.Path;

@Component
public class NonStaticResourceHttpRequestHandler extends ResourceHttpRequestHandler {
    // 定义视频路径
    public String filepath = "filepath";

    @Override
    protected Resource getResource(HttpServletRequest request) {
        // 获取视频路径对象
        final Path filePath = (Path) request.getAttribute(filepath);
        // 用 FileSystemResource 加载资源
        return new FileSystemResource(filePath);
    }

}
