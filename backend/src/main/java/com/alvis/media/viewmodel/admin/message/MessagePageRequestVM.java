package com.alvis.media.viewmodel.admin.message;

import com.alvis.media.base.BasePage;
import lombok.Data;

@Data
public class MessagePageRequestVM extends BasePage {
    private String sendUserName;
}
