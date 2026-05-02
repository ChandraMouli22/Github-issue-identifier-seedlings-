package com.analyzer.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;

/**
 * File-based JSON cache service.
 * Equivalent to services/cache_service.py — same MD5 hash keys, same cache/ directory.
 */
@Service
public class CacheService {

    private static final Path CACHE_DIR = Paths.get("cache");
    private final ObjectMapper objectMapper;

    public CacheService() {
        this.objectMapper = new ObjectMapper();
        ensureCacheDir();
    }

    private void ensureCacheDir() {
        try {
            Files.createDirectories(CACHE_DIR);
        } catch (IOException e) {
            System.out.println("Could not create cache directory: " + e.getMessage());
        }
    }

    /**
     * Generate a unique cache key based on repo URL, issue number, and model.
     * Uses MD5 hash — same algorithm as the Python version.
     */
    public String generateCacheKey(String repoUrl, int issueNumber, String model) {
        String rawKey = repoUrl + "#" + issueNumber + "#" + model;
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(rawKey.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
    }

    /**
     * Retrieve cached analysis result if it exists.
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getCachedAnalysis(String repoUrl, int issueNumber, String model) {
        ensureCacheDir();
        String cacheKey = generateCacheKey(repoUrl, issueNumber, model);
        Path cacheFile = CACHE_DIR.resolve(cacheKey + ".json");

        if (Files.exists(cacheFile)) {
            try {
                String content = Files.readString(cacheFile);
                Map<String, Object> cached = objectMapper.readValue(content, Map.class);
                System.out.printf("✓ Cache HIT for %s #%d (model: %s)%n", repoUrl, issueNumber, model);
                return cached;
            } catch (Exception e) {
                System.out.println("Cache read error: " + e.getMessage());
                return null;
            }
        }

        System.out.printf("✗ Cache MISS for %s #%d (model: %s)%n", repoUrl, issueNumber, model);
        return null;
    }

    /**
     * Save analysis result to cache.
     */
    public void saveToCache(String repoUrl, int issueNumber, String model, Object analysis) {
        ensureCacheDir();
        String cacheKey = generateCacheKey(repoUrl, issueNumber, model);
        Path cacheFile = CACHE_DIR.resolve(cacheKey + ".json");

        try {
            String json = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(analysis);
            Files.writeString(cacheFile, json);
            System.out.printf("✓ Cached analysis for %s #%d (model: %s)%n", repoUrl, issueNumber, model);
        } catch (Exception e) {
            System.out.println("Cache write error: " + e.getMessage());
        }
    }

    /**
     * Clear all cached analysis results.
     */
    public void clearCache() {
        ensureCacheDir();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(CACHE_DIR, "*.json")) {
            for (Path file : stream) {
                try {
                    Files.delete(file);
                } catch (Exception e) {
                    System.out.println("Error deleting " + file + ": " + e.getMessage());
                }
            }
            System.out.println("✓ Cache cleared");
        } catch (IOException e) {
            System.out.println("Error clearing cache: " + e.getMessage());
        }
    }
}
