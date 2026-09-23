package com.alvis.media.context;

import com.alvis.media.domain.User;
import com.alvis.media.service.UserService;
import lombok.AllArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.RequestContextHolder;

@Component
@AllArgsConstructor
public class WebContext {
    private static final String USER_ATTRIBUTES = "USER_ATTRIBUTES";
    private final UserService userService;


    public void setCurrentUser(User user) {
        RequestContextHolder.currentRequestAttributes().setAttribute(USER_ATTRIBUTES, user, RequestAttributes.SCOPE_REQUEST);
    }

    public User getCurrentUser() {
        User user = (User) RequestContextHolder.currentRequestAttributes().getAttribute(USER_ATTRIBUTES, RequestAttributes.SCOPE_REQUEST);
        if (null != user) {
            return user;
        }
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        Object principal = null == authentication ? null : authentication.getPrincipal();
        if (null == principal) {
            return null;
        }
        String userName;
        if (principal instanceof UserDetails) {
            userName = ((UserDetails) principal).getUsername();
        } else if (principal instanceof String) {
            // 管理端登录后的 principal 是用户名字符串（旧写法直接强转 UserDetails 会 ClassCastException，
            // 匿名请求则是 "anonymousUser"，查不到用户自然返回 null）
            userName = (String) principal;
        } else {
            return null;
        }
        user = userService.getUserByUserName(userName);
        if (null != user) {
            setCurrentUser(user);
        }
        return user;
    }
}
