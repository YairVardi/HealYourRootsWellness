package Helpers;

import java.util.List;

public final class InvalidInputs {
    public static final List<String> INVALID_EMAILS = List.of("abc", "abc@", "abc@.com", "abc@gmail");

    public static final List<String> MALICIOUS_PAYLOADS = List.of(
            "<script>alert(1)</script>",
            "' OR 1=1 --",
            "<b>bold</b>",
            "<img src=x onerror=alert(1)>"
    );

    public static final String SPECIAL_CHARACTERS = "QA !@#$%^&*()_+-=[]{};:'\\\",.<>/?`~";
    public static final String UNICODE_HEBREW_TEXT =
            "\u05e9\u05dc\u05d5\u05dd \u05d1\u05d3\u05d9\u05e7\u05ea \u05d0\u05d5\u05d8\u05d5\u05de\u05e6\u05d9\u05d4";
    public static final String LEADING_TRAILING_SPACES = "  Yael  ";
    public static final String LONG_INPUT = "long-input-".repeat(25);

    private InvalidInputs() {
    }
}
