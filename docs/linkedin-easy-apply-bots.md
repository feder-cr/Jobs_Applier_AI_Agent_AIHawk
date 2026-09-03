---
title: "LinkedIn Easy Apply bots: the landscape, read honestly"
description: "The real GitHub bots, the extension class and the SaaS class - what each actually does, what breaks first, the lineage that leads back to this project, and the User Agreement reality none of them change."
parent: "Job Application Automation"
nav_order: 6
---


# LinkedIn Easy Apply bots: the landscape, read honestly

Easy Apply is LinkedIn's short-form application flow: instead of bouncing to
an employer's own site, you answer a few structured questions inside LinkedIn
and submit. That structure is exactly what makes it automatable - a bounded
form, predictable fields, one platform's markup instead of every employer's -
and so it became the target of an entire class of bots. This page reads that
class honestly: the real tools, what they actually do, what breaks, and the
two facts that frame all of it.

The facts first, because they apply to every tool named below equally.
LinkedIn's User Agreement, section 8.2, prohibits members from using
"software, devices, scripts, robots or any other means or processes" to
scrape the Services, and from using "bots or other unauthorized automated
methods to access the Services." Its help center adds that members using such
tools "risk having their accounts restricted or shut down," and that the
tools themselves "may become non-operational without notice." Every bot in
this landscape operates against that baseline, whatever its README says, and
the account the risk lands on is yours.

## The GitHub bots, factually

These are the real, findable, open-source tools a searcher encounters. All
three were checked on 2026-09-03; descriptions are theirs, not ours.

**[nicolomantini/LinkedIn-Easy-Apply-Bot](https://github.com/nicolomantini/LinkedIn-Easy-Apply-Bot)**
(about 1,100 stars) describes itself simply: "Automate the application
process on LinkedIn." You configure positions, locations and constraints in a
YAML file, supply credentials, and the bot applies to matching Easy Apply
postings. The author's companion write-up is titled "How to apply for 1,000
jobs while sleeping," which tells you the design goal in one line: volume,
unattended.

**[GodsScion/Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn)**
(about 2,800 stars) pitches "Make your job hunt easy by automating your
application process with this Auto Applier." It is the maximal version of the
class: it searches for relevant postings, answers application questions,
tailors resumes per job with the OpenAI API, and its README claims it can
apply to more than 100 jobs in an hour. It is built on Selenium, and its
repository topics include undetected-chromedriver - worth noticing, because a
tool that needs a detection-evading driver is telling you the platform is
looking for it.

**[jomacs/linkedIn_auto_jobs_applier_with_AI](https://github.com/jomacs/linkedIn_auto_jobs_applier_with_AI)**
(about 54 stars) matters less for its size than for what it is: a fork of
this repository, frozen under the project's old name. Its description still
reads "LinkedIn_AIHawk is a tool that automates the jobs application process
on LinkedIn. Utilizing artificial intelligence, it enables users to apply for
multiple job offers in an automated and personalized way" - which is a
faithful description of what this project was in 2024.

## The lineage, stated plainly

That last repo is the visible end of a real lineage. AIHawk began life as the
LinkedIn_AIHawk jobs applier - an AI-powered bulk application bot for
LinkedIn, the one 404 Media ran to 17 applications in an hour and TechCrunch
and The Verge covered in October 2024. Forks taken in that era keep the name
and README the project carried then, so a searcher who finds
"linkedIn_auto_jobs_applier_with_AI" or "LinkedIn_AIHawk" today is finding
descendants of this project's old code. They are legitimate forks - the code
was open source and forking it is exactly what the license allowed - and
nothing here is a criticism of the people maintaining them. The original,
meanwhile, retired the bulk applier and became AIHawk, a general web agent;
that whole arc is told in
[the open-source job application bot, and what it became](open-source-job-application-bot.md).

The practical consequence for a reader comparing tools: the forks continue
the 2024 design - unattended LinkedIn volume - while the original now takes
the opposite position, supervised work with a human reading every submission.
Same ancestor, opposite answers to the volume question.

## The extension class

Chrome extensions occupy the low-friction end: they run inside your existing
logged-in session and auto-fill or auto-advance Easy Apply forms as you
browse, sometimes with an AI layer drafting the free-text answers. No
separate driver, no credential handoff, which makes them feel safer than they
are: LinkedIn's prohibited-software page names "browser plug-ins, or browser
extensions that scrape, modify the appearance of, or automate activity" on
the site explicitly, and an extension operates in the one place LinkedIn's
own JavaScript can see. The convenience is real; the policy exposure is
identical to the scripts'.

## The SaaS class

Paid services sit at the other end: you hand over your profile, preferences
and often your credentials or an active session, and the service applies for
you - some driving cloud browsers, some using human operators, most
advertising volume per week as the headline feature. Two things distinguish
this class, neither favorable. The activity still lands on your account, so
the User Agreement exposure is unchanged. And you have added a third party
holding your login and acting in your name at their pace, not yours - an
arrangement you cannot audit from outside.

## What breaks, in the order it breaks

**Selectors drift.** Every scripted bot is welded to LinkedIn's markup, and
the markup changes - ordinary redesign or otherwise. When it changes, the bot
mis-clicks, skips required fields, or silently submits garbage until its
maintainer catches up. An open-source bot's issue tracker is the honest
changelog of this arms race.

**Multi-step forms filter the class.** Easy Apply's short path is automatable;
the longer variants - conditional questions, file uploads, free-text answers
that get read by a human - are where scripted bots either stop or answer
badly. The AI-augmented bots push further into this territory by generating
answers, which replaces "blank field" failures with "confidently wrong
field" failures, at volume.

**Account flags end the run.** The failure mode that matters most is not
technical. Application velocity is visible to the platform in a way no
selector fix addresses, and LinkedIn's stated response to prohibited tools is
restriction of the account - covered mechanically in
[how LinkedIn detects bots](linkedin-bot-detection.md). Every bot in this
landscape shares this exposure completely, whatever driver it ships.

## The honest read

Read as a landscape, the Easy Apply bot class is a machine for converting a
real frustration - application forms are repetitive and screening is already
automated on the employer side - into a specific bad trade: volume you
cannot review, sent from an account you cannot afford to lose, against terms
that prohibit it. This project made that trade at scale in 2024, got the
star count and the headlines, and concluded the criticism was right; the
[head page of this cluster](automating-linkedin-job-applications.md) carries
that history and the quality-over-volume position it produced. If what you
actually want is AI help with a job search rather than a volume machine,
that is a different shape of tool entirely -
[an AI agent for your LinkedIn job search](ai-agent-linkedin-job-search.md)
describes it.

## Short answers to the questions that lead here

**What is the best LinkedIn Easy Apply bot?** The premise buys the wrong
contest. The bots differ in polish, but they share markup fragility and,
completely, the account risk - LinkedIn prohibits the whole class. The
differences that matter are in what you are risking, not which bot clicks
faster.

**Are Easy Apply bots against LinkedIn's terms?** Yes. Section 8.2 of the
User Agreement prohibits scripts, robots and unauthorized automated access,
and the help center names bots, plug-ins and extensions, with account
restriction as the stated consequence.

**Do the GitHub bots still work?** They work between markup changes and
account flags. Their issue trackers document both failure modes better than
any review could.

**Is AIHawk one of these bots?** It was - it began as LinkedIn_AIHawk, the
bulk applier the 2024 press covered, and forks of that code still circulate
under the old name. The current project is a general agent with a
human-review rule, which is the opposite design.

**Are the forks scams?** No claim of that here. They are legitimate forks of
open-source code, maintained by their own authors, continuing the original
design. The reservations on this page are about that design - unattended
volume against prohibiting terms - not about the people running the forks.

**What breaks these bots most often?** Selector drift first, multi-step and
free-text forms second, account restriction third - and the third is the one
no update fixes.

## Sources

All retrieved 2026-09-03.

- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement),
  section 8.2, for the quoted prohibitions.
- [LinkedIn Help: Prohibited software and extensions](https://www.linkedin.com/help/linkedin/answer/a1341387),
  for the extension-class prohibition, "restricted or shut down," and tools
  becoming "non-operational without notice."
- [nicolomantini/LinkedIn-Easy-Apply-Bot](https://github.com/nicolomantini/LinkedIn-Easy-Apply-Bot),
  [GodsScion/Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn),
  and
  [jomacs/linkedIn_auto_jobs_applier_with_AI](https://github.com/jomacs/linkedIn_auto_jobs_applier_with_AI),
  for each tool's own description, star count, and stated capabilities.
- [404 Media, "I Applied to 2,843 Roles: The Rise of AI-Powered Job
  Application Bots"](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
  Jason Koebler, October 10 2024, for the first-hand account of the original
  AIHawk bot.
- The [AIHawk README](https://github.com/feder-cr/AIHawk#readme), for the
  project's current shape and the human-review rule.

**See also:** [automating LinkedIn job applications: what exists and what it
costs you](automating-linkedin-job-applications.md) for the full landscape
this page zooms into, [how LinkedIn detects
bots](linkedin-bot-detection.md) for the enforcement layer, [an AI agent for
your LinkedIn job search](ai-agent-linkedin-job-search.md) for the
supervised alternative, and [the open-source job application bot, and what
it became](open-source-job-application-bot.md) for the lineage from the
inside.

---

*Written by the maintainer of [AIHawk](https://github.com/feder-cr/AIHawk),
the project several of these bots descend from. Nobody gets to describe this
landscape from higher ground; this page settles for describing it
accurately.*
