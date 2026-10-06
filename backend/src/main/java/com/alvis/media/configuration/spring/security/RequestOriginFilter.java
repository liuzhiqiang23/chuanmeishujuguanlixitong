package com.alvis.media.configuration.spring.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.net.URI;
import java.util.Arrays;
import java.util.Locale;
import java.util.Set;
import java.util.stream.Collectors;

/** Reject browser state-changing requests from origins outside the configured allowlist. */
public class RequestOriginFilter extends OncePerRequestFilter {

    private final Set<String> allowedOrigins;

    public RequestOriginFilter(String allowedOrigins) {
        this.allowedOrigins = Arrays.stream(allowedOrigins.split(","))
                .map(String::trim)
                .map(RequestOriginFilter::normalizeOrigin)
                .filter(origin -> !origin.isEmpty())
                .collect(Collectors.toUnmodifiableSet());
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String method = request.getMethod();
        if ("GET".equalsIgnoreCase(method) || "HEAD".equalsIgnoreCase(method)
                || "OPTIONS".equalsIgnoreCase(method) || "TRACE".equalsIgnoreCase(method)
                || request.getRequestURI().startsWith("/api/wx/")) {
            filterChain.doFilter(request, response);
            return;
        }

        String source = request.getHeader("Origin");
        if (source == null || source.isBlank()) {
            source = request.getHeader("Referer");
        }
        String normalizedSource = normalizeOrigin(source);
        String requestHost = request.getServerName();
        if (requestHost != null && requestHost.contains(":" ) && !requestHost.startsWith("[")) {
            requestHost = "[" + requestHost + "]";
        }
        String requestOrigin = normalizeOrigin(request.getScheme() + "://" + requestHost
                + portSuffix(request.getScheme(), request.getServerPort()));

        if (normalizedSource.isEmpty()
                || (!normalizedSource.equals(requestOrigin) && !allowedOrigins.contains(normalizedSource))) {
            response.sendError(HttpServletResponse.SC_FORBIDDEN, "Untrusted request origin");
            return;
        }
        filterChain.doFilter(request, response);
    }

    private static String portSuffix(String scheme, int port) {
        boolean defaultPort = ("http".equalsIgnoreCase(scheme) && port == 80)
                || ("https".equalsIgnoreCase(scheme) && port == 443);
        return defaultPort ? "" : ":" + port;
    }

    private static String normalizeOrigin(String value) {
        if (value == null || value.isBlank()) {
            return "";
        }
        try {
            URI uri = URI.create(value.trim());
            String scheme = uri.getScheme();
            String host = uri.getHost();
            if (scheme == null || host == null
                    || !("http".equalsIgnoreCase(scheme) || "https".equalsIgnoreCase(scheme))
                    || uri.getUserInfo() != null) {
                return "";
            }
            int port = uri.getPort();
            boolean defaultPort = ("http".equalsIgnoreCase(scheme) && port == 80)
                    || ("https".equalsIgnoreCase(scheme) && port == 443);
            return scheme.toLowerCase(Locale.ROOT) + "://" + host.toLowerCase(Locale.ROOT)
                    + (port < 0 || defaultPort ? "" : ":" + port);
        } catch (IllegalArgumentException ignored) {
            return "";
        }
    }
}
