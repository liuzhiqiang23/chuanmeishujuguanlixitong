package com.alvis.media.event;

import com.alvis.media.domain.User;
import org.springframework.context.ApplicationEvent;

/**
 *@author 奇趣
 */
public class OnRegistrationCompleteEvent extends ApplicationEvent {


    private final User user;


    public OnRegistrationCompleteEvent(final User user) {
        super(user);
        this.user = user;
    }

    public User getUser() {
        return user;
    }

}