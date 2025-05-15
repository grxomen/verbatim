Privacy Policy

Last updated: [May 14th, 2025]

1. Introduction
Verbatim ("we", "us", "our") is a Discord bot that provides server management, moderation, and user verification via Stripe Identity. This Privacy Policy describes how we collect, use, and disclose personal information when you interact with Verbatim.

2. Information We Collect

Discord User Data: User ID, username, discriminator, avatar, roles, and locale, obtained via Discord’s API to enable commands (e.g., /userinfo, /verify).

Verification Data: When you complete the ID verification flow, Stripe sends us minimal metadata (Discord user ID) and a verification status. We do not store raw ID images.

Logs & Audit Data: Audit entries (e.g., bans, mutes, role assignments) are recorded in a private Discord channel for moderation transparency.

Technical Data: Bot logs, API request records, error traces — used for debugging and uptime monitoring.

3. How We Use Your Information

Role Assignment & Verification: Grant or remove Discord roles based on verification status.

Moderation Actions: Log and communicate moderation events as configured by server administrators.

Service Improvement: Analyze logs and usage patterns to fix bugs, optimize performance, and add features.

Compliance & Security: Retain minimal data needed for audit, compliance with Stripe Identity rules, and troubleshooting.

4. Data Retention & Security

Retention Period: We auto-delete any temporary verification metadata and logs older than 90 days.

Security Measures: Communications with Stripe and Discord use TLS. We never store secret keys in plain text — they reside in environment variables.

Access Controls: Only the bot process and designated server administrators can view audit logs.

5. Third-Party Services

Stripe Identity: Handles document capture and liveness checks. We only store the session status and metadata.

Discord: We use Discord’s API under their Developer Terms. No data is shared beyond Discord and Stripe.

6. Your Rights

Request Access or Deletion: To view or delete any personal data we hold, contact us at [VoxForge].

Modify Consent: You may disable DMs to the bot, but this may prevent verification and role assignment.

7. Changes to This PolicyWe may update this policy occasionally. We will post a new version here and update the "Last updated" date.