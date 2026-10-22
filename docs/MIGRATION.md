# Java to Python Coverage Map

All TestNG methods present in the local working tree were mapped before the Java framework was removed. Parameterized Python node ids make the original Java loops visible as separate cases.

| Java/TestNG test | Python/pytest equivalent |
|---|---|
| `ClientFlowTest.homepageLoadsAndExposesPatientFacingEntryPoints` | `tests/ui/test_client_flow.py::test_homepage_loads_and_exposes_patient_facing_entry_points` |
| `ClientFlowTest.clientJourneyRoutesStayInsidePublicPatientFacingPages` | `test_client_journey_routes_stay_inside_public_patient_facing_pages[...]` |
| `ClientFlowTest.faqRouteShouldRenderFaqContentInsteadOfGlobalErrorBoundary` | `test_faq_route_should_render_faq_content_instead_of_global_error_boundary` |
| `ClientFlowTest.contactPageBookNowCtaLeadsIntoConsultationFlow` | `test_contact_page_book_now_cta_leads_into_consultation_flow` |
| `ClientFlowTest.clientCtaDoesNotRedirectIntoTherapistOnlyAreasUnderRapidClicks` | `test_client_cta_does_not_redirect_into_therapist_only_areas_under_rapid_clicks` |
| `ClientFlowTest.consultationHappyPathCompletesSafelyWithMockedProductionApis` | `test_consultation_happy_path_completes_safely_with_mocked_production_apis` |
| `TherapistFlowTest.therapistCtaExistsAndRedirectsToClinicianLandingPage` | `tests/ui/test_therapist_flow.py::test_therapist_cta_exists_and_redirects_to_clinician_landing_page` |
| `TherapistFlowTest.therapistRoutesStayOutOfClientBookingFlow` | `test_therapist_routes_stay_out_of_client_booking_flow[...]` |
| `TherapistFlowTest.unauthenticatedUsersCannotAccessMemberDashboardDirectly` | `test_unauthenticated_users_cannot_access_member_dashboard_directly` |
| `TherapistFlowTest.loginErrorsAvoidExposingRawTransportDetailsInUi` | `test_login_errors_avoid_exposing_raw_transport_details_in_ui` |
| `NavigationTest.homepageRendersHeaderFooterLogoAndMainNavigationLinks` | `tests/ui/test_navigation.py::test_homepage_renders_header_footer_logo_and_main_navigation_links` |
| `NavigationTest.headerLinksAndLogoNavigateCorrectly` | `test_header_links_and_logo_navigate_correctly` |
| `NavigationTest.browserBackForwardAndRefreshPreserveRouteStability` | `test_browser_back_forward_and_refresh_preserve_route_stability` |
| `NavigationTest.importantPublicRoutesDoNotReturnHttp404Responses` | `test_important_public_routes_do_not_return_http_404_responses[...]` |
| `NavigationTest.footerSupportLinksLoadRealContentPages` | `test_footer_support_links_load_real_content_pages[...]` |
| `NavigationTest.footerSitemapLinkShouldNotLandOn404Page` | `test_footer_sitemap_link_should_not_land_on_404_page` |
| `FormsValidationTest.emptyPersonalInformationKeepsConsultationFlowBlocked` | `tests/ui/test_forms_validation.py::test_empty_personal_information_keeps_consultation_flow_blocked` |
| `FormsValidationTest.invalidEmailFormatsShouldBeBlockedBeforeTherapistMatching` | `test_invalid_email_formats_should_be_blocked_before_therapist_matching[...]` |
| `FormsValidationTest.unicodeSpacesAndSpecialCharactersCanBeEnteredWithoutCrashingTheFlow` | `test_unicode_spaces_and_special_characters_can_be_entered_without_crashing_flow` |
| `FormsValidationTest.copyPasteStyleEntryAndLongInputSurviveOnPersonalInfoStep` | `test_copy_paste_style_entry_and_long_input_survive_on_personal_info_step` |
| `FormsValidationTest.multipleRapidSubmitClicksDoNotCreateDuplicateConsultationRequests` | `test_multiple_rapid_submit_clicks_do_not_create_duplicate_consultation_requests` |
| `FormsValidationTest.consultationFlowStaysUsableWhenAvailabilityCallsAreSlow` | `test_consultation_flow_stays_usable_when_availability_calls_are_slow` |
| `ResponsiveTest.mobileHamburgerMenuOpensAndClosesWithClientAndTherapistLinks` | `tests/ui/test_responsive.py::test_mobile_hamburger_menu_opens_and_closes_with_client_and_therapist_links` |
| `ResponsiveTest.mobileCtasStayTappableAndHeroLayoutAvoidsOverlap` | `test_mobile_ctas_stay_tappable_and_hero_layout_avoids_overlap` |
| `ResponsiveTest.tabletPortraitAndLandscapeViewportsKeepConsultationEntryUsable` | `test_tablet_viewports_keep_consultation_entry_usable[portrait/landscape]` |
| `SecurityBasicTest.homeConsultationAndLoginPagesStayOnHttps` | `tests/ui/test_security.py::test_home_consultation_and_login_pages_stay_on_https` |
| `SecurityBasicTest.scriptSqlHtmlAndSpecialCharacterPayloadsStayInertInConsultationInputs` | `test_script_sql_html_and_special_character_payloads_stay_inert_in_inputs` |
| `SecurityBasicTest.noSensitiveConsultationPayloadIsEchoedToConsoleDuringDataEntry` | `test_no_sensitive_consultation_payload_is_echoed_to_console_during_entry` |
| `SecurityBasicTest.loginFailuresDoNotExposeRawStatusCodesOrJsonPayloadsInUi` | `test_login_failures_do_not_expose_raw_status_codes_or_json_payloads` |
| `SeleniumUiTest.homepageHeaderLinksRenderAndFindTherapistNavigationWorksWithSelenium` | Navigation header tests and client homepage smoke test |
| `SeleniumUiTest.contactBookNowCtaOpensConsultationFlowWithSelenium` | `test_contact_page_book_now_cta_leads_into_consultation_flow` |
| `SeleniumUiTest.consultationNextButtonRequiresServiceTypeSelectionWithSelenium` | `test_consultation_next_requires_service_type_and_previous_preserves_selection` |
| `SeleniumUiTest.consultationPreviousButtonPreservesSelectedServiceTypeWithSelenium` | `test_consultation_next_requires_service_type_and_previous_preserves_selection` |
| `SeleniumUiTest.loginPageRendersMemberSignInOptionsWithSelenium` | `tests/ui/test_security.py::test_login_page_renders_member_sign_in_options` |
| `MemberRegistrationApiTest.createMemberAccountReturnsSuccessAndCreatedIdentityWhenAvailable` | `tests/api/test_member_registration.py::test_create_member_account_returns_success_and_created_identity_when_available` |
| `MemberRegistrationApiTest.createMemberAccountRejectsMissingRequiredFields` | `test_create_member_account_rejects_missing_required_fields` |
| `MemberRegistrationApiTest.createMemberAccountRejectsInvalidEmail` | `test_create_member_account_rejects_invalid_email` |
| `MemberRegistrationApiTest.createMemberAccountRejectsDuplicateEmail` | `test_create_member_account_rejects_duplicate_email` |
| `MemberRegistrationApiTest.createMemberAccountRejectsEmptyBody` | `test_create_member_account_rejects_empty_body` |
| `MemberAccountVerificationApiTest.createdMemberAccountAppearsInTeamAccounts` | `tests/api/test_member_account_verification.py::test_created_member_account_appears_in_team_accounts` |
| `MemberAccountVerificationApiTest.teamAccountsRejectsUnauthenticatedRequests` | `test_team_accounts_rejects_unauthenticated_requests` |
| `MemberDeleteAccountInvestigationTest.confirmedDeleteOrDeactivateCandidateSucceeds` | `tests/api/test_member_delete_account_investigation.py::test_confirmed_delete_or_deactivate_candidate_succeeds` |

## Expected Failures

These remain executable `pytest.mark.xfail(strict=True)` checks. A product fix becomes an XPASS failure until the wrapper is intentionally removed.

- raw login 401/JSON exposure (two coverage paths)
- invalid email formats enabling Next (four parameter cases)
- duplicate consultation submission on Chromium rapid-clicks
- homepage schedule-a-consult entry point removed in the current production UI
- contact Book Now consultation entry point replaced by clinician browsing
- the production `/consultation` route now states that HYRW no longer performs intake, matching, or scheduling; all preserved wizard validation, mock submission, responsive and input-security assertions remain strict xfails behind this blocking contract

## Retired Selectors

The Selenium-specific CSS/XPath layer was not carried forward: fixed `header a[href=...]` selectors, broad union XPath radio fallbacks, and lower-cased XPath text expressions were tied to the removed Selenium implementation. Browser validation also confirmed the old homepage heading (`A Therapist Directory & Mental Health Community`) was stale; `HomePage` now targets the current heading (`A therapist directory and community, built by clinicians`). The header's former direct `Find a Therapist` link is now an accessible menu button whose `All providers` menu item opens the directory. The retired `/locations` page is no longer linked; location coverage uses the current Pennsylvania directory route and asserts its state-specific heading. Python Page Objects use Playwright role, label, placeholder and scoped locator APIs. The placeholder-based login inputs remain because that is the current accessible surface; they are isolated in `LoginPage` for a single future change.

## Safety

- Consultation POSTs are fulfilled by local Playwright routes and their payloads are asserted in memory.
- Member creation needs `RUN_MUTATING_API_TESTS=true` plus a password and generates `example.com`-style synthetic identities by default.
- Delete/deactivate coverage remains skipped unless all destructive guards are supplied.
- Jira tests use fakes and fixture XML only; they never contact Jira.
