package com.alvis.media.viewmodel.admin.user;

import com.alvis.media.domain.UserTag;
import lombok.Data;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

@Data
public class UserCreateVM {

    private Integer id;

    @NotBlank
    private String userName;

    private String password;

    @NotBlank
    private String realName;

    private String age;

    private Integer status;

    private Integer sex;

    private String birthDay;

    private String phone;

    private Integer role;

    private String city;

    private String job;

    private List <UserTag> userTagList;
}
