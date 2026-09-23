package com.alvis.media.configuration.spring.mvc;

import com.alvis.media.configuration.property.SystemConfig;
import com.alvis.media.configuration.spring.wx.TokenHandlerInterceptor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.CacheControl;
import org.springframework.util.StringUtils;
import org.springframework.web.servlet.config.annotation.*;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.List;


/**
 *@author 奇趣
 */

@Configuration
public class WebMvcConfiguration implements WebMvcConfigurer {

    private final TokenHandlerInterceptor tokenHandlerInterceptor;
    private final SystemConfig systemConfig;

    /**
     * Python 离线 EDA 图目录（Movie-Analysis-master/FeatureEDA/figures），
     * 通过 /eda/** 暴露给前端图库页面。配置了且目录存在时优先读外部目录
     * （重跑 Python EDA 后无需重启后端即可看到新图）；否则回退 jar 内
     * classpath:/static/eda/ 的兜底快照。
     */
    @Value("${system.eda.dir:}")
    private String edaDir;

    /**
     * 票房预测的算法对比图目录（algorithm/boxoffice_prediction/figures），
     * 通过 /algo-figures/** 暴露给前端「算法对比」页面。
     */
    @Value("${system.algo.dir:}")
    private String algoDir;

    public WebMvcConfiguration(TokenHandlerInterceptor tokenHandlerInterceptor,
                               SystemConfig systemConfig) {
        this.tokenHandlerInterceptor = tokenHandlerInterceptor;
        this.systemConfig = systemConfig;
    }

    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addRedirectViewController("/", "/student/index.html");
        registry.addRedirectViewController("/student", "/student/index.html");
        registry.addRedirectViewController("/admin", "/admin/index.html");
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // Python EDA 图：优先外部 figures 目录，无配置/目录缺失时回退 classpath 快照
        String edaClasspath = "classpath:/static/eda/";
        if (StringUtils.hasText(edaDir) && Files.exists(Paths.get(edaDir))) {
            registry.addResourceHandler("/eda/**")
                    .addResourceLocations(Paths.get(edaDir).toUri().toString(), edaClasspath)
                    .setCacheControl(CacheControl.maxAge(Duration.ofMinutes(10)).cachePublic());
        } else {
            registry.addResourceHandler("/eda/**")
                    .addResourceLocations(edaClasspath)
                    .setCacheControl(CacheControl.maxAge(Duration.ofMinutes(10)).cachePublic());
        }

        // 算法对比图：algorithm/boxoffice_prediction/figures → /algo-figures/**
        if (StringUtils.hasText(algoDir) && Files.exists(Paths.get(algoDir))) {
            registry.addResourceHandler("/algo-figures/**")
                    .addResourceLocations(Paths.get(algoDir).toUri().toString())
                    .setCacheControl(CacheControl.maxAge(Duration.ofMinutes(10)).cachePublic());
        }

        // HTML 入口不缓存：Vite 每次构建会生成新的内容哈希文件名，index.html 里引用的是最新 bundle。
        // 若 index.html 被长缓存，浏览器会拿到旧引用，指向已删除的旧 bundle（请求返回 500），导致白屏。
        // 因此所有 .html 一律 no-store，始终拉取最新。
        registry.addResourceHandler("/**/*.html")
                .addResourceLocations("classpath:/static/")
                .setCacheControl(CacheControl.noStore());

        // 其余静态资源（js/css 文件名带内容哈希，可放心长缓存）
        registry.addResourceHandler("/**")
                .addResourceLocations("classpath:/static/")
                .setCacheControl(CacheControl.maxAge(Duration.ofSeconds(31556926)).cachePublic());
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        List<String> securityIgnoreUrls = systemConfig.getWx().getSecurityIgnoreUrls();
        String[] ignores = new String[securityIgnoreUrls.size()];
        registry.addInterceptor(tokenHandlerInterceptor)
                .addPathPatterns("/api/wx/**")
                .excludePathPatterns(securityIgnoreUrls.toArray(ignores));
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowCredentials(true)
                .allowedMethods("*")
                .allowedOriginPatterns("*")
                .allowedHeaders("*");
    }

}
