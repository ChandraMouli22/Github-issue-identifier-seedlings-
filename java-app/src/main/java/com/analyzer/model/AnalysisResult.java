package com.analyzer.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * Response DTO for issue analysis results.
 * Maps to the JSON schema returned by the LLM.
 */
public class AnalysisResult {
    private String summary;
    private String type;

    @JsonProperty("priority_score")
    private String priorityScore;

    @JsonProperty("suggested_labels")
    private List<String> suggestedLabels;

    @JsonProperty("potential_impact")
    private String potentialImpact;

    public AnalysisResult() {}

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getPriorityScore() { return priorityScore; }
    public void setPriorityScore(String priorityScore) { this.priorityScore = priorityScore; }

    public List<String> getSuggestedLabels() { return suggestedLabels; }
    public void setSuggestedLabels(List<String> suggestedLabels) { this.suggestedLabels = suggestedLabels; }

    public String getPotentialImpact() { return potentialImpact; }
    public void setPotentialImpact(String potentialImpact) { this.potentialImpact = potentialImpact; }
}
