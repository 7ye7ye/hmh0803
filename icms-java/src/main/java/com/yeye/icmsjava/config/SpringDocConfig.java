package com.yeye.icmsjava.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SpringDocConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("ICMS-Java 项目 API 文档")
                        .description("这是 ICMS-Java 项目的接口文档，描述项目相关功能接口")
                        .version("1.0.0"));
    }
}