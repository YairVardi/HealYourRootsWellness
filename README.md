# HealYourRootsWellness Automation Framework

Java Maven automation framework for `https://healyourrootswellness.com`, organized according to the `FullStackFinalProject` blueprint.

The project is branded in Jenkins and Allure as a Java Selenium automation framework for `HealYourRootsWellness`. It uses TestNG, Page Object Model classes, reusable extensions, XML-backed runtime configuration, and Allure reporting.

Implementation note: the existing browser layer still contains Playwright Java APIs from the previous framework. Selenium and WebDriverManager are already configured in Maven, but a full runtime migration from Playwright Java to Selenium WebDriver is a separate code change.

## Tech Stack

- Java 17
- Maven
- TestNG
- Selenium WebDriver and WebDriverManager
- Playwright Java legacy browser layer pending migration
- Rest Assured
- Appium Java Client
- AShot
- Allure TestNG

## Project Structure

```text
.
|-- Configuration/
|   `-- DataConfig.xml
|-- Drivers/
|-- ImageRepository/
|-- src/
|   |-- main/java/
|   |   |-- Extensions/
|   |   |-- Helpers/
|   |   |-- PageObjects/
|   |   |-- Utilities/
|   |   `-- WorkFlows/
|   `-- test/java/
|       |-- Helpers/
|       |-- SanityTest/
|       `-- Utilities/
|-- allure-results/
|-- Jenkinsfile
|-- pom.xml
`-- testng.xml
```

## Configuration

Runtime defaults live in `Configuration/DataConfig.xml`.

Important keys:

- `PlatformName`: defaults to `WEB`
- `BrowserName`: `chrome` or `firefox` for Jenkins Java Selenium runs. The legacy browser layer still normalizes `chrome` to `chromium` internally.
- `Headless`: `true` or `false`
- `url`: web base URL
- `url_api`: API base URL
- `DefaultTimeoutMs` and `ExpectTimeoutMs`: UI automation timeouts
- `UDID`, `AppPackage`, `AppActivity`: mobile placeholders
- `ElectronDriverPath`, `ElectronAppPath`: Electron placeholders
- `CalculatorAPP`, `WindowsServer`: desktop placeholders

Java system properties override XML values. Common examples:

```bash
./mvnw test -DBrowserName=firefox -DHeadless=true -Durl=https://healyourrootswellness.com
./mvnw test -Dbase.url=https://example.com -Dbrowser=chrome
```

Environment variables `BASE_URL`, `BROWSER`, `HEADLESS`, `API_URL`, and `PLATFORM_NAME` are also supported by the current framework utilities.

## Setup

Install Java 17+. The Maven wrapper is included, so a local Maven installation is optional.

Selenium WebDriver binaries are handled by WebDriverManager when the Selenium browser layer is used. Until the remaining Playwright Java code is migrated, the legacy browser runtime still needs Playwright browsers installed:

```bash
./mvnw exec:java -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install"
```

For Linux CI agents that need browser system dependencies:

```bash
./mvnw exec:java -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install --with-deps"
```

## Run Commands

Compile tests without executing them:

```bash
./mvnw -DskipTests test
```

Run the full sanity suite:

```bash
./mvnw test
```

Run one TestNG class:

```bash
./mvnw -Dtest=SanityTest.ClientFlowTest test
./mvnw -Dtest=SanityTest.NavigationTest test
```

Run headed:

```bash
./mvnw test -DHeadless=false
```

Run with an alternate config file:

```bash
./mvnw test -Dconfig.file=Configuration/DataConfig.xml
```

## Main Test Suites

- `SanityTest.ClientFlowTest`: patient/client journey and mocked consultation flow
- `SanityTest.TherapistFlowTest`: clinician journey and dashboard access checks
- `SanityTest.NavigationTest`: route, header, footer, and HTTP status coverage
- `SanityTest.FormsValidationTest`: consultation validation and duplicate-submit checks
- `SanityTest.ResponsiveTest`: mobile/tablet responsive coverage
- `SanityTest.SecurityBasicTest`: basic HTTPS, payload, and login-error checks

## Reporting

Surefire XML reports are written to:

```text
target/surefire-reports/
```

Allure raw results are written to:

```text
allure-results/
```

Generate a local Allure HTML report:

```bash
./mvnw allure:report
```

## Jenkins

The root `Jenkinsfile` provides a parameterized Java Selenium pipeline for local or SCM-based execution. It maps Jenkins parameters into the same keys used by `DataConfig.xml`, publishes JUnit-compatible Surefire results, writes Allure environment metadata, and archives `allure-results`.

Recommended defaults for this project:

- `TEST_SUITE=` to run all sanity tests
- `PLATFORM_NAME=WEB`
- `BROWSER_NAME=chrome`
- `HEADLESS=true`
- `BASE_URL=https://healyourrootswellness.com`

Set `TEST_SUITE=SanityTest.ClientFlowTest` to run one class.

## Notes

- `Drivers/` is intentionally empty; place local machine-specific binaries there only when needed.
- `ImageRepository/` is reserved for visual baselines.
- `WorkFlows/` is reserved for future reusable business-level flows as the suite grows.
- Known production issues are kept explicit in `Helpers.KnownProductionIssues`.
