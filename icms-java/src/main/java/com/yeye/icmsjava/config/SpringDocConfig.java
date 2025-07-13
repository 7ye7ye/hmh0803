package com.yeye.icmsjava.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

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

    @Bean // 标记这个方法会产生一个 Spring Bean
    public RestTemplate restTemplate() {
        // 在这里可以对 RestTemplate 进行各种自定义配置，例如设置超时、拦截器等
        RestTemplate restTemplate = new RestTemplate();
        // 示例：设置连接和读取超时 (实际项目中通常会设置)
        // restTemplate.setRequestFactory(new SimpleClientHttpRequestFactory() {{
        //     setConnectTimeout(5000); // 5秒连接超时
        //     setReadTimeout(5000);    // 5秒读取超时
        // }});
        return restTemplate;
    }
}
