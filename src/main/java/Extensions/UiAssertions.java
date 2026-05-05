package Extensions;

import Utilities.TestEnvironment;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.BoundingBox;
import com.microsoft.playwright.options.LoadState;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.fail;

public final class UiAssertions {
    private UiAssertions() {
    }

    public static Pattern regex(String expression) {
        return Pattern.compile(expression, Pattern.CASE_INSENSITIVE);
    }

    public static String escapeRegex(String value) {
        return Pattern.quote(value);
    }

    public static String normalizeWhitespace(String value) {
        return value == null ? "" : value.replaceAll("\\s+", " ").trim();
    }

    public static void waitForAppReady(Page page) {
        page.waitForLoadState(LoadState.DOMCONTENTLOADED);
        page.waitForTimeout(750);
    }

    public static void assertPageHealthy(Page page) {
        PlaywrightAssertions.assertThat(page.getByText(TestEnvironment.ERROR_BOUNDARY_TEXT)).hasCount(0);

        Locator primaryHeading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setLevel(1)
        ).first();
        if (primaryHeading.count() > 0) {
            PlaywrightAssertions.assertThat(primaryHeading).not().hasText(TestEnvironment.NOT_FOUND_HEADING);
        }
    }

    public static void assertUrlMatches(Page page, Pattern urlPattern) {
        assertThat(urlPattern.matcher(page.url()).find())
                .as("Expected URL <%s> to match <%s>", page.url(), urlPattern)
                .isTrue();
    }

    public static void assertHttps(Page page) {
        assertThat(page.url()).startsWith("https://");
    }

    public static void assertNoHorizontalOverflow(Page page) {
        Boolean hasNoOverflow = (Boolean) page.evaluate("""
                () => document.documentElement.scrollWidth <= window.innerWidth + 1
                  && document.body.scrollWidth <= window.innerWidth + 1
                """);
        assertThat(hasNoOverflow)
                .as("The page has unexpected horizontal overflow.")
                .isTrue();
    }

    public static void assertElementsDoNotOverlap(Locator first, Locator second) {
        BoundingBox firstBox = first.boundingBox();
        BoundingBox secondBox = second.boundingBox();

        assertThat(firstBox).isNotNull();
        assertThat(secondBox).isNotNull();

        boolean overlaps = !(
                firstBox.x + firstBox.width <= secondBox.x
                        || secondBox.x + secondBox.width <= firstBox.x
                        || firstBox.y + firstBox.height <= secondBox.y
                        || secondBox.y + secondBox.height <= firstBox.y
        );

        assertThat(overlaps)
                .as("The checked elements overlap in the viewport.")
                .isFalse();
    }

    public static List<String> attachDialogCollector(Page page) {
        List<String> messages = new ArrayList<>();
        page.onDialog(dialog -> {
            messages.add(dialog.message());
            dialog.dismiss();
        });
        return messages;
    }

    public static List<String> attachConsoleCollector(Page page) {
        List<String> messages = new ArrayList<>();
        page.onConsoleMessage(message -> messages.add(normalizeWhitespace(message.text())));
        return messages;
    }

    public static void assertNoDialog(List<String> dialogMessages) {
        assertThat(dialogMessages)
                .as("Unexpected browser dialogs were triggered.")
                .isEmpty();
    }

    public static void assertNoSensitiveConsoleLeak(List<String> consoleMessages, List<String> payloads) {
        List<String> normalizedMessages = consoleMessages.stream()
                .map(String::toLowerCase)
                .collect(Collectors.toList());

        for (String payload : payloads) {
            String normalizedPayload = payload.toLowerCase();
            assertThat(normalizedMessages.stream().anyMatch(entry -> entry.contains(normalizedPayload)))
                    .as("Console logs leaked sensitive payload: %s", payload)
                    .isFalse();
        }
    }

    public static void insertTextWithKeyboard(Page page, Locator locator, String value) {
        locator.click();
        locator.fill("");
        page.keyboard().insertText(value);
    }

    public static void expectKnownIssue(String issue, ThrowingRunnable runnable) {
        try {
            runnable.run();
        } catch (AssertionError expectedFailure) {
            return;
        } catch (Exception exception) {
            throw new RuntimeException(exception);
        }

        fail("Known production issue appears fixed; remove the expected-failure wrapper: " + issue);
    }
}
