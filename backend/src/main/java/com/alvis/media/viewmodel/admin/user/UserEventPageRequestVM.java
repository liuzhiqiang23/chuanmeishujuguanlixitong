package com.alvis.media.viewmodel.admin.user;

import com.alvis.media.base.BasePage;
import lombok.Data;

/**
 *@author 奇趣
 */

@Data
public class UserEventPageRequestVM extends BasePage {

    private Integer userId;

    private String userName;

}
