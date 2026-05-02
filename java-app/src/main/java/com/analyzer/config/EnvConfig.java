package com.analyzer.config;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.stereotype.Component;

/**
 * Loads environment variables from .env file (like python-dotenv).
 * Falls back to system environment variables automatically.
 */
@Component
public class EnvConfig {

    private final Dotenv dotenv;

    public EnvConfig() {
        this.dotenv = Dotenv.configure()
                .ignoreIfMissing()
                .load();
    }

    public String get(String key) {
        return dotenv.get(key, "");
    }

    public String get(String key, String defaultValue) {
        return dotenv.get(key, defaultValue);
    }
}
