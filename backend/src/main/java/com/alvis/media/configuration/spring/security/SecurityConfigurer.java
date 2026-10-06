package com.alvis.media.configuration.spring.security;

import com.alvis.media.configuration.property.CookieConfig;
import com.alvis.media.configuration.property.SystemConfig;
import com.alvis.media.domain.enums.RoleEnum;
import lombok.AllArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.config.Customizer;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.HeadersConfigurer;
import org.springframework.security.web.csrf.CookieCsrfTokenRepository;
import org.springframework.security.web.csrf.CsrfTokenRequestAttributeHandler;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.util.StringUtils;

import java.util.Arrays;
import java.util.List;
import java.util.UUID;


/**
 *@author 奇趣
 */

@Configuration
@EnableWebSecurity
@AllArgsConstructor
public class SecurityConfigurer {

    private final SystemConfig systemConfig;
    private final LoginAuthenticationEntryPoint restAuthenticationEntryPoint;
    private final RestAuthenticationProvider restAuthenticationProvider;
    private final RestDetailsServiceImpl formDetailsService;
    private final RestAuthenticationSuccessHandler restAuthenticationSuccessHandler;
    private final RestAuthenticationFailureHandler restAuthenticationFailureHandler;
    private final RestLogoutSuccessHandler restLogoutSuccessHandler;
    private final RestAccessDeniedHandler restAccessDeniedHandler;

    /**
     * 自定义登录 Filter 的认证管理器：只委托给 RestAuthenticationProvider。
     */
    @Bean
    public AuthenticationManager authenticationManager() {
        return new ProviderManager(restAuthenticationProvider);
    }

    @Bean
    public RestLoginAuthenticationFilter authenticationFilter(AuthenticationManager authenticationManager) {
        RestLoginAuthenticationFilter authenticationFilter = new RestLoginAuthenticationFilter();
        authenticationFilter.setAuthenticationSuccessHandler(restAuthenticationSuccessHandler);
        authenticationFilter.setAuthenticationFailureHandler(restAuthenticationFailureHandler);
        authenticationFilter.setAuthenticationManager(authenticationManager);
        authenticationFilter.setUserDetailsService(formDetailsService);
        // Spring Security 6 中 AbstractAuthenticationProcessingFilter 的 SecurityContextRepository
        // 默认为 null，登录成功后不会把认证信息写入 session，导致后续请求仍是“用户未登录”(401)。
        // 这里显式指定为 HttpSessionSecurityContextRepository（配合 Spring Session Redis）。
        authenticationFilter.setSecurityContextRepository(new HttpSessionSecurityContextRepository());
        return authenticationFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http,
                                                   AuthenticationManager authenticationManager,
                                                   RestLoginAuthenticationFilter authenticationFilter,
                                                   @Value("${app.cors.allowed-origins:}") String allowedOrigins,
                                                   @Value("${app.security.remember-me-key:}") String rememberMeKey) throws Exception {
        http.headers(headers -> headers.frameOptions(HeadersConfigurer.FrameOptionsConfig::sameOrigin));

        List<String> securityIgnoreUrls = systemConfig.getSecurityIgnoreUrls();
        String[] ignores = securityIgnoreUrls.toArray(new String[0]);

        http
                .csrf(csrf -> csrf
                        .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                        .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler())
                        .ignoringRequestMatchers("/api/wx/**", "/api/admin/upload/**"))
                .cors(Customizer.withDefaults())
                .authenticationManager(authenticationManager)
                .addFilterBefore(new RequestOriginFilter(allowedOrigins), UsernamePasswordAuthenticationFilter.class)
                .addFilterAt(authenticationFilter, UsernamePasswordAuthenticationFilter.class)
                .exceptionHandling(ex -> ex
                        .authenticationEntryPoint(restAuthenticationEntryPoint)
                        .accessDeniedHandler(restAccessDeniedHandler))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.GET, "/api/admin/upload/configAndUpload").hasRole(RoleEnum.ADMIN.getName())
                        .requestMatchers("/api/admin/**").hasRole(RoleEnum.ADMIN.getName())
                        .requestMatchers("/video/**").hasRole(RoleEnum.ADMIN.getName())
                        .requestMatchers("/api/student/user/register").permitAll()
                        .requestMatchers("/api/student/**").hasRole(RoleEnum.VIP.getName())
                        .requestMatchers(ignores).permitAll()
                        .requestMatchers("/api/csrf", "/api/user/login", "/api/wx/**",
                                "/api/movie/**", "/api/predict/**", "/api/recommend/**",
                                "/", "/admin", "/admin/**", "/assets/**", "/css/**",
                                "/js/**", "/images/**", "/static/**", "/error", "/favicon.ico").permitAll()
                        .anyRequest().authenticated())
                .formLogin(form -> form
                        .successHandler(restAuthenticationSuccessHandler)
                        .failureHandler(restAuthenticationFailureHandler))
                .logout(logout -> logout
                        .logoutUrl("/api/user/logout")
                        .logoutSuccessHandler(restLogoutSuccessHandler)
                        .invalidateHttpSession(true))
                .rememberMe(remember -> remember
                        .key(StringUtils.hasText(rememberMeKey) ? rememberMeKey : UUID.randomUUID().toString())
                        .tokenValiditySeconds(CookieConfig.getInterval())
                        .userDetailsService(formDetailsService));

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource(
            @Value("${app.cors.allowed-origins:}") String allowedOrigins) {
        final CorsConfiguration configuration = new CorsConfiguration();
        configuration.setMaxAge(3600L);
        configuration.setAllowedOrigins(Arrays.stream(allowedOrigins.split(","))
                .map(String::trim).filter(origin -> !origin.isEmpty()).toList());
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"));
        configuration.setAllowCredentials(true);
        configuration.setAllowedHeaders(List.of("Content-Type", "X-XSRF-TOKEN", "request-ajax",
                "Authorization", "X-Requested-With"));
        final UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        return source;
    }

}
