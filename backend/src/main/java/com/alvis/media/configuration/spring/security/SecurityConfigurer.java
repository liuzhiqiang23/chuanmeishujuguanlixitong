package com.alvis.media.configuration.spring.security;

import com.alvis.media.configuration.property.CookieConfig;
import com.alvis.media.configuration.property.SystemConfig;
import com.alvis.media.domain.enums.RoleEnum;
import lombok.AllArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.HeadersConfigurer;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Collections;
import java.util.List;


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
                                                   RestLoginAuthenticationFilter authenticationFilter) throws Exception {
        http.headers(headers -> headers.frameOptions(HeadersConfigurer.FrameOptionsConfig::disable));

        List<String> securityIgnoreUrls = systemConfig.getSecurityIgnoreUrls();
        String[] ignores = securityIgnoreUrls.toArray(new String[0]);

        http
                .csrf(csrf -> csrf.disable())
                .cors(Customizer.withDefaults())
                .authenticationManager(authenticationManager)
                .addFilterAt(authenticationFilter, UsernamePasswordAuthenticationFilter.class)
                .exceptionHandling(ex -> ex
                        .authenticationEntryPoint(restAuthenticationEntryPoint)
                        .accessDeniedHandler(restAccessDeniedHandler))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(ignores).permitAll()
                        .requestMatchers("/api/admin/**").hasRole(RoleEnum.ADMIN.getName())
                        .requestMatchers("/video/**").hasRole(RoleEnum.ADMIN.getName())
                        .requestMatchers("/api/student/**").hasRole(RoleEnum.VIP.getName())
                        .anyRequest().permitAll())
                .formLogin(form -> form
                        .successHandler(restAuthenticationSuccessHandler)
                        .failureHandler(restAuthenticationFailureHandler))
                .logout(logout -> logout
                        .logoutUrl("/api/user/logout")
                        .logoutSuccessHandler(restLogoutSuccessHandler)
                        .invalidateHttpSession(true))
                .rememberMe(remember -> remember
                        .key(CookieConfig.getName())
                        .tokenValiditySeconds(CookieConfig.getInterval())
                        .userDetailsService(formDetailsService));

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        final CorsConfiguration configuration = new CorsConfiguration();
        configuration.setMaxAge(3600L);
        configuration.setAllowedOriginPatterns(Collections.singletonList("*"));
        configuration.setAllowedMethods(Collections.singletonList("*"));
        configuration.setAllowCredentials(true);
        configuration.setAllowedHeaders(Collections.singletonList("*"));
        final UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        return source;
    }

}
