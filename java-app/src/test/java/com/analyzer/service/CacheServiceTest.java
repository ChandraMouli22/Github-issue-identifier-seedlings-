package com.analyzer.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Path;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class CacheServiceTest {

    private final CacheService cacheService = new CacheService();

    @Test
    void generateCacheKey_Consistent() {
        String key1 = cacheService.generateCacheKey("https://github.com/test/repo", 1, "gemini-2.0-flash");
        String key2 = cacheService.generateCacheKey("https://github.com/test/repo", 1, "gemini-2.0-flash");
        assertEquals(key1, key2);
    }

    @Test
    void generateCacheKey_DifferentForDifferentInputs() {
        String key1 = cacheService.generateCacheKey("https://github.com/test/repo", 1, "gemini-2.0-flash");
        String key2 = cacheService.generateCacheKey("https://github.com/test/repo", 2, "gemini-2.0-flash");
        assertNotEquals(key1, key2);
    }

    @Test
    void generateCacheKey_DifferentForDifferentModels() {
        String key1 = cacheService.generateCacheKey("https://github.com/test/repo", 1, "gemini-2.0-flash");
        String key2 = cacheService.generateCacheKey("https://github.com/test/repo", 1, "deepseek");
        assertNotEquals(key1, key2);
    }

    @Test
    void getCachedAnalysis_ReturnNullOnMiss() {
        Map<String, Object> result = cacheService.getCachedAnalysis(
                "https://github.com/nonexistent/repo", 99999, "test-model");
        assertNull(result);
    }

    @Test
    void saveAndRetrieveCache() {
        String repoUrl = "https://github.com/test/cache-test";
        int issueNumber = 42;
        String model = "test-model";

        Map<String, Object> analysis = Map.of(
                "summary", "Test summary",
                "type", "bug"
        );

        cacheService.saveToCache(repoUrl, issueNumber, model, analysis);
        Map<String, Object> cached = cacheService.getCachedAnalysis(repoUrl, issueNumber, model);

        assertNotNull(cached);
        assertEquals("Test summary", cached.get("summary"));
        assertEquals("bug", cached.get("type"));
    }
}
