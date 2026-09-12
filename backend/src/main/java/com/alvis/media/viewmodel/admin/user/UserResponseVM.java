package com.alvis.media.viewmodel.admin.user;

import com.alvis.media.domain.*;
import com.alvis.media.utility.DateTimeUtil;
import com.alvis.media.viewmodel.BaseVM;
import lombok.Data;

import java.util.List;

/**
 *@author 奇趣
 */

@Data
public class UserResponseVM extends BaseVM {

    private Integer id;

    private String userUuid;

    private String userName;

    private String realName;

    private Integer age;

    private Integer role;

    private Integer sex;

    private String birthDay;

    private String phone;

    private String lastActiveTime;

    private String createTime;

    private String modifyTime;

    private Integer status;
    private String imagePath;

    private List <VideoPlay> userPlayList;

    private List <MessageUser> userRecommendList;

    private List <UserVideoOperation> userOperationList;

    private List <UserTag> userTagList;


    private String city;

    private String job;


    public static UserResponseVM from(User user) {
        UserResponseVM vm = modelMapper.map(user, UserResponseVM.class);
        vm.setBirthDay(DateTimeUtil.dateFormat(user.getBirthDay()));
        vm.setLastActiveTime(DateTimeUtil.dateFormat(user.getLastActiveTime()));
        vm.setCreateTime(DateTimeUtil.dateFormat(user.getCreateTime()));
        vm.setModifyTime(DateTimeUtil.dateFormat(user.getModifyTime()));
        return vm;
    }
}
