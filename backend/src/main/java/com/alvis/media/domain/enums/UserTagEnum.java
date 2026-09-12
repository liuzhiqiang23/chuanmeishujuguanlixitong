package com.alvis.media.domain.enums;


import java.util.HashMap;
import java.util.Map;

public enum UserTagEnum {
    SELF(1, "self"),
    ANALYSIS(2, "analysis");

    int code;
    String name;

    UserTagEnum(int code, String name) {
        this.code = code;
        this.name = name;
    }

    private static final Map<Integer, UserTagEnum> keyMap = new HashMap<>();

    static {
        for (UserTagEnum item : UserTagEnum.values()) {
            keyMap.put(item.getCode(), item);
        }
    }

    public static UserTagEnum fromCode(Integer code) {
        return keyMap.get(code);
    }

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getRoleName() {
        return "ROLE_" + name;
    }

}
