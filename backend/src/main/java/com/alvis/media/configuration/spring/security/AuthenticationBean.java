package com.alvis.media.configuration.spring.security;

import lombok.Data;

/**
 *@author 奇趣
 */

@Data
public class AuthenticationBean {
    private String userName;
    private String password;
    private boolean remember;
}
