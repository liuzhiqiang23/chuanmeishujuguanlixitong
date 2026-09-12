package com.alvis.media.viewmodel.admin.user;

import com.alvis.media.base.BasePage;
import lombok.Data;

/**
 *@author 奇趣
 */

@Data
public class UserPageRequestVM extends BasePage {

    private String userName;
    private Integer role;

}
