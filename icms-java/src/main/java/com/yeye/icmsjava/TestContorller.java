package com.yeye.icmsjava;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono; // 引入 Mono

@RestController
@RequestMapping("/test")
public class TestContorller {
    private final WebClient webClient;

    public TestContorller(WebClient.Builder webClientBuilder) {
        // 构建 WebClient 实例，用于调用 FastAPI
        // 确保 FastAPI 运行在 8000 端口
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    // Spring Boot 内部调用 FastAPI 的 GET 接口（修改为发送纯字符串）
    @GetMapping("/reverse")
    public Mono<String> reverseStringFromFastAPI() {
        String strToReverse = "abc"; // 你要反转的字符串

        System.out.println("Spring Boot GET endpoint received request. Reversing: " + strToReverse);

        // 2. 使用 WebClient 调用 FastAPI 的 POST 接口
        //    直接发送字符串作为请求体，并指定 Content-Type 为 text/plain
        return webClient.post()
                .uri("/reverse") // FastAPI 的反转接口路径
                .contentType(MediaType.TEXT_PLAIN) // <--- 关键：发送纯文本
                .bodyValue(strToReverse) // <--- 关键：直接发送字符串
                .retrieve() // 执行请求并获取响应
                .bodyToMono(String.class) // <--- 关键：接收纯文本响应
                .map(fastAPIResponse -> {
                    // 3. 处理 FastAPI 返回的结果，并直接返回给 Vue
                    System.out.println("Spring Boot sending back to Vue (raw string): " + fastAPIResponse);
                    return fastAPIResponse; // 直接返回反转后的字符串
                })
                .doOnError(e -> {
                    System.err.println("Error calling FastAPI from /api/processString: " + e.getMessage());
                    // 实际项目中可以返回 Mono.error(new CustomException(...)) 或者提供默认值
                });
    }

//    @GetMapping("/reverse")
//    public String reverse() {
//        String str="abc";
//
//        return str;
//    }
}
