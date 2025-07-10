package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Olá do container: " + System.getenv("HOSTNAME");
    }

    @GetMapping("/cpu")
    public void cpuStress() {
        long t = System.currentTimeMillis() + 10000;
        while (System.currentTimeMillis() < t) Math.atan(Math.random());
    }
}