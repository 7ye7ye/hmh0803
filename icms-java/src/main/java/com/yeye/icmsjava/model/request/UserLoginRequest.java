package com.yeye.icmsjava.model.request;

import lombok.Getter;

import java.io.Serial;
import java.io.Serializable;

@Getter
public class UserLoginRequest implements Serializable {
    @Serial
    private static final long serialVersionUID = 2L;

    private String username;
    private String password;

    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }
}
