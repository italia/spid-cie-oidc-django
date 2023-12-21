# Security Policy

A responsible security disclosure is a practice in the field of cybersecurity where a vulnerability found in software or a system is disclosed only to the software's vendor or a trusted entity capable of fixing the issue, rather than being publicly disclosed or sold.

The process typically involves the following steps:

1. Discovery: A security researcher discovers a vulnerability.
2. Reporting: The vulnerability is reported to the software vendor or a trusted third-party, often via a dedicated security contact.
3. Verification & Fixing: The vendor verifies the vulnerability and develops a patch or workaround.
4. Release: The patch is released to users, often alongside a security advisory detailing the issue without revealing exploitable details.
5. Public Disclosure: After a reasonable period of time, the vulnerability is publicly disclosed, allowing the community to understand the issue and verify that the patch resolves it.

This practice is intended to prevent potential exploitation of the vulnerability by malicious actors, giving the vendor time to address the issue before it becomes widely known.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest   | :white_check_mark: |

## Reporting a Vulnerability

Anyone can submit a potential security vulnerability to `demarcog83@gmail.com`.
The author will verify the issue and contact you on how this will be
handled.


## Public Discussions

When a new vulnerability is reported and verified, a new security advisory is created on
GitHub and the issue is assigned a CVE identifier. Progress on the mitigation is tracked
on a private fork, where the incident-response team and developers communicate to fix
the issue.

When the fix is ready, a release plan is prepared and all communication channels are
used to notify the community of the presence of a new issue and the expected release
plan. This allows the community time to prepare for a security upgrade. (Notice that
security fixes are not backported at the moment.)

When the advisory is published, GitHub automatically notifies all associated projects of
the published advisory. Projects that use IdPy projects as dependencies should
automatically get Pull Requests by dependabot. Additionally, all communication channels
are used again, to notify the community of the release of a new version of the affected
software that contains the relevant fixes that mitigate the reported issue.


## Supported versions

Notice, that security fixes are not backported at the moment to older releases than the
latest. The team does not have the capacity to guarantee that these backports will exist.
You are advised to be prepared to upgrade to the latest version once the fix is out.
