package com.analyzer.service;

import com.analyzer.config.EnvConfig;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class LlmServiceTest {

    @Mock
    private EnvConfig envConfig;

    @InjectMocks
    private LlmService llmService;

    @Test
    void cleanJson_RemovesCodeBlocks() {
        String input = "```json\n{\"summary\": \"test\"}\n```";
        String result = llmService.cleanJson(input);
        assertEquals("{\"summary\": \"test\"}", result);
    }

    @Test
    void cleanJson_RemovesThinkTags() {
        String input = "<think>some reasoning</think>{\"summary\": \"test\"}";
        String result = llmService.cleanJson(input);
        assertEquals("{\"summary\": \"test\"}", result);
    }

    @Test
    void cleanJson_ExtractsBracedContent() {
        String input = "Here is the JSON: {\"type\": \"bug\"} end";
        String result = llmService.cleanJson(input);
        assertEquals("{\"type\": \"bug\"}", result);
    }

    @Test
    void cleanJson_PlainJson() {
        String input = "{\"summary\": \"test\", \"type\": \"bug\"}";
        String result = llmService.cleanJson(input);
        assertEquals("{\"summary\": \"test\", \"type\": \"bug\"}", result);
    }

    @Test
    void cleanJson_NestedThinkAndCodeBlocks() {
        String input = "<think>reasoning here\nmore reasoning</think>\n```json\n{\"summary\": \"clean\"}\n```";
        String result = llmService.cleanJson(input);
        assertEquals("{\"summary\": \"clean\"}", result);
    }
}
