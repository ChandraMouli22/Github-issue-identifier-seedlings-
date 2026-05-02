package com.analyzer.model;

/**
 * DTO for available AI model information.
 * Equivalent to the AVAILABLE_MODELS list entries in Python.
 */
public class ModelInfo {
    private String id;
    private String name;
    private String description;
    private String speed;
    private boolean recommended;
    private String provider;

    public ModelInfo(String id, String name, String description, String speed, boolean recommended, String provider) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.speed = speed;
        this.recommended = recommended;
        this.provider = provider;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getSpeed() { return speed; }
    public boolean isRecommended() { return recommended; }
    public String getProvider() { return provider; }
}
